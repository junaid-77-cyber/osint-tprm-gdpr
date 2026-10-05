import requests
from bs4 import BeautifulSoup
import textstat
from models.policy_findings import PolicyFindings

class PolicyScraper:
    """Scrape and analyze privacy policy"""

    def scrape(self, domain: str) -> PolicyFindings:
        """Scrape privacy policy from domain"""
        try:
            # Try common privacy policy URLs
            urls_to_try = [
                f'https://{domain}/privacy',
                f'https://{domain}/privacy-policy',
                f'https://{domain}/privacypolicy',
                f'https://{domain}/privacy.html',
                f'http://{domain}/privacy',
            ]

            for url in urls_to_try:
                try:
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        return self._parse_policy(url, response.text)
                except:
                    continue

            # Try finding link on homepage
            try:
                response = requests.get(f'https://{domain}', timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Look for privacy policy links
                    for link in soup.find_all('a', href=True):
                        href = link['href'].lower()
                        link_text = link.get_text().lower()

                        if 'privacy' in href or 'privacy' in link_text:
                            full_url = href if href.startswith('http') else f'https://{domain}{href}'
                            try:
                                policy_response = requests.get(full_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                                if policy_response.status_code == 200:
                                    return self._parse_policy(full_url, policy_response.text)
                            except:
                                continue
            except:
                pass

            return PolicyFindings(
                found=False,
                details="Privacy policy not found"
            )

        except Exception as e:
            return PolicyFindings(
                found=False,
                error=str(e),
                details="Policy scraping failed"
            )

    def _parse_policy(self, url: str, html: str) -> PolicyFindings:
        """Parse and analyze policy text"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove scripts, styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            word_count = len(text.split())

            # Calculate readability (Flesch Reading Ease)
            try:
                readability = textstat.flesch_reading_ease(text)
            except:
                readability = 0.0

            if word_count < 500:
                return PolicyFindings(
                    found=False,
                    details="Text too short to be valid policy"
                )

            return PolicyFindings(
                found=True,
                url=url,
                text=text[:10000],  # Store first 10k chars
                word_count=word_count,
                readability_score=readability,
                details=f"Found policy with {word_count} words, readability: {readability:.1f}"
            )

        except Exception as e:
            return PolicyFindings(
                found=False,
                error=str(e),
                details="Policy parsing failed"
            )
