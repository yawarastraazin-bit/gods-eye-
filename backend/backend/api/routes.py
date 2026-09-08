from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory storage (consider using database for persistence)
memory = []
journal = []


class JournalEntry(BaseModel):
    """Schema for journal entries"""
    entry: str


class MemoryNote(BaseModel):
    """Schema for memory notes"""
    note: str


@router.get("/status")
def status():
    """Get the current status of God's Eye"""
    return {
        "app": "God's Eye",
        "status": "active"
    }


@router.get("/chat")
def chat(message: str):
    """Chat endpoint with contextual responses"""
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


@router.post("/journal")
def add_journal(entry: str):
    """Add a new journal entry"""
    journal.append(entry)
    return {
        "saved": entry
    }


@router.get("/journal")
def get_journal():
    """Retrieve all journal entries"""
    return {
        "entries": journal
    }


@router.post("/remember")
def remember(note: str):
    """Add a new memory note"""
    memory.append(note)
    return {
        "saved": note,
        "total_memories": len(memory)
    }


@router.get("/memories")
def get_memories():
    """Retrieve all memory notes"""
    return {
        "memories": memory
    }


@router.delete("/memories")
def clear_memories():
    """Clear all memory notes"""
    memory.clear()
    return {
        "message": "All memories deleted"
    }
