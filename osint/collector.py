from .dns_checker import DNSChecker
from .tls_checker import TLSChecker
from .breach_checker import BreachChecker
from .policy_scraper import PolicyScraper
from models.osint_report import OSINTReport

class OSINTCollector:
    """Main OSINT collection orchestrator"""

    def __init__(self):
        self.dns_checker = DNSChecker()
        self.tls_checker = TLSChecker()
        self.breach_checker = BreachChecker()
        self.policy_scraper = PolicyScraper()

    def collect(self, domain: str) -> OSINTReport:
        """Collect all OSINT data for a domain"""

        # Run all checks
        dns = self.dns_checker.check(domain)
        tls = self.tls_checker.check(domain)
        breach = self.breach_checker.check(domain)
        policy = self.policy_scraper.scrape(domain)

        # Calculate overall OSINT score (average of all scores)
        scores = []
        if dns.security_score > 0:
            scores.append(dns.security_score)
        if tls.security_score > 0:
            scores.append(tls.security_score)
        if breach.security_score > 0:
            scores.append(breach.security_score)

        overall_score = sum(scores) / len(scores) if scores else 0.0

        return OSINTReport(
            domain=domain,
            dns=dns,
            tls=tls,
            breach=breach,
            policy=policy,
            overall_osint_score=overall_score
        )
