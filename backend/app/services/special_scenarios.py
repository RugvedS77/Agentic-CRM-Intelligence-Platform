from app.services.classifier_service import classify_email
from app.services.planner_service import create_plan
from app.agent.tool_executor import execute_tool
from app.agent.state import AgentState


def detect_special_scenario(email_text: str, classification: dict) -> str | None:
    text = (email_text or "").lower()
    category = (classification.get("category") or "").lower()
    sentiment = (classification.get("sentiment") or "").lower()

    if "gdpr" in text or "article 20" in text or "data portability" in text or "right to erasure" in text:
        return "gdpr_request"

    if any(keyword in text for keyword in ["ransomware", "breach", "data leak", "btc", "bitcoin", "extortion", "p0", "production down"]):
        return "ransomware_threat"

    if any(keyword in text for keyword in ["misinformation", "false claim", "incorrect information", "hallucination"]):
        return "chatbot_misinformation"

    if any(keyword in text for keyword in ["reputation crisis", "public backlash", "social media storm", "viral complaint"]):
        return "reputation_crisis"

    if sentiment == "mixed" or "conflict" in text or "contradict" in text:
        return "conflicting_signals"

    return None


def handle_special_scenario(
    scenario: str,
    email_text: str,
    classification: dict,
    email_id: str
) -> dict:
    if scenario == "gdpr_request":
        return {
            "scenario": scenario,
            "action": "flag_for_legal",
            "reason": "GDPR/data privacy request requires legal/compliance review. Do NOT auto-reply.",
            "requires_human": True,
            "escalation_reason": classification.get("escalation_reason") or "GDPR request detected"
        }

    if scenario == "ransomware_threat":
        return {
            "scenario": scenario,
            "action": "flag_for_security",
            "reason": "Security threat detected. Immediate security team review required.",
            "requires_human": True,
            "escalation_reason": classification.get("escalation_reason") or "Ransomware/security threat detected"
        }

    if scenario == "chatbot_misinformation":
        return {
            "scenario": scenario,
            "action": "escalate_to_human",
            "reason": "Potential chatbot misinformation detected. Human review required before responding.",
            "requires_human": True,
            "escalation_reason": classification.get("escalation_reason") or "Misinformation risk detected"
        }

    if scenario == "reputation_crisis":
        return {
            "scenario": scenario,
            "action": "escalate_to_human",
            "reason": "Reputation crisis detected. PR/communications team must review before any response.",
            "requires_human": True,
            "escalation_reason": classification.get("escalation_reason") or "Reputation crisis detected"
        }

    if scenario == "conflicting_signals":
        return {
            "scenario": scenario,
            "action": "escalate_to_human",
            "reason": "Conflicting signals detected in email. Human review required to resolve mixed intent.",
            "requires_human": True,
            "escalation_reason": classification.get("escalation_reason") or "Conflicting signals detected"
        }

    return {
        "scenario": scenario,
        "action": "escalate_to_human",
        "reason": "Special scenario detected. Human review required.",
        "requires_human": True,
        "escalation_reason": classification.get("escalation_reason") or "Special scenario detected"
    }


def process_special_scenario(email_id: str, email_text: str) -> dict:
    classification = classify_email(
        email_content=email_text,
        thread_context="",
        rag_context=""
    )

    scenario = detect_special_scenario(email_text, classification.dict())
    if not scenario:
        return {
            "scenario": None,
            "classification": classification.dict(),
            "action": None
        }

    special_action = handle_special_scenario(
        scenario=scenario,
        email_text=email_text,
        classification=classification.dict(),
        email_id=email_id
    )

    return {
        "scenario": scenario,
        "classification": classification.dict(),
        "special_action": special_action
    }
