from pydantic import BaseModel
from typing import Dict, List

class RiskScore(BaseModel):
    """Overall risk assessment results"""
    overall_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH
    gdpr_scores: Dict[str, float]  # Control name -> confidence score
    recommendations: List[str]
    osint_summary: str
    compliant_controls: int
    total_controls: int
