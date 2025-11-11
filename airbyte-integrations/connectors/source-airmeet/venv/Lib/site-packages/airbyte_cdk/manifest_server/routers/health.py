from typing import Dict

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok"}
