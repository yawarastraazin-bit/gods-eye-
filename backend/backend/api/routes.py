from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {
        "app": "God's Eye",
        "status": "active"
    }

@router.get("/chat")
def chat(message: str):
    return {
        "user": message,
        "response": f"You said: {message}"
    }
