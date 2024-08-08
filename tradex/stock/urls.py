from django.urls import path
from . import views

urlpatterns = [
    path("user-stocks/", views.get_user_stocks, name="get_user_stocks"),
    path("all/", views.get_stocks, name="get_stocks")
]
