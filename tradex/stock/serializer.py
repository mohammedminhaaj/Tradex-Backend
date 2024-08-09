
from rest_framework.serializers import (
    ModelSerializer,
    DecimalField,
    Serializer,
    IntegerField,
    CharField,
    ValidationError
)
from .models import UserStock, Stock

from decimal import Decimal


class StockSerializer(ModelSerializer):
    class Meta:
        model = Stock
        fields = ["name", "price", "created_at", "id"]


class UserStockSerializer(ModelSerializer):
    stock = StockSerializer()
    latest_price = DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        model = UserStock
        fields = ["stock", "latest_price", "quantity", "id"]


class StockDetailsSerializer(ModelSerializer):

    class Meta:
        model = Stock
        fields = ["price", "created_at"]


class ModifyUserStockSerializer(Serializer):

    def __init__(self, instance=None, data=..., **kwargs):
        self.mode = kwargs.pop("mode", None)
        self.latest_stock = Stock.objects.filter(
            name=instance.stock.name).order_by("-created_at").only("price").first()
        super().__init__(instance, data, **kwargs)

    quantity = IntegerField()
    name = CharField(max_length=10)

    def validate_quantity(self, value):
        if self.mode == "sell" and value > self.instance.quantity:
            raise ValidationError(
                {"quantity": "Cannot sell more than you own."})
        return value

    def save(self, **kwargs):
        self.instance.stock = self.latest_stock
        quantity_to_update: int = int(self.validated_data["quantity"])
        if self.mode == "sell":
            average_stock_price: float = self.instance.invested_amount/self.instance.quantity
            self.instance.quantity -= quantity_to_update
            if self.instance.quantity <= 0:
                self.instance.delete()
                return self.instance
            self.instance.invested_amount -= average_stock_price * quantity_to_update
        elif self.mode == "buy":
            self.instance.quantity += quantity_to_update
            self.instance.invested_amount += Decimal(
                self.latest_stock.price * quantity_to_update)
        self.instance.save()
        return self.instance
