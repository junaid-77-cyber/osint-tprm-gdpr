from pydantic import BaseModel
from typing import List, Optional

class BreachFindings(BaseModel):
    """Breach data check results from HaveIBeenPwned"""
    breach_count: int = 0
    breaches: List[str] = []
    has_breaches: bool = False
    security_score: float = 0.0
    details: str = ""
    error: Optional[str] = None
