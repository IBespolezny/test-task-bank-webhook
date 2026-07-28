import uvicorn
from fastapi import FastAPI

from app.api.system import system_router
from app.api.webhook import payment_router

from app.config import settings

app = FastAPI(title="Subscription Payment Webhook")

app.include_router(payment_router)
app.include_router(system_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)