# app/services/planner.py

from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

from app.schemas.agent_plan_schema import AgentPlan
from app.agent.tools_registry import TOOLS


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

planner_llm = llm.with_structured_output(
    AgentPlan
)

PLANNER_PROMPT = """
You are an autonomous CRM triage agent.

Your job is to decide which tools should be executed.

Rules:
- Security incidents must never receive auto replies.
- Legal threats must be escalated.
- GDPR requests require compliance review and the creation of an internal ticket using `create_internal_ticket`.
- Maximum 6 tool calls.
- If urgency = "Critical", you MUST include `escalate_to_human` and NEVER use `send_auto_reply`.
- If the email mentions public reviews, Twitter, G2, or Trustpilot, you MUST use `scrape_public_sentiment`.
- If `requires_human` is true from the classification, ensure `escalate_to_human` is in the plan.
- Only choose tools from the provided tool list. Do not invent tools.
- CRITICAL SAFEGUARDS:
  * NEVER use `send_auto_reply` for Spam, Legal, or Security categories.
  * NEVER use `send_auto_reply` when urgency is Critical.
  * NEVER use `send_auto_reply` when requires_human is true.
  * For GDPR/data privacy requests, ALWAYS include `flag_for_legal` and `create_internal_ticket`, and NEVER use `send_auto_reply`.

Available Tools:
{tools}

Classification:
{classification}

Email:
{email}

Retrieved Policy Context:
{rag_context}
"""

def create_plan(
    email_text: str,
    classification: dict,
    rag_context: list
) -> AgentPlan:

    prompt = PLANNER_PROMPT.format(
        tools="\n".join(f"- {tool}" for tool in TOOLS),
        classification=classification,
        email=email_text,
        rag_context=rag_context
    )

    return planner_llm.invoke(prompt)