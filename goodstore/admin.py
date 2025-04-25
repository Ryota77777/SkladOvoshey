from django.contrib import admin
from .models import Good

class GoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'dates')  # Поля, которые будут отображаться в списке товаров
    search_fields = ('name', 'brand')  # Поля для поиска
    list_filter = ('brand',)  # Фильтр по бренду

    # Настройка отображения формы в админке
    fieldsets = (
        (None, {
            'fields': ('name', 'brand', 'description', 'price', 'dates', 'cover_image')
        }),
    )

# Регистрация модели в админке
admin.site.register(Good, GoodAdmin)
