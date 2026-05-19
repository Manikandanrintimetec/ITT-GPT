from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime
)
from sqlalchemy.orm import relationship

from datetime import datetime

from app.core.database import Base


class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id")
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    role = Column(String)

    content = Column(Text)

    provider = Column(String)

    prompt_tokens = Column(Integer, default=0)

    completion_tokens = Column(Integer, default=0)

    total_tokens = Column(Integer, default=0)

    model_name = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )