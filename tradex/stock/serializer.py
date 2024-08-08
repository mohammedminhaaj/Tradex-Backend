from rest_framework.serializers import ModelSerializer, DecimalField
from .models import UserStock, Stock


class StockSerializer(ModelSerializer):
    class Meta:
        model = Stock
        fields = ["name", "price", "created_at"]


class UserStockSerializer(ModelSerializer):
    stock = StockSerializer()
    latest_price = DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        model = UserStock
        fields = ["stock", "latest_price", "quantity", "id"]
