from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler


class AppException(Exception):
    """Базовое исключение"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "Внутренняя ошибка сервера"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class InsufficientStockError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INSUFFICIENT_STOCK"
    message = "Недостаточно товара на складе"
    
class InvalidQuantityError(AppException):
    status_code = 400
    error_code = "INVALID_QUANTITY"
    message = "Количество товара должно быть строго больше нуля"


class InsufficientBalanceError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INSUFFICIENT_BALANCE"
    message = "Недостаточно средств на балансе"


class EmptyCartError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "EMPTY_CART"
    message = "Корзина пуста"


class ItemNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message = "Запрашиваемый объект не найден"


class EmptyDepositError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INSUFFICIENT_DEPOSIT"
    message = "Недостаточная сумма для пополнения"


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """Глобальный обработчик исключений"""
    request: Request | None = context.get("request")
    path = request.path if request else "Unknown"

    if isinstance(exc, AppException):
        return Response(
            {
                "error_code": exc.error_code,
                "message": exc.message,
                "path": path,
            },
            status=exc.status_code,
        )

    response = exception_handler(exc, context)

    if response is not None:
        error_code = "VALIDATION_ERROR" if response.status_code == 400 else "API_ERROR"

        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            message = str(detail["detail"])
        elif isinstance(detail, list):
            message = "; ".join(str(item) for item in detail)
        else:
            message = str(detail)

        response.data = {
            "error_code": error_code,
            "message": message,
            "path": path,
        }

    return response
