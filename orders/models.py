from decimal import Decimal

from django.conf import settings
from django.db import models

from products.models import Product


class OrderStatus(models.TextChoices):
    COMPLETED = "COMPLETED", "Выполнен"
    CANCELLED = "CANCELLED", "Отменен"


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="in_carts",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_cart"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orders_cartitem_quantity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.product.name} (кол-во - {self.quantity})"


class Order(models.Model):
    Status = OrderStatus

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Покупатель",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Итоговая стоимость",
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.COMPLETED,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=OrderStatus.values),
                name="orders_order_status_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=Decimal("0.00")),
                name="orders_order_total_amount_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"Заказ #{self.id} | {self.user.username} | {self.total_amount} руб."


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="ordered_in",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена при покупке",
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orders_orderitem_quantity_positive",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
