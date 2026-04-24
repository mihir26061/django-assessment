from django.urls import path
from orders.views import order_summary

urlpatterns = [
    path("api/orders/summary/", order_summary),
]