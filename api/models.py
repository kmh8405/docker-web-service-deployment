import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# Conversation(1) <-> Message(N) 1개의 대화 안에 N개의 메시지 (1대다)
class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(),
    )

class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    conversation_id: Mapped[str] = mapped_column(
        # Conversation 클래스의 id를 가져와야 함
        ForeignKey("conversation.id")
    )
    role: Mapped[str] = mapped_column(String(10)) # user / assistant (assistant말고 다른거 쓰면 안 됨)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(),
    )
    