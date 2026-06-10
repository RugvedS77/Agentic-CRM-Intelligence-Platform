from pathlib import Path

from langchain_core.documents import Document


def load_documents():

    docs = []

    kb_path = Path("app/knowledge_base")

    for file in kb_path.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": file.name
                }
            )
        )

    return docs