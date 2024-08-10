from django.contrib import admin
from django.urls.resolvers import URLPattern
from .models import Stock, UserStock, StockDataAudit
from django.urls import path
from .utils import StockDataGenerator
from django.contrib import messages
from django.shortcuts import redirect
# Import for type hinting HTTP requests and responses
from django.http import HttpRequest, HttpResponse

# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Admin class for managing Stock model in Django admin interface.
    """
    list_display: list[str] = [
        'name', 'price']  # Display 'name' and 'price' fields in the admin list view

    # Custom template for the stock admin change list view
    change_list_template: str = 'stock/custom_stock_admin.html'

    def get_urls(self) -> list[URLPattern]:
        """
        Override the default `get_urls` method to add custom URLs to the admin interface.

        Returns:
            list[URLPattern]: A list of URL patterns for the admin interface.
        """
        urls: list[URLPattern] = super().get_urls(
        )  # Get the default URLs from the parent class
        custom_urls: list[URLPattern] = [
            path(
                'generate-random-stocks/',
                self.admin_site.admin_view(self.generate_random_stocks),
                name='generate_random_stocks'
            ),
            path(
                'generate-existing-stocks/',
                self.admin_site.admin_view(self.generate_existing_stocks),
                name='generate_existing_stocks'
            ),
        ]
        return custom_urls + urls  # Combine the default URLs with custom ones

    def generate_random_stocks(self, request: HttpRequest) -> HttpResponse:
        """
        Generate a CSV file with random stock data and save it to the media directory.
        Redirects the user back to the stock admin page with a success message.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Redirect response to the admin change list view.
        """
        generator: StockDataGenerator = StockDataGenerator(
        )  # Initialize the StockDataGenerator
        # Generate random stock data and get the file path
        file_path: str = generator.generate_random_stocks()
        messages.success(
            request, f"File generated and saved to /media ({file_path})"
        )  # Add a success message
        # Redirect to the parent directory (admin change list view)
        return redirect("..")

    def generate_existing_stocks(self, request: HttpRequest) -> HttpResponse:
        """
        Generate a CSV file using existing stock names and save it to the media directory.
        Redirects the user back to the stock admin page with a success message.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Redirect response to the admin change list view.
        """
        generator: StockDataGenerator = StockDataGenerator(
        )  # Initialize the StockDataGenerator
        file_path: str = generator.generate_random_stocks(
            use_existing_names=True)  # Generate stock data with existing names
        messages.success(
            request, f"File generated and saved to /media ({file_path})"
        )  # Add a success message
        # Redirect to the parent directory (admin change list view)
        return redirect("..")


@admin.register(UserStock)
class UserStockAdmin(admin.ModelAdmin):
    """
    Admin class for managing UserStock model in Django admin interface.
    """
    list_display: list[str] = ['user', 'stock', 'quantity',
                               'invested_amount']  # Display relevant fields in the admin list view


@admin.register(StockDataAudit)
class StockDataAuditAdmin(admin.ModelAdmin):
    """
    Admin class for managing StockDataAudit model in Django admin interface.
    """
    list_display: list[str] = [
        "file_name"]  # Display the 'file_name' field in the admin list view
