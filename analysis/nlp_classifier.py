import json
from typing import Dict

class NLPClassifier:
    """Keyword-based GDPR control classifier"""

    def __init__(self):
        self.keywords = {
            "data_minimization": [
                "only necessary", "minimal data", "essential information",
                "purpose-specific", "adequate, relevant and limited",
                "minimum amount", "necessary for", "minimal information"
            ],
            "purpose_limitation": [
                "specific purpose", "not use for", "original purpose",
                "clearly defined", "explicit purpose", "specified purposes",
                "legitimate purposes"
            ],
            "storage_limitation": [
                "retention period", "delete after", "storage limit",
                "no longer necessary", "retention policy", "data retention",
                "how long we keep"
            ],
            "accuracy": [
                "data accuracy", "keep information accurate", "update your information",
                "correct inaccurate", "accurate and up to date", "accuracy of data"
            ],
            "integrity_confidentiality": [
                "security measures", "protect your data", "encryption",
                "secure", "confidentiality", "integrity", "safeguards",
                "technical and organizational measures"
            ],
            "lawfulness": [
                "legal basis", "lawful basis", "legitimate interest",
                "contractual necessity", "legal obligation", "consent as basis"
            ],
            "transparency": [
                "transparent", "clear information", "inform you",
                "explain how", "what information we collect", "how we use"
            ],
            "consent": [
                "your consent", "with your permission", "opt-in", "agree to",
                "consent to", "ask for your consent", "withdraw consent"
            ],
            "data_subject_rights": [
                "right to access", "right to delete", "right to rectification",
                "data portability", "right to object", "erasure", "your rights",
                "access your data"
            ],
            "dpo_contact": [
                "data protection officer", "dpo", "privacy officer",
                "contact our dpo", "data protection contact"
            ]
        }

    def classify(self, policy_text: str) -> Dict[str, float]:
        """
        Classify policy text for GDPR controls
        Returns dict of control -> confidence score (0.0-1.0)
        """
        if not policy_text:
            return {control: 0.0 for control in self.keywords.keys()}

        policy_lower = policy_text.lower()
        scores = {}

        for control, keywords in self.keywords.items():
            matches = sum(1 for kw in keywords if kw in policy_lower)
            # Normalize: 0 matches = 0.0, 3+ matches = 1.0
            confidence = min(matches / 3.0, 1.0)
            scores[control] = confidence

        return scores
