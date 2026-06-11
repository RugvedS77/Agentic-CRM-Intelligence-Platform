from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.gemini import llm
from app.rag.retriever import retrieve_context
from app.schemas.classification_schema import ClassificationResult


parser = PydanticOutputParser(
    pydantic_object=ClassificationResult
)


def classify_email(
    email_content: str,
    thread_context: str,
    rag_context: str
) -> ClassificationResult:

    # rag_chunks = retrieve_context(
    #     email_content,
    #     k=3
    # )

    # rag_context = "\n\n".join(
    #     [
    #         f"Source: {chunk['source']}\n"
    #         f"{chunk['content']}"
    #         for chunk in rag_chunks
    #     ]
    # )

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI CRM triage system.

Classify the email into one of:

billing
refund
technical_support
gdpr_request
security_incident
legal_threat
vip_churn
general_inquiry
spam

THREAD CONTEXT:
{thread_context}

CURRENT EMAIL:
{email_content}

RETRIEVED POLICY DOCUMENTS:
{rag_context}

Return JSON only.

{format_instructions}
"""
    )

    chain = prompt | llm | parser

    return chain.invoke(
        {
            "thread_context": thread_context,
            "email_content": email_content,
            "rag_context": rag_context,
            "format_instructions":
                parser.get_format_instructions()
        }
    )