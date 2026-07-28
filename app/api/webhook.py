from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as PGConnection

from app.db import get_db
from app.schemas import PaymentWebhook

payment_router = APIRouter(prefix="/webhook", tags=["payments"])


@payment_router.post("/payment")
def handle_payment_webhook(
    payload: PaymentWebhook,
    conn: PGConnection = Depends(get_db),
):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO payments (payment_id, user_id, amount, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (payment_id) DO NOTHING
            RETURNING id
            """,
            (payload.payment_id, payload.user_id, payload.amount, payload.status),
        )
        inserted = cur.fetchone()

        if inserted is None:
            return {"status": "already_processed", "payment_id": payload.payment_id}

        if payload.status == "CONFIRMED":
            cur.execute(
                """
                INSERT INTO subscriptions (user_id, status, expires_at)
                VALUES (%s, 'active', now() + interval '30 days')
                ON CONFLICT (user_id) DO UPDATE SET
                    status = 'active',
                    expires_at = GREATEST(subscriptions.expires_at, now())
                                 + interval '30 days'
                """,
                (payload.user_id,),
            )

    return {"status": "processed", "payment_id": payload.payment_id}