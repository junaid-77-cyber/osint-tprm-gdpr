from pydantic import BaseModel
from typing import Optional

class DNSFindings(BaseModel):
    """DNS security check results"""
    has_spf: bool = False
    has_dmarc: bool = False
    has_dnssec: bool = False
    mx_records: int = 0
    security_score: float = 0.0
    details: str = ""
    error: Optional[str] = None
