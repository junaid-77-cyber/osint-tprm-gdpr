import requests
from bs4 import BeautifulSoup
import textstat
from models.policy_findings import PolicyFindings

class PolicyScraper:
    """Scrape and analyze privacy policy"""

    def scrape(self, domain: str) -> PolicyFindings:
        """Scrape privacy policy from domain"""
        try:
            # Extract base domain (remove www)
            base_domain = domain.replace('www.', '')

            # Try common privacy policy URLs (most specific first)
            urls_to_try = [
                # Major tech company specific URLs
                f'https://policies.{base_domain}/privacy',
                f'https://www.{base_domain}/privacy-policy',
                f'https://{base_domain}/privacy-policy',
                f'https://{base_domain}/legal/privacy',
                f'https://{base_domain}/about/privacy',
                f'https://{base_domain}/privacypolicy',
                f'https://{base_domain}/privacy',
                f'https://{base_domain}/privacy.html',
                f'https://{base_domain}/en/privacy',
                f'https://{base_domain}/terms/privacy',
                f'http://{base_domain}/privacy-policy',
                f'http://{base_domain}/privacy',
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

                    # Look for privacy policy links (prioritize full policy links)
                    privacy_links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href'].lower()
                        link_text = link.get_text().lower()

                        if 'privacy' in href or 'privacy policy' in link_text or 'privacy' in link_text:
                            # Prioritize links with "policy" in URL/text
                            priority = 2 if 'policy' in href or 'policy' in link_text else 1
                            full_url = href if href.startswith('http') else f'https://{domain}{href}'
                            privacy_links.append((priority, full_url))

                    # Sort by priority (highest first)
                    privacy_links.sort(reverse=True, key=lambda x: x[0])

                    # Try each link
                    for _, full_url in privacy_links[:5]:  # Try top 5
                        try:
                            policy_response = requests.get(full_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                            if policy_response.status_code == 200:
                                parsed = self._parse_policy(full_url, policy_response.text)
                                # Only return if policy is substantial (>1500 words)
                                if parsed.found and parsed.word_count >= 1500:
                                    return parsed
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

            # Remove scripts, styles, nav, footer, header
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "menu"]):
                element.decompose()

            # Try to find main content area first
            main_content = None
            content_selectors = [
                soup.find('main'),
                soup.find('article'),
                soup.find('div', class_=lambda x: x and any(c in str(x).lower() for c in ['content', 'policy', 'main', 'body', 'article'])),
                soup.find('div', id=lambda x: x and any(c in str(x).lower() for c in ['content', 'policy', 'main', 'body', 'article'])),
            ]

            for selector in content_selectors:
                if selector:
                    main_content = selector
                    break

            # Extract text from main content or full page
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()

            # Clean text aggressively
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Remove repeated navigation text (common issue)
            lines = text.split('\n')
            seen = {}
            cleaned_lines = []
            for line in lines:
                if len(line) > 20:  # Only check substantial lines
                    if line not in seen or seen[line] < 2:  # Allow max 2 repetitions
                        cleaned_lines.append(line)
                        seen[line] = seen.get(line, 0) + 1
                elif len(line) > 0:
                    cleaned_lines.append(line)

            text = '\n'.join(cleaned_lines)

            word_count = len(text.split())

            # Calculate readability (Flesch Reading Ease)
            try:
                readability = textstat.flesch_reading_ease(text)
            except:
                readability = 0.0

            # Be lenient with word count for initial finding
            if word_count < 300:
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
