import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import GoodForm
from .models import Good
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Good, Order, OrderItem

# Настройка логирования
logger = logging.getLogger(__name__)

@login_required
def add_to_cart(request, good_id):
    good = get_object_or_404(Good, id=good_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, good=good)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    logger.info(f"Товар {good.name} добавлен в корзину пользователя {request.user.username}. Количество: {cart_item.quantity}")
    return JsonResponse({"success": True, "product_count": cart_item.quantity})

@login_required
def update_cart(request, good_id):
    good = get_object_or_404(Good, id=good_id)
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, good=good).first()

    if not cart_item:
        logger.warning(f"Товар {good.name} не найден в корзине пользователя {request.user.username}.")
        return JsonResponse({"success": False, "error": "Товар не найден в корзине."})

    change = int(request.GET.get("change", 0))
    cart_item.quantity += change

    if cart_item.quantity <= 0:
        cart_item.delete()
        logger.info(f"Товар {good.name} удален из корзины пользователя {request.user.username}.")
        return JsonResponse({"success": True, "product_count": 0})

    cart_item.save()
    logger.info(f"Количество товара {good.name} обновлено в корзине пользователя {request.user.username}. Новое количество: {cart_item.quantity}")
    return JsonResponse({"success": True, "product_count": cart_item.quantity})

@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.good.price * item.quantity for item in items)

    logger.info(f"Пользователь {request.user.username} просматривает свою корзину. Общее количество товаров: {len(items)}. Общая цена: {total_price}.")
    return render(request, 'cart.html', {'items': items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        messages.error(request, "Ваша корзина пуста!")
        logger.warning(f"Пользователь {request.user.username} пытался оформить заказ, но корзина пуста.")
        return redirect('catalog')

    total_price = sum(item.good.price * item.quantity for item in items)
    
    order = Order.objects.create(user=request.user, total_price=total_price)
    for item in items:
        OrderItem.objects.create(order=order, good=item.good, quantity=item.quantity)
    
    items.delete()
    messages.success(request, "Заказ успешно оформлен!")
    logger.info(f"Пользователь {request.user.username} оформил заказ. Общая сумма: {total_price}.")
    return redirect('order_history')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    logger.info(f"Пользователь {request.user.username} просматривает свою историю заказов. Количество заказов: {len(orders)}.")
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def profile(request):
    logger.info(f"Пользователь {request.user.username} зашел в свой профиль.")
    return render(request, "accounts/profile.html")

def home(request):
    goods = Good.objects.all()
    logger.info("Пользователь просматривает главную страницу.")
    return render(request, 'home.html', {'goods': goods})

def add_good(request):
    if request.method == 'POST':
        form = GoodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            logger.info("Новый товар был успешно добавлен.")
            return redirect('catalog')  
    else:
        form = GoodForm()

    return render(request, 'add_good.html', {'form': form})

def catalog(request):
    query = request.GET.get('q')  
    if query:
        goods = Good.objects.filter(name__icontains=query)  
    else:
        goods = Good.objects.all()
    logger.info(f"Пользователь ищет товары с запросом: {query if query else 'без запроса'}")
    return render(request, 'catalog.html', {'goods': goods})

def delete_good(request, id):
    good = get_object_or_404(Good, id=id)
    good.delete()  # Удаление товара
    logger.info(f"Товар {good.name} был удален.")
    return redirect('catalog')

def load_goods_from_json(request):
    # Открываем JSON файл с товарами
    with open('goods.json', 'r', encoding='utf-8') as file:
        goods_data = json.load(file)
        
    # Перебираем товары и добавляем их в базу данных
    for item in goods_data:
        Good.objects.create(
            name=item['name'],
            brand=item['brand'],
            description=item['description'],
            price=item['price'],
            dates=item['dates'],
            cover_image=item['cover_image']
        )
    
    logger.info("Товары успешно добавлены в базу данных из JSON.")
    return HttpResponse('Товары успешно добавлены в базу данных!')

@csrf_exempt
def add_goods_api(request):
    if request.method == 'POST':
        try:
            # Преобразуем тело запроса в JSON
            data = json.loads(request.body)
            
            # Проверка структуры данных
            if not isinstance(data, dict):  # Ожидаем, что data будет словарём
                logger.error("Ошибка формата JSON: ожидался словарь.")
                return JsonResponse({'status': 'error', 'message': 'Ожидался JSON-объект'}, status=400)
            
            # Работаем с данными
            good = Good.objects.create(
                name=data['name'],
                brand=data['brand'],
                description=data['description'],
                price=data['price'],
                dates=data['dates'],
                cover_image=data['cover_image']
            )
            logger.info(f"Товар {good.name} добавлен через API.")
            return JsonResponse({'status': 'success', 'message': 'Товар добавлен'})
        except json.JSONDecodeError:
            logger.error("Ошибка в формате JSON.")
            return JsonResponse({'status': 'error', 'message': 'Ошибка в формате JSON'}, status=400)
        except KeyError as e:
            logger.error(f"Отсутствует поле: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Отсутствует поле: {str(e)}'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)

def personal_cabinet_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile')  # перенаправление в личный кабинет
    return redirect('login')  # перенаправление на форму входа

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, "Вы успешно зарегистрированы!")
            logger.info(f"Пользователь {user.username} зарегистрировался.")
            return redirect('personal_cabinet')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте данные.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы вошли в систему!")
            logger.info(f"Пользователь {user.username} вошел в систему.")
            return redirect('personal_cabinet')
        else:
            messages.error(request, "Ошибка входа. Проверьте логин и пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    logger.info(f"Пользователь {request.user.username} вышел из системы.")
    return redirect('login')

def log_session(request):
    logger.info(f"Session ID: {request.session.session_key}")
    logger.info(f"Session Data: {request.session.items()}")




