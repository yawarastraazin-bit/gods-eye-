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
journal = []
@router.post("/journal")
def add_journal(entry: str):
    journal.append(entry)
    return {
        "saved": entry
    }

@router.get("/journal")
def get_journal():
    return {
        "entries": journal
    }
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
