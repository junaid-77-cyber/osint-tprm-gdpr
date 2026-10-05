from pydantic import BaseModel
from typing import Optional

class PolicyFindings(BaseModel):
    """Privacy policy scraping results"""
    found: bool = False
    url: Optional[str] = None
    text: str = ""
    word_count: int = 0
    readability_score: float = 0.0
    details: str = ""
    error: Optional[str] = None
