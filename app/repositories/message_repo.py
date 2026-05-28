from sqlalchemy.orm import Session

from app.models.message import Message


class MessageRepository:

    @staticmethod
    def create(
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        provider: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0
    ):

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )

        db.add(message)

        db.commit()

        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: int
    ):
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()

    @staticmethod
    def get_by_id(
        db: Session,
        message_id: int
    ):
        return db.query(Message).filter(
            Message.id == message_id
        ).first()

    @staticmethod
    def get_messages_before(
        db: Session,
        conversation_id: int,
        message_id: int
    ):
        return db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.id < message_id
        ).order_by(Message.id.asc()).all()

    @staticmethod
    def get_next_message(
        db: Session,
        conversation_id: int,
        message_id: int,
        role: str = "assistant"
    ):
        return db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.id > message_id,
            Message.role == role
        ).order_by(Message.id.asc()).first()

    @staticmethod
    def update(
        db: Session,
        message,
        **kwargs
    ):
        for key, value in kwargs.items():
            setattr(message, key, value)

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def prune_messages(db: Session, conversation_id: int, keep: int = 20):
        messages_to_delete = db.query(Message) \
            .filter(Message.conversation_id == conversation_id) \
            .order_by(Message.created_at.desc()) \
            .offset(keep).all()

        for message in messages_to_delete:
            db.delete(message)

        db.commit()