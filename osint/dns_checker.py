import dns.resolver
from models.dns_findings import DNSFindings

class DNSChecker:
    """Check DNS security records"""

    def check(self, domain: str) -> DNSFindings:
        """Perform DNS security checks"""
        try:
            has_spf = False
            has_dmarc = False
            has_dnssec = False
            mx_count = 0

            # Check SPF record
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                for rdata in answers:
                    if 'v=spf1' in str(rdata):
                        has_spf = True
                        break
            except:
                pass

            # Check DMARC record
            try:
                dmarc_domain = f'_dmarc.{domain}'
                answers = dns.resolver.resolve(dmarc_domain, 'TXT')
                for rdata in answers:
                    if 'v=DMARC1' in str(rdata):
                        has_dmarc = True
                        break
            except:
                pass

            # Check MX records
            try:
                mx_answers = dns.resolver.resolve(domain, 'MX')
                mx_count = len(list(mx_answers))
            except:
                pass

            # Calculate security score
            score = 0.0
            if has_spf:
                score += 35
            if has_dmarc:
                score += 35
            if mx_count > 0:
                score += 30

            details = f"SPF: {'✓' if has_spf else '✗'}, DMARC: {'✓' if has_dmarc else '✗'}, MX Records: {mx_count}"

            return DNSFindings(
                has_spf=has_spf,
                has_dmarc=has_dmarc,
                has_dnssec=has_dnssec,
                mx_records=mx_count,
                security_score=score,
                details=details
            )

        except Exception as e:
            return DNSFindings(
                error=str(e),
                details="DNS check failed"
            )
