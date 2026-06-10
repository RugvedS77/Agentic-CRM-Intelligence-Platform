from langchain_chroma import Chroma

from app.rag.embeddings import embeddings


vectorstore = Chroma(
    collection_name="senai_kb",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)