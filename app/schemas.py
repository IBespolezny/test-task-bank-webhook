from pydantic import BaseModel, Field

from app.enums import PaymentStatusBank, PaymentStatusServer


class PaymentWebhook(BaseModel):
    payment_id: str = Field(..., min_length=1)
    user_id: int
    amount: int = Field(..., gt=0)
    status: PaymentStatusBank


class PaymentResponse(BaseModel):
    status: PaymentStatusServer
    payment_id: str = Field(..., min_length=1)
