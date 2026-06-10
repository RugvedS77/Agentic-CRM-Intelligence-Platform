from pydantic import BaseModel
from typing import List


class AgentPlan(BaseModel):
    reasoning: str
    tools: List[str]
    priority: str = "medium"