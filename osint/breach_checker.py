import requests
import os
from dotenv import load_dotenv
from models.breach_findings import BreachFindings

load_dotenv()

class BreachChecker:
    """Check breach data from HaveIBeenPwned"""

    def __init__(self):
        self.api_key = os.getenv('HIBP_API_KEY', '')
        self.base_url = 'https://haveibeenpwned.com/api/v3'

    def check(self, domain: str) -> BreachFindings:
        """Check for data breaches"""
        if not self.api_key:
            return BreachFindings(
                error="HIBP API key not configured",
                details="Set HIBP_API_KEY in .env file"
            )

        try:
            headers = {
                'hibp-api-key': self.api_key,
                'user-agent': 'OSINT-TPRM-Tool'
            }

            url = f'{self.base_url}/breaches?domain={domain}'
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                breaches = response.json()
                breach_names = [b.get('Name', 'Unknown') for b in breaches]
                breach_count = len(breaches)

                # Calculate score (fewer breaches = higher score)
                if breach_count == 0:
                    score = 100.0
                elif breach_count <= 2:
                    score = 50.0
                else:
                    score = 0.0

                details = f"Found {breach_count} breach(es)" if breach_count > 0 else "No breaches found"

                return BreachFindings(
                    breach_count=breach_count,
                    breaches=breach_names,
                    has_breaches=(breach_count > 0),
                    security_score=score,
                    details=details
                )
            elif response.status_code == 404:
                # No breaches found
                return BreachFindings(
                    breach_count=0,
                    security_score=100.0,
                    details="No breaches found"
                )
            else:
                return BreachFindings(
                    error=f"API returned status {response.status_code}",
                    details="Unable to check breaches"
                )

        except Exception as e:
            return BreachFindings(
                error=str(e),
                details="Breach check failed"
            )
