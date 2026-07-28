from fastapi import APIRouter

system_router = APIRouter(tags=["system"])


@system_router.get("/health")
def health():
    return {"ok": True}