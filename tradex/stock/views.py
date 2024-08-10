from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import OuterRef, Subquery, DecimalField
from django.core.paginator import Paginator
from typing import Dict, Optional

from .models import UserStock, Stock
from .serializer import UserStockSerializer, StockSerializer, StockDetailsSerializer, ModifyUserStockSerializer
from tradex.utils import response_structure, SERVER_ERROR_MESSAGE, SUCCESS_MESSAGE


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_stocks(request: Request) -> Response:
    """
    Retrieve the user's stock information, with optional pagination and search filtering.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object containing user stock data.
    """
    page = request.query_params.get("page", 1)
    limit = request.query_params.get("limit", 9999)
    search = request.query_params.get("search", None)

    search_term: Dict[str, str] = {
        "stock__name__icontains": search} if search else {}

    try:
        # Subquery to get the latest price for the stock name
        latest_stock_price = Stock.objects.filter(
            name=OuterRef('stock__name')
        ).order_by('-created_at').values('price')[:1]

        user_stocks = UserStock.objects.filter(user=request.user).annotate(
            latest_price=Subquery(
                latest_stock_price,
                output_field=DecimalField(max_digits=12, decimal_places=6)
            )
        ).select_related("stock").only(
            "stock__name",
            "stock__price",
            "quantity",
            "id",
            "invested_amount",
            "stock_id",
            "stock__created_at"
        ).filter(**search_term)

        serializer = UserStockSerializer(user_stocks, many=True)
        paginator = Paginator(serializer.data, int(limit))
        paginated_results = paginator.get_page(int(page)).object_list

        return response_structure(SUCCESS_MESSAGE, status.HTTP_200_OK, paginated_results, count=paginator.count)
    except Exception:
        return response_structure(SERVER_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_stocks(request: Request) -> Response:
    """
    Retrieve stock information with optional pagination and search filtering.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object containing stock data.
    """
    page = request.query_params.get("page", 1)
    limit = request.query_params.get("limit", 10)
    search = request.query_params.get("search", None)

    search_term: Dict[str, str] = {
        "name__icontains": search} if search else {}

    try:
        latest_stock = Stock.objects.filter(
            name=OuterRef('name')).order_by('-created_at').only("name", "id")
        stocks = Stock.objects.filter(id=Subquery(latest_stock.values('id')[:1])).only(
            'name', 'price', 'created_at', 'id').filter(**search_term)

        serializer = StockSerializer(stocks, many=True)
        paginator = Paginator(serializer.data, int(limit))
        paginated_results = paginator.get_page(int(page)).object_list

        return response_structure(SUCCESS_MESSAGE, status.HTTP_200_OK, paginated_results, count=paginator.count)
    except Exception:
        return response_structure(SERVER_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_stock_details(request: Request) -> Response:
    """
    Retrieve details for a specific stock by its name.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object containing stock details.
    """
    try:
        stock_name = request.query_params.get("name", None)
        if not stock_name:
            return response_structure("Invalid request", status.HTTP_400_BAD_REQUEST)

        stocks = Stock.objects.filter(
            name=stock_name).order_by("created_at").only("created_at", "price")
        serializer = StockDetailsSerializer(stocks, many=True)

        return response_structure(SUCCESS_MESSAGE, status.HTTP_200_OK, serializer.data)
    except Exception:
        return response_structure(SERVER_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def modify_user_stock(request: Request, mode: str) -> Response:
    """
    Modify the user's stock based on the action mode (buy/sell).

    Args:
        request (Request): The HTTP request object containing stock data.
        mode (str): The action mode ("buy" or "sell").

    Returns:
        Response: The HTTP response object indicating the result of the operation.
    """
    try:
        user_stock = UserStock.objects.filter(
            user=request.user, stock__name=request.data.get("name")).first()

        if not user_stock:
            if mode == "buy":
                user_stock = UserStock(user=request.user, stock=Stock(
                    name=request.data.get("name"), price=0.0))
            else:
                return response_structure("User Stock does not exist", status.HTTP_400_BAD_REQUEST)

        serializer = ModifyUserStockSerializer(
            user_stock, data=request.data, mode=mode)
        if serializer.is_valid():
            serializer.save()
            return response_structure(SUCCESS_MESSAGE, status.HTTP_200_OK)
        else:
            return response_structure("Failed to update stock", status.HTTP_400_BAD_REQUEST, serializer.errors)
    except Exception:
        return response_structure(SERVER_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)
