import json
import re
from typing import Dict, List

class NLPClassifier:
    """Enhanced keyword-based GDPR control classifier with scoring"""

    def __init__(self):
        # Comprehensive GDPR keywords with importance weights
        self.keywords = {
            "data_minimization": {
                "high": [
                    "only collect necessary", "minimal data collection", "data minimization",
                    "adequate, relevant and limited", "necessary and proportionate",
                    "limit the collection", "only information needed"
                ],
                "medium": [
                    "only necessary", "minimal data", "essential information",
                    "minimum amount", "necessary for", "relevant data"
                ],
                "low": [
                    "specific data", "required information", "needed data"
                ]
            },
            "purpose_limitation": {
                "high": [
                    "specific, explicit and legitimate purposes", "purpose limitation",
                    "not used for purposes other than", "original purpose only",
                    "specified and legitimate purposes"
                ],
                "medium": [
                    "specific purpose", "explicit purpose", "clearly defined purpose",
                    "legitimate purposes", "designated purpose"
                ],
                "low": [
                    "purpose of", "use for", "intended for"
                ]
            },
            "storage_limitation": {
                "high": [
                    "data retention policy", "storage limitation", "delete after",
                    "retention period", "how long we keep your data",
                    "no longer than necessary"
                ],
                "medium": [
                    "storage limit", "retention schedule", "data deletion",
                    "keep your information for", "retain data"
                ],
                "low": [
                    "delete", "remove", "time period"
                ]
            },
            "accuracy": {
                "high": [
                    "ensure data accuracy", "accurate and up to date",
                    "maintain accuracy", "update your information",
                    "correct inaccurate data"
                ],
                "medium": [
                    "data accuracy", "keep information accurate",
                    "accuracy of personal data", "verify information"
                ],
                "low": [
                    "accurate", "correct", "update"
                ]
            },
            "integrity_confidentiality": {
                "high": [
                    "technical and organizational measures", "security of personal data",
                    "protect against unauthorized", "confidentiality and integrity",
                    "appropriate security measures", "encryption of data"
                ],
                "medium": [
                    "security measures", "protect your data", "encryption",
                    "secure storage", "safeguards", "data protection"
                ],
                "low": [
                    "secure", "safety", "protection"
                ]
            },
            "lawfulness": {
                "high": [
                    "lawful basis for processing", "legal basis for collection",
                    "legitimate interest", "contractual necessity",
                    "legal obligation to process", "article 6"
                ],
                "medium": [
                    "legal basis", "lawful processing", "legal grounds",
                    "legitimate reason", "lawful purpose"
                ],
                "low": [
                    "legal", "lawful", "comply with law"
                ]
            },
            "transparency": {
                "high": [
                    "transparent manner", "clear and accessible information",
                    "explain how we use", "inform you about how",
                    "transparency in data processing"
                ],
                "medium": [
                    "transparent", "clear information", "inform you",
                    "explain", "tell you about", "disclose"
                ],
                "low": [
                    "information about", "details of", "describe"
                ]
            },
            "consent": {
                "high": [
                    "with your consent", "obtain your consent", "withdraw consent",
                    "freely given consent", "explicit consent",
                    "opt-in consent", "consent mechanism"
                ],
                "medium": [
                    "your consent", "with your permission", "agree to",
                    "consent to", "ask for consent"
                ],
                "low": [
                    "permission", "agree", "accept"
                ]
            },
            "data_subject_rights": {
                "high": [
                    "right to access", "right to rectification", "right to erasure",
                    "right to data portability", "right to object",
                    "right to restriction", "exercise your rights",
                    "subject access request"
                ],
                "medium": [
                    "your rights", "data subject rights", "access your data",
                    "delete your data", "request deletion", "correct your data"
                ],
                "low": [
                    "rights", "request", "access"
                ]
            },
            "dpo_contact": {
                "high": [
                    "data protection officer", "contact our dpo",
                    "dpo@", "data protection contact",
                    "reach our data protection officer"
                ],
                "medium": [
                    "dpo", "privacy officer", "data protection team",
                    "privacy contact", "data protection authority"
                ],
                "low": [
                    "privacy", "contact us", "email"
                ]
            }
        }

    def classify(self, policy_text: str) -> Dict[str, float]:
        """
        Enhanced classification with weighted keyword matching
        Returns dict of control -> confidence score (0.0-1.0)
        """
        if not policy_text or len(policy_text) < 100:
            return {control: 0.0 for control in self.keywords.keys()}

        policy_lower = policy_text.lower()
        scores = {}

        for control, keyword_groups in self.keywords.items():
            # Weighted scoring
            high_matches = sum(1 for kw in keyword_groups["high"] if kw in policy_lower)
            medium_matches = sum(1 for kw in keyword_groups["medium"] if kw in policy_lower)
            low_matches = sum(1 for kw in keyword_groups["low"] if kw in policy_lower)

            # Calculate weighted score
            weighted_score = (high_matches * 3.0) + (medium_matches * 1.5) + (low_matches * 0.5)

            # Normalize to 0-1 range
            # Target: 2 high matches OR 4 medium matches OR mix = 1.0
            max_expected_score = 6.0
            confidence = min(weighted_score / max_expected_score, 1.0)

            # Bonus for multiple keyword types
            types_found = sum([
                1 if high_matches > 0 else 0,
                1 if medium_matches > 0 else 0,
                1 if low_matches > 0 else 0
            ])

            if types_found >= 2:
                confidence = min(confidence * 1.1, 1.0)  # 10% bonus

            scores[control] = round(confidence, 3)

        # Additional heuristics
        scores = self._apply_heuristics(scores, policy_text)

        return scores

    def _apply_heuristics(self, scores: Dict[str, float], policy_text: str) -> Dict[str, float]:
        """Apply additional heuristics to improve accuracy"""
        policy_lower = policy_text.lower()
        word_count = len(policy_text.split())

        # If policy is very short, reduce all scores
        if word_count < 500:
            scores = {k: v * 0.5 for k, v in scores.items()}

        # If "GDPR" is explicitly mentioned, boost credibility
        if "gdpr" in policy_lower or "general data protection regulation" in policy_lower:
            scores = {k: min(v * 1.15, 1.0) for k, v in scores.items()}

        # Email presence boosts DPO contact score
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.search(email_pattern, policy_text):
            scores["dpo_contact"] = min(scores["dpo_contact"] + 0.2, 1.0)

        # If "article" numbers mentioned (GDPR articles), boost lawfulness
        if re.search(r'article\s+\d+', policy_lower):
            scores["lawfulness"] = min(scores["lawfulness"] + 0.15, 1.0)

        # Check for rights section (long list of rights)
        if "right to" in policy_lower:
            right_count = policy_lower.count("right to")
            if right_count >= 4:
                scores["data_subject_rights"] = min(scores["data_subject_rights"] + 0.2, 1.0)

        return scores
