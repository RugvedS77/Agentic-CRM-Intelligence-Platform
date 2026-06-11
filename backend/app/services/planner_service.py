# app/services/planner.py

from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

from app.schemas.agent_plan_schema import AgentPlan
from app.agent.tools_registry import TOOLS


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
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
- GDPR requests require compliance review.
- Maximum 6 tool calls.
- Only choose tools from the provided tool list.
- Do not invent tools.
- Minimize unnecessary tool usage.
- Prefer escalation when confidence is low.

Additional Guidance:

- GDPR requests should consult the knowledge base before action.
- Refund requests should review customer history and refund policy.
- Legal threats should gather sufficient context before escalation.
- Legal threats must always be escalated to a human after legal review and drafting reply.
- Enterprise customers and VIP customers require account review before final decisions.
- When policy decisions are involved, prefer using search_knowledge_base.
- If urgency = critical → always include escalate_to_human
For:
- refund
- billing
- technical_support
- legal_threat involving SLA disputes
- vip_churn

Include: search_knowledge_base, draft_reply

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