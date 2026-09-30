from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    BalanceTopUpSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
)
from users.services import user_deposit_balance


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        responses={status.HTTP_201_CREATED: UserProfileSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Получить профиль текущего пользователя")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    def get_object(self) -> User:
        return self.request.user


class BalanceTopUpView(generics.GenericAPIView):
    serializer_class = BalanceTopUpSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Пополнить личный баланс",
        description="Увеличивает баланс пользователя на указанную сумму",
        request=BalanceTopUpSerializer,
        responses={status.HTTP_200_OK: UserProfileSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_deposit_balance(
            user_id=request.user.id,
            amount=serializer.validated_data["amount"],
        )
        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
