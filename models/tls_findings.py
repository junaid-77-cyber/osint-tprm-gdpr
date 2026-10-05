from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TLSFindings(BaseModel):
    """TLS/SSL certificate check results"""
    has_valid_cert: bool = False
    cert_expiry: Optional[str] = None
    days_until_expiry: Optional[int] = None
    tls_version: Optional[str] = None
    is_secure: bool = False
    security_score: float = 0.0
    details: str = ""
    error: Optional[str] = None
