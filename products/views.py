from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from products.models import Product
from products.permissions import IsAdminOrReadOnly
from products.serializers import ProductSerializer


@extend_schema_view(
    list=extend_schema(summary="Список товаров"),
    retrieve=extend_schema(summary="Детальная информация о товаре"),
    create=extend_schema(summary="Создать товар (только админ)"),
    update=extend_schema(summary="Обновить товар целиком (только админ)"),
    partial_update=extend_schema(summary="Частично обновить товар (только админ)"),
    destroy=extend_schema(summary="Удалить товар (только админ)"),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
