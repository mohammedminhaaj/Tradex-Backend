from rest_framework.request import Request
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import UserStock
from .serializer import UserStockSerializer, StockSerializer
from tradex.utils import response_structure
from rest_framework import status
from .models import Stock
from django.db.models import OuterRef, Subquery, DecimalField


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_stocks(request: Request):
    try:
        # Subquery to get the latest price for the stock name
        latest_stock_price = Stock.objects.filter(
            name=OuterRef('stock__name')
        ).order_by('-created_at').values('price')[:1]

        stocks = UserStock.objects.filter(user=request.user).annotate(
            latest_price=Subquery(
                latest_stock_price,
                output_field=DecimalField(max_digits=12, decimal_places=6)
            )
        ).select_related("stock").only("stock__name", "stock__price", "quantity", "id")
        serializer = UserStockSerializer(stocks, many=True)
        return response_structure("Success", status.HTTP_200_OK, serializer.data)
    except Exception:
        return response_structure("Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_stocks(request: Request):
    try:
        stocks = Stock.objects.all().order_by("-created_at").distinct().only(
            "name", "price", "created_at")
        serializer = StockSerializer(stocks, many=True)
        return response_structure("Success", status.HTTP_200_OK, serializer.data)
    except Exception:
        return response_structure("Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR)
