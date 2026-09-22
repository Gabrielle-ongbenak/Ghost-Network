import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RiskSignalResponse(BaseModel):
    id: uuid.UUID
    rule_code: str
    severity: str
    score_points: int
    explanation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
