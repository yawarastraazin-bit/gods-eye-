"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============ Journal Schemas ============
class JournalEntryCreate(BaseModel):
    """Schema for creating journal entries"""
    title: str
    content: str
    mood: Optional[str] = None
    tags: Optional[str] = None


class JournalEntryResponse(BaseModel):
    """Schema for journal entry responses"""
    id: int
    title: str
    content: str
    mood: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Memory Schemas ============
class MemoryCreate(BaseModel):
    """Schema for creating memories"""
    title: str
    content: str
    category: str
    importance: float = 1.0


class MemoryResponse(BaseModel):
    """Schema for memory responses"""
    id: int
    title: str
    content: str
    category: str
    importance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Chat Schemas ============
class ChatMessage(BaseModel):
    """Schema for chat messages"""
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat responses"""
    reply: str
    sources: Optional[List[str]] = None
    confidence: float = 1.0


# ============ Conversation Schemas ============
class ConversationResponse(BaseModel):
    """Schema for conversation history"""
    id: int
    user_message: str
    assistant_reply: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Knowledge Schemas ============
class KnowledgeEntryCreate(BaseModel):
    """Schema for creating knowledge entries"""
    tradition: str
    topic: str
    content: str
    source: Optional[str] = None


class KnowledgeEntryResponse(BaseModel):
    """Schema for knowledge entry responses"""
    id: int
    tradition: str
    topic: str
    content: str
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Voice Schemas ============
class VoiceLogResponse(BaseModel):
    """Schema for voice interaction logs"""
    id: int
    audio_filename: str
    transcription: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Status Schemas ============
class StatusResponse(BaseModel):
    """Schema for status responses"""
    app: str
    status: str
    version: str
    features: dict
