from django.contrib import admin
from .models import Stock, UserStock

# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


@admin.register(UserStock)
class UserStockAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'quantity', 'invested_amount']
