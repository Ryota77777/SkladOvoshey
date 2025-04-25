from django.urls import path, include
from . import views
from django.contrib import admin
from .views import profile, add_to_cart, view_cart, checkout, order_history, personal_cabinet_redirect
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('add_good/', views.add_good, name='add_good'),
    path('catalog/', views.catalog, name='catalog'),
    path('personal_cabinet/', personal_cabinet_redirect, name='personal_cabinet'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('load_goods/', views.load_goods_from_json, name='load_goods'),
    path('add_goods_api/', views.add_goods_api, name='add_goods_api'),
    path('delete_good/<int:id>/', views.delete_good, name='delete_good'),
    path('admin/', admin.site.urls),
    path("profile/", profile, name="profile"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cart/', view_cart, name='cart'),
    path('add_to_cart/<int:good_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order_history/', order_history, name='order_history'),
    path("update_cart/<int:good_id>/", views.update_cart, name="update_cart"),
]



