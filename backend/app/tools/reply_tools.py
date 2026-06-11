from langchain_core.prompts import ChatPromptTemplate

from app.llm.gemini import llm


def draft_reply(
    email_body: str,
    rag_context: str,
    tone: str = "professional"
):
    prompt = ChatPromptTemplate.from_template(
        """
You are a customer support agent.

Write a short reply.

TONE:
{tone}

CUSTOMER EMAIL:
{email_body}

POLICY CONTEXT:
{rag_context}

Requirements:
- Be empathetic
- Do not promise anything not present in policy
- Cite policy documents used
- Keep under 200 words
"""
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "tone": tone,
            "email_body": email_body,
            "rag_context": rag_context
        }
    )

    return response.content