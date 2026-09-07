from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {
        "app": "God's Eye",
        "status": "active"
    }
