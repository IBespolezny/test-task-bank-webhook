from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as PGConnection

from app.db import get_db
from app.schemas import PaymentResponse, PaymentWebhook
from services.payments import PaymentsService

payment_router = APIRouter(prefix="/webhook", tags=["payments"])


@payment_router.post("/payment", response_model=PaymentResponse)
def handle_payment_webhook(
    payload: PaymentWebhook,
    conn: PGConnection = Depends(get_db),
):
    service = PaymentsService(conn)
    return service.process_webhook(payload)