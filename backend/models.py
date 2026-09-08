"""Database models for God's Eye"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from backend.database import Base


class JournalEntry(Base):
    """Journal entry model"""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)
    mood = Column(String(50), nullable=True)
    tags = Column(String(255), nullable=True)  # comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Memory(Base):
    """Memory model for knowledge retention"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)
    category = Column(String(100), index=True)  # spiritual, practical, learned, etc.
    importance = Column(Float, default=1.0)  # 0.0-1.0 scale
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Conversation(Base):
    """Conversation history model"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text)
    assistant_reply = Column(Text)
    context = Column(Text, nullable=True)  # JSON context
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeEntry(Base):
    """Knowledge base entries for different spiritual traditions"""
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    tradition = Column(String(100), index=True)  # Buddhism, Christianity, Islam, etc.
    topic = Column(String(255), index=True)
    content = Column(Text)
    source = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VoiceLog(Base):
    """Voice interaction logs"""
    __tablename__ = "voice_logs"

    id = Column(Integer, primary_key=True, index=True)
    audio_filename = Column(String(255))
    transcription = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
