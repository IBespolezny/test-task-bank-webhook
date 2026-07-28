from fastapi import HTTPException
from psycopg2.extensions import connection as PGConnection
import time

from app.enums import PaymentStatusBank, PaymentStatusServer
from app.schemas import PaymentResponse, PaymentWebhook


class PaymentsService:
    """
    Бизнес-логика обработки платежей.
    """

    def __init__(self, conn: PGConnection):
        self._conn = conn

    def process_webhook(self, payload: PaymentWebhook) -> PaymentResponse:
        with self._conn.cursor() as cur:
            try:
                applied_status = self._upsert_payment(cur, payload)
            except Exception as e:
                self._conn.rollback()
                raise HTTPException(status_code=422, detail=f"Ошибка при обработке платежа: \n{e}")

            if applied_status is None:
                # CONFIRMED или тот же status + payment_id
                return PaymentResponse(status=PaymentStatusServer.ALREADY_PROCESSED, payment_id=payload.payment_id)

            if applied_status == PaymentStatusBank.CONFIRMED:
                time.sleep(5) # Имитация долгой работы
                self._activate_subscription(cur, payload.user_id)

        return PaymentResponse(status=PaymentStatusServer.PROCESSED, payment_id=payload.payment_id)


    @staticmethod
    def _upsert_payment(cur, payload: PaymentWebhook) -> str | None:
        """
        Метод позволяет обновлять уже отработанный ранее платёж, но только в сторону
        успешной оплаты. Сделать успешный платёж неуспешным и отнять подписку нельзя.
        """

        cur.execute(
            """
            INSERT INTO payments (payment_id, user_id, amount, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (payment_id) DO UPDATE SET
                status = EXCLUDED.status
            WHERE payments.status <> 'CONFIRMED'
              AND payments.status IS DISTINCT FROM EXCLUDED.status
            RETURNING status
            """,
            (payload.payment_id, payload.user_id, payload.amount, payload.status),
        )
        row = cur.fetchone()
        return row[0] if row else None


    @staticmethod
    def _activate_subscription(cur, user_id: int) -> None:
        """
        Метод активирует подписку двумя способами:
        1. Нет подписки -> +30 дней с now()
        2. Есть подписка -> =30 дней с конца подписки
        """
        cur.execute(
            """
            INSERT INTO subscriptions (user_id, status, expires_at)
            VALUES (%s, 'active', now() + interval '30 days')
            ON CONFLICT (user_id) DO UPDATE SET
                status = 'active',
                expires_at = GREATEST(subscriptions.expires_at, now())
                             + interval '30 days'
            """,
            (user_id,),
        )