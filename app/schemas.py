from typing import Literal

from pydantic import BaseModel, Field


class PaymentWebhook(BaseModel):
    payment_id: str = Field(..., min_length=1)
    user_id: int
    amount: int = Field(..., gt=0)
    # В реальности банк может слать и другие статусы (FAILED, PENDING…).
    # Явно перечисляем ожидаемые значения, чтобы опечатка в статусе
    # роняла запрос на этапе валидации, а не молча писалась в БД.
    status: Literal["CONFIRMED", "FAILED", "PENDING"]
