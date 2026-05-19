import os
import shutil

from app.rag.pdf_loader import (
    load_and_split_pdf
)

from app.rag.vectordb import (
    create_vector_store
)


class RagService:

    @staticmethod
    def upload_pdf(
        conversation_id: int,
        file
    ):

        folder_path = f"uploads/{conversation_id}"

        os.makedirs(
            folder_path,
            exist_ok=True
        )

        file_path = (
            f"{folder_path}/{file.filename}"
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        documents = load_and_split_pdf(
            file_path
        )

        create_vector_store(
            conversation_id,
            documents
        )

        return {
            "message": "PDF uploaded successfully"
        }