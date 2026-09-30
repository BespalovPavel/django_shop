from django.urls import path

from orders.views import (
    CartItemAddView,
    CartItemDetailView,
    CartView,
    OrderCheckoutView,
    OrderListView,
)

app_name = "orders"

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart_view"),
    path("cart/items/", CartItemAddView.as_view(), name="cart_add"),
    path(
        "cart/items/<int:product_id>/",
        CartItemDetailView.as_view(),
        name="cart_item_detail",
    ),
    path("orders/checkout/", OrderCheckoutView.as_view(), name="order_checkout"),
    path("orders/", OrderListView.as_view(), name="order_list"),
]
