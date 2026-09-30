from decimal import Decimal
from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from orders.models import CartItem, Order
from orders.serializers import (
    CartAddSerializer,
    CartItemSerializer,
    CartListResponseSerializer,
    CartUpdateSerializer,
    OrderSerializer,
)
from orders.services import (
    cart_add_item,
    cart_remove_item,
    cart_update_item,
    order_create_from_cart,
)


class CartView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartListResponseSerializer

    @extend_schema(
        summary="Просмотр корзины",
        description="Возвращает все позиции корзины текущего пользователя и итоговую сумму",
        responses={status.HTTP_200_OK: CartListResponseSerializer},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        items = CartItem.objects.filter(user=request.user).select_related("product")
        total = sum(
            (item.product.price * item.quantity for item in items), Decimal("0.00")
        )

        serializer = self.get_serializer(
            instance={"items": items, "total_amount": total}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemAddView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartAddSerializer

    @extend_schema(
        summary="Добавить товар в корзину",
        description="Добавляет позицию в корзину или увеличивает количество существующей",
        responses={
            status.HTTP_201_CREATED: CartItemSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Неверный ID товара или количество меньше 0"
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = cart_add_item(
            user=request.user,
            product_id=serializer.validated_data["product_id"],
            quantity=serializer.validated_data["quantity"],
        )
        return Response(
            CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED
        )


class CartItemDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartUpdateSerializer

    @extend_schema(
        summary="Изменить количество товара",
        description="Устанавливает новое количество товара в позиции корзины",
        request=CartUpdateSerializer,
        responses={
            status.HTTP_200_OK: CartItemSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Некорректное количество"
            ),
        },
    )
    def patch(
        self, request: Request, product_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = cart_update_item(
            user=request.user,
            product_id=product_id,
            quantity=serializer.validated_data["quantity"],
        )
        return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удалить товар из корзины",
        description="Удаляет указанный товар из корзины покупателя",
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def delete(
        self, request: Request, product_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        cart_remove_item(user=request.user, product_id=product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCheckoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    @extend_schema(
        summary="Оформить заказ из корзины",
        description="Списывает средства с баланса, уменьшает остатки на складе и очищает корзину",
        request=None,
        responses={
            status.HTTP_201_CREATED: OrderSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Недостаточно средств, недостаточно товара на складе или пустая корзина"
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        order = order_create_from_cart(user_id=request.user.id)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    @extend_schema(
        summary="Список заказов пользователя",
        description="Возвращает историю заказов текущего пользователя",
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Order]:
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
