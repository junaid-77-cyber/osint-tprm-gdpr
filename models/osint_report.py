from pydantic import BaseModel
from .dns_findings import DNSFindings
from .tls_findings import TLSFindings
from .breach_findings import BreachFindings
from .policy_findings import PolicyFindings

class OSINTReport(BaseModel):
    """Complete OSINT collection results for a domain"""
    domain: str
    dns: DNSFindings
    tls: TLSFindings
    breach: BreachFindings
    policy: PolicyFindings
    overall_osint_score: float = 0.0
