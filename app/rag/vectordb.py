import os

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from app.rag.embeddings import get_embedding_model


BASE_PATH = "chroma_db"


def get_conversation_path(conversation_id: int):

    return os.path.join(
        BASE_PATH,
        str(conversation_id)
    )


def create_vector_store(
    conversation_id,
    documents
):
    persist_directory = get_conversation_path(
        conversation_id
    )

    embeddings = get_embedding_model()

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    # ChromaDB persists automatically with persist_directory parameter


def load_vector_store(conversation_id):
    persist_directory = get_conversation_path(
        conversation_id
    )

    if not os.path.exists(persist_directory):
        return None

    embeddings = get_embedding_model()

    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )