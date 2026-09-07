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

@router.get("/chat")
def chat(message: str):
    text = message.lower()

    if "hello" in text:
        reply = "Hello. I am God's Eye."
    elif "who are you" in text:
        reply = "I am God's Eye, your personal assistant."
    elif "memory" in text:
        reply = f"I currently have {len(memory)} memories."
    else:
        reply = f"You said: {message}"

    return {
        "reply": reply
    }
