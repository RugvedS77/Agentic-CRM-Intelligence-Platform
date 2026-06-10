from pydantic import BaseModel


class TraceStep(BaseModel):
    thought: str
    action: str
    observation: dict | str
    next: str