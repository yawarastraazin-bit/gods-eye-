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
        "reply": f"You said: {message}"
    }

memory = []
@router.post("/remember")
def remember(note: str):
    memory.append(note)
    return {
        "saved": note,
        "total_memories": len(memory)
    }

@router.get("/memories")
def get_memories():
    return {
        "memories": memory
    }

@router.delete("/memories")
def clear_memories():
    memory.clear()
    return {
        "message": "All memories deleted"
    }
