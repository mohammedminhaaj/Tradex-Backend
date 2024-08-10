from django.contrib import admin
from django.urls.resolvers import URLPattern
from .models import Stock, UserStock
from django.urls import path
from .utils import StockDataGenerator
from django.contrib import messages
from django.shortcuts import redirect

# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

    change_list_template = 'stock/custom_stock_admin.html'

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path('generate-random-stocks/', self.admin_site.admin_view(
                self.generate_random_stocks), name='generate_random_stocks'),
            path('generate-existing-stocks/', self.admin_site.admin_view(
                self.generate_existing_stocks), name='generate_existing_stocks'),
        ]
        return custom_urls + urls

    def generate_random_stocks(self, request):
        generator = StockDataGenerator()
        generator.generate_random_stocks()
        messages.success(request, "File created successfully")
        return redirect(request.META.get('HTTP_REFERER'))

    def generate_existing_stocks(self, request):
        generator = StockDataGenerator()
        generator.generate_random_stocks(use_existing_names=True)
        messages.success(request, "File created successfully")
        return redirect(request.META.get('HTTP_REFERER'))


@admin.register(UserStock)
class UserStockAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'quantity', 'invested_amount']
