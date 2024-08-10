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
from typing import Optional, Dict, Any


class StockSerializer(ModelSerializer):
    """
    Serializer for the Stock model, including fields: name, price, created_at, and id.
    """
    class Meta:
        model = Stock
        fields = ["name", "price", "created_at", "id"]


class UserStockSerializer(ModelSerializer):
    """
    Serializer for the UserStock model, including related Stock details and latest_price.
    """
    stock = StockSerializer()
    latest_price = DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        model = UserStock
        fields = ["stock", "latest_price", "quantity", "id", "invested_amount"]


class StockDetailsSerializer(ModelSerializer):
    """
    Serializer for detailed Stock information, including price and created_at.
    """
    class Meta:
        model = Stock
        fields = ["price", "created_at"]


class ModifyUserStockSerializer(Serializer):
    """
    Serializer for modifying UserStock instances, including validation and saving logic.
    """
    quantity = IntegerField()
    name = CharField(max_length=10)

    def __init__(self, instance = None, data = ..., **kwargs: Any) -> None:
        """
        Initialize the serializer, setting the mode and fetching the latest stock price.

        :param instance: The instance to update (if any).
        :param data: The data to validate and use for the update.
        :param kwargs: Additional keyword arguments.
        """
        self.mode: Optional[str] = kwargs.pop("mode", None)
        if instance and instance.stock:
            self.latest_stock: Optional[Stock] = Stock.objects.filter(
                name=instance.stock.name
            ).order_by("-created_at").only("price").first()
        else:
            self.latest_stock = None
        super().__init__(instance, data, **kwargs)

    def validate_quantity(self, value: int) -> int:
        """
        Validate the quantity field.

        :param value: The quantity value to validate.
        :raises ValidationError: If the quantity is invalid.
        :return: The validated quantity.
        """
        if value <= 0:
            raise ValidationError(
                {"quantity": "Quantity cannot be less than 1."})
        if self.mode == "sell" and value > self.instance.quantity:
            raise ValidationError(
                {"quantity": "Cannot sell more than you own."})
        return value

    def save(self, **kwargs: Any) -> UserStock:
        """
        Save the UserStock instance with updated values based on the mode.

        :param kwargs: Additional keyword arguments.
        :return: The updated UserStock instance.
        """
        if self.latest_stock is None:
            raise ValidationError("Latest stock information is not available.")

        self.instance.stock = self.latest_stock
        quantity_to_update: int = int(self.validated_data["quantity"])

        if self.mode == "sell":
            average_stock_price: float = float(
                self.instance.invested_amount / self.instance.quantity)
            self.instance.quantity -= quantity_to_update
            if self.instance.quantity <= 0:
                self.instance.delete()
                return self.instance
            self.instance.invested_amount -= Decimal(
                average_stock_price * quantity_to_update)
        elif self.mode == "buy":
            self.instance.quantity += quantity_to_update
            self.instance.invested_amount += Decimal(
                self.latest_stock.price * quantity_to_update)

        self.instance.save()
        return self.instance
