from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {"status": "active"}

@router.get("/chat")
def chat(message: str):
    return {"response": "You said: " + message}
