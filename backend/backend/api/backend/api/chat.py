from fastapi import APIRouter

router = APIRouter()

@router.get("/chat")
def chat():
    return {
        "message": "God's Eye chat endpoint is working"
    }
