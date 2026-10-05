import ssl
import socket
from datetime import datetime
from models.tls_findings import TLSFindings

class TLSChecker:
    """Check TLS/SSL certificate"""

    def check(self, domain: str) -> TLSFindings:
        """Perform TLS/SSL security checks"""
        try:
            context = ssl.create_default_context()

            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    tls_version = ssock.version()

                    # Parse expiry date
                    expiry_str = cert.get('notAfter')
                    if expiry_str:
                        expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days

                        # Calculate score
                        score = 0.0
                        is_secure = True

                        if days_until_expiry > 30:
                            score += 50
                        elif days_until_expiry > 0:
                            score += 25
                            is_secure = False
                        else:
                            is_secure = False

                        if tls_version and 'TLSv1.2' in tls_version or 'TLSv1.3' in tls_version:
                            score += 50
                        else:
                            is_secure = False

                        details = f"TLS Version: {tls_version}, Expires in {days_until_expiry} days"

                        return TLSFindings(
                            has_valid_cert=True,
                            cert_expiry=expiry_str,
                            days_until_expiry=days_until_expiry,
                            tls_version=tls_version,
                            is_secure=is_secure,
                            security_score=score,
                            details=details
                        )

            return TLSFindings(error="Could not retrieve certificate information")

        except Exception as e:
            return TLSFindings(
                error=str(e),
                details="TLS check failed"
            )
