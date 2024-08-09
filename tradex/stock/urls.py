from django.urls import path, re_path
from . import views

urlpatterns = [
    path("user-stocks/", views.get_user_stocks, name="get_user_stocks"),
    re_path(r'^user-stocks/(buy|sell)/$',
            views.modify_user_stock, name='modify_user_stock'),
    path("all/", views.get_stocks, name="get_stocks"),
    path("details/", views.get_stock_details, name="get_stock_details"),
]
