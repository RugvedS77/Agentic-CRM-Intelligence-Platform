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

Classify the email using the provided schema.

RULES FOR CLASSIFICATION:
1. Conflicting Signals: If an email contains mixed sentiment (e.g., "Love the product, but hate the price and want a refund"), classify sentiment as "Mixed", prioritize the negative action (e.g., Category: "Billing" or "Complaint"), and set `requires_human` to true.
2. Confidence Threshold: If your confidence in the classification is below 0.70, you MUST set `requires_human` to true and provide an `escalation_reason`.
3. Extraction: Extract any order IDs, ticket IDs, monetary amounts, deadlines, and products into `detected_entities`.
4. GDPR / Data Privacy Requests: If the email mentions GDPR, Article 20, data portability, right to erasure, privacy request, or similar legal data-rights language, classify category as "Compliance", set urgency to "High" or "Critical", set `requires_human` to true, and set `escalation_reason` to "GDPR/data privacy request requires legal/compliance review. Do NOT auto-reply."
5. Security Threats: If the email mentions ransomware, breach, data leak, BTC payment demand, or extortion, classify category as "Security", urgency as "Critical", and set `requires_human` to true.
6. Legal Threats: If the email mentions cease and desist, legal action, lawsuit, or attorney, classify category as "Legal", urgency as "High" or "Critical", and set `requires_human` to true.
7. Policy Citation: In your `reasoning` field, explicitly cite which policy document(s) from the retrieved context informed your classification. Use the document source names provided in the context.

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