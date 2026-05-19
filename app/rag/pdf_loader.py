from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import re


def load_and_split_pdf(file_path: str, use_semantic_chunking: bool = True):
    """
    Load and split PDF using recursive or semantic chunking.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    if use_semantic_chunking:
        split_docs = _semantic_chunk(documents)
    else:
        split_docs = _recursive_chunk(documents)

    for index, doc in enumerate(split_docs, start=1):
        source = doc.metadata.get("source", file_path)
        page = doc.metadata.get("page", 0)

        doc.metadata["source"] = source
        doc.metadata["chunk_id"] = index
        doc.metadata["page"] = page
        doc.metadata["source_index"] = index

    return split_docs


def _recursive_chunk(documents: List[Document]) -> List[Document]:
    """Traditional recursive character-based chunking."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(documents)


def _semantic_chunk(documents: List[Document]) -> List[Document]:
    """Semantic chunking based on sentence boundaries."""
    semantic_docs = []

    for doc in documents:
        sentences = _split_into_sentences(doc.page_content)
        chunks = _group_sentences_into_chunks(sentences, target_chunk_size=800)

        for chunk_text in chunks:
            new_doc = Document(
                page_content=chunk_text,
                metadata=doc.metadata.copy()
            )
            semantic_docs.append(new_doc)

    return semantic_docs


def _split_into_sentences(text: str) -> List[str]:
    sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_endings, text)
    return [s.strip() for s in sentences if s.strip()]


def _group_sentences_into_chunks(
    sentences: List[str],
    target_chunk_size: int = 800,
    overlap_sentences: int = 2
) -> List[str]:
    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        current_chunk.append(sentence)
        current_length += sentence_length + 1

        if current_length > target_chunk_size and len(current_chunk) > 2:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            if len(current_chunk) > overlap_sentences:
                current_chunk = current_chunk[-overlap_sentences:]
                current_length = sum(len(s) for s in current_chunk) + overlap_sentences
            else:
                current_chunk = []
                current_length = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
