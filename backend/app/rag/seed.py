from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from app.rag.loader import load_documents
from app.rag.vector_store import vectorstore


def seed():

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,      # ~300-400 tokens
            chunk_overlap=200
    )

    chunks = splitter.split_documents(
        docs
    )

    vectorstore.add_documents(
        chunks
    )

    print(
        f"Loaded {len(chunks)} chunks"
    )


if __name__ == "__main__":
    seed()