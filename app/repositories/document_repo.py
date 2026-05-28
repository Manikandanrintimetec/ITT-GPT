from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:

    @staticmethod
    def create(
        db: Session,
        conversation_id: int,
        file_name: str
    ):

        document = Document(
            conversation_id=conversation_id,
            file_name=file_name
        )

        db.add(document)

        db.commit()

        db.refresh(document)

        return document

    @staticmethod
    def get_documents(
        db: Session,
        conversation_id: int
    ):

        return db.query(Document).filter(
            Document.conversation_id == conversation_id
        ).all()

    @staticmethod
    def delete_documents(
        db: Session,
        conversation_id: int
    ):

        db.query(Document).filter(
            Document.conversation_id == conversation_id
        ).delete()

        db.commit()