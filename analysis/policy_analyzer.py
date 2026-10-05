"""
Detailed policy analyzer - pinpoints exact errors and recommendations
"""

from typing import List, Dict, Tuple
import re

class PolicyIssue:
    """Represents a specific issue in the policy"""
    def __init__(self, control: str, severity: str, missing_element: str,
                 recommendation: str, example: str, why_it_matters: str):
        self.control = control
        self.severity = severity  # CRITICAL, HIGH, MEDIUM
        self.missing_element = missing_element
        self.recommendation = recommendation
        self.example = example
        self.why_it_matters = why_it_matters

class DetailedPolicyAnalyzer:
    """Analyzes policy text and provides detailed, actionable feedback"""

    def __init__(self):
        # Define what MUST be present for each GDPR control
        self.gdpr_requirements = {
            "data_minimization": {
                "name": "Data Minimization (GDPR Article 5(1)(c))",
                "must_have": [
                    "explicit statement about collecting only necessary data",
                    "purpose-specific data collection limits",
                    "explanation of what data is NOT collected"
                ],
                "keywords": ["minimal", "only necessary", "limited to", "adequate, relevant and limited"],
                "example": "We only collect information that is necessary for the specific purpose of processing your application. We do not collect excessive or irrelevant data.",
                "why": "GDPR requires that personal data must be adequate, relevant and limited to what is necessary. Without this, you're at risk of collecting excessive data and facing penalties."
            },
            "purpose_limitation": {
                "name": "Purpose Limitation (GDPR Article 5(1)(b))",
                "must_have": [
                    "clear statement of specific purposes for data collection",
                    "commitment not to use data for other purposes",
                    "explanation of each processing purpose"
                ],
                "keywords": ["specific purpose", "explicit purpose", "legitimate purposes", "not use for other"],
                "example": "We collect your email address for the sole purpose of sending admission notifications. We will not use your email for marketing or share it with third parties without your consent.",
                "why": "Data must only be used for the specific purpose it was collected for. Using data for secondary purposes without consent violates GDPR Article 5(1)(b)."
            },
            "storage_limitation": {
                "name": "Storage Limitation (GDPR Article 5(1)(e))",
                "must_have": [
                    "specific retention periods for different data types",
                    "deletion policy after purpose is fulfilled",
                    "explanation of when data will be removed"
                ],
                "keywords": ["retention period", "delete after", "keep for", "no longer necessary", "retention policy"],
                "example": "We will retain your application data for 2 years after the admission cycle. After this period, your data will be securely deleted unless you have enrolled as a student.",
                "why": "GDPR requires data to be kept no longer than necessary. Without clear retention periods, you risk indefinite storage which violates Article 5(1)(e) and opens liability."
            },
            "accuracy": {
                "name": "Accuracy (GDPR Article 5(1)(d))",
                "must_have": [
                    "commitment to maintain accurate data",
                    "process for users to update their information",
                    "regular data accuracy reviews"
                ],
                "keywords": ["accurate", "up to date", "update your information", "correct inaccurate", "verify"],
                "example": "We take steps to ensure your personal data is accurate and up-to-date. You can update your information at any time by logging into your account or contacting us at privacy@saveetha.ac.in.",
                "why": "Inaccurate data can harm individuals and lead to wrong decisions. GDPR mandates keeping data accurate and providing correction mechanisms."
            },
            "integrity_confidentiality": {
                "name": "Integrity & Confidentiality (GDPR Article 5(1)(f))",
                "must_have": [
                    "specific security measures described",
                    "encryption methods mentioned",
                    "organizational safeguards explained"
                ],
                "keywords": ["encryption", "security measures", "protect your data", "technical and organizational measures", "secure"],
                "example": "We protect your personal data using industry-standard encryption (TLS 1.3). Our servers are secured with firewalls, access controls, and regular security audits. Only authorized personnel can access your data.",
                "why": "GDPR requires appropriate technical and organizational measures. Vague statements like 'we keep data secure' are insufficient and expose you to breach liability."
            },
            "lawfulness": {
                "name": "Lawfulness of Processing (GDPR Article 6)",
                "must_have": [
                    "explicit legal basis for each processing activity",
                    "reference to GDPR Article 6 lawful bases",
                    "explanation of legitimate interest (if used)"
                ],
                "keywords": ["legal basis", "lawful basis", "legitimate interest", "contractual necessity", "Article 6"],
                "example": "We process your personal data based on the following legal grounds: (1) Your consent when you submit the registration form (Article 6(1)(a)), (2) Contractual necessity for admission processing (Article 6(1)(b)), and (3) Legal obligation to maintain academic records (Article 6(1)(c)).",
                "why": "Every processing activity needs a valid legal basis under GDPR Article 6. Without explicit legal grounds, all data processing is unlawful and subject to fines up to €20 million."
            },
            "transparency": {
                "name": "Transparency (GDPR Article 12)",
                "must_have": [
                    "clear, plain language throughout",
                    "detailed explanation of what data is collected",
                    "explanation of how data is used"
                ],
                "keywords": ["transparent", "clear information", "explain how", "inform you", "what we collect"],
                "example": "When you register for counseling, we collect: your name, email address, phone number, academic marks, and preferred program. We use this information to: schedule your counseling session, evaluate your eligibility, and send you admission updates.",
                "why": "GDPR requires information to be provided in a concise, transparent, intelligible and easily accessible form. Vague policies lead to user mistrust and regulatory scrutiny."
            },
            "consent": {
                "name": "Consent (GDPR Article 7)",
                "must_have": [
                    "clear consent mechanism described",
                    "explanation of how to withdraw consent",
                    "granular consent options for different purposes"
                ],
                "keywords": ["your consent", "with your permission", "withdraw consent", "opt-in", "freely given"],
                "example": "When you register, we will ask for your explicit consent to: ☐ Process your admission application (required), ☐ Send marketing communications (optional). You can withdraw consent at any time by emailing privacy@saveetha.ac.in.",
                "why": "GDPR requires consent to be freely given, specific, informed and unambiguous. Pre-ticked boxes or bundled consent violates Article 7 and makes consent invalid."
            },
            "data_subject_rights": {
                "name": "Data Subject Rights (GDPR Articles 15-22)",
                "must_have": [
                    "explicit mention of all 8 GDPR rights",
                    "clear process to exercise each right",
                    "contact information for rights requests"
                ],
                "keywords": ["right to access", "right to rectification", "right to erasure", "right to object", "data portability"],
                "example": "You have the following rights: (1) Access - request a copy of your personal data, (2) Rectification - correct inaccurate data, (3) Erasure - request deletion (right to be forgotten), (4) Restriction - limit processing, (5) Portability - receive data in machine-readable format, (6) Object - object to processing, (7) Withdraw consent, (8) Lodge complaint with supervisory authority. To exercise any right, email privacy@saveetha.ac.in.",
                "why": "GDPR grants individuals 8 fundamental rights. Not informing users of these rights violates transparency obligations and prevents individuals from exercising their rights."
            },
            "dpo_contact": {
                "name": "Data Protection Officer (GDPR Article 37)",
                "must_have": [
                    "name or title of DPO or privacy contact",
                    "direct contact email for privacy matters",
                    "phone number or address for privacy inquiries"
                ],
                "keywords": ["data protection officer", "dpo", "privacy officer", "privacy@", "dpo@"],
                "example": "Our Data Protection Officer is Dr. Rajesh Kumar. For any privacy-related questions or to exercise your rights, contact: Email: dpo@saveetha.ac.in, Phone: +91-44-1234-5678, Address: Data Protection Officer, Saveetha Engineering College, Chennai - 602105.",
                "why": "GDPR requires organizations to provide easy contact with privacy responsible person. Without clear DPO contact, users cannot exercise rights or report concerns, violating Article 13."
            }
        }

    def analyze(self, policy_text: str, nlp_scores: Dict[str, float]) -> List[PolicyIssue]:
        """
        Perform detailed analysis and return specific issues with recommendations
        """
        issues = []

        if not policy_text or len(policy_text) < 500:
            issues.append(PolicyIssue(
                control="Overall Policy",
                severity="CRITICAL",
                missing_element="Privacy policy is too short or missing",
                recommendation="Create a comprehensive privacy policy of at least 2000 words covering all GDPR requirements. Use the examples below as a starting point.",
                example="A complete GDPR-compliant policy should include: Introduction, What data we collect, Why we collect it, Legal basis, How we use it, Who we share with, Retention periods, Security measures, Your rights, and Contact information.",
                why_it_matters="GDPR Article 13 requires you to provide detailed information to users. A minimal or missing policy exposes you to regulatory fines and user mistrust."
            ))
            return issues

        policy_lower = policy_text.lower()

        # Analyze each GDPR control
        for control_key, score in nlp_scores.items():
            if score < 0.6:  # Control is failing
                req = self.gdpr_requirements.get(control_key)
                if not req:
                    continue

                # Check which specific elements are missing
                missing_keywords = []
                for kw in req["keywords"]:
                    if kw not in policy_lower:
                        missing_keywords.append(kw)

                # Determine severity
                if score < 0.2:
                    severity = "CRITICAL"
                elif score < 0.4:
                    severity = "HIGH"
                else:
                    severity = "MEDIUM"

                # Create detailed issue
                missing_text = ", ".join(req["must_have"])

                issues.append(PolicyIssue(
                    control=req["name"],
                    severity=severity,
                    missing_element=missing_text,
                    recommendation=f"Add a dedicated section titled '{req['name']}' with the following information: {missing_text}",
                    example=req["example"],
                    why_it_matters=req["why"]
                ))

        # Check for specific problematic phrases
        issues.extend(self._check_problematic_phrases(policy_text))

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
        issues.sort(key=lambda x: severity_order.get(x.severity, 99))

        return issues

    def _check_problematic_phrases(self, policy_text: str) -> List[PolicyIssue]:
        """Check for specific problematic phrases that violate GDPR"""
        issues = []
        policy_lower = policy_text.lower()

        # Check for DND override statement (common Indian privacy policy issue)
        if "dnd" in policy_lower and "activated" in policy_lower:
            # Find the exact text
            match = re.search(r'.{0,100}dnd.{0,100}', policy_lower)
            if match:
                problematic_text = match.group(0)
                issues.append(PolicyIssue(
                    control="Consent Violation",
                    severity="CRITICAL",
                    missing_element=f"Problematic statement found: '{problematic_text.strip()}'",
                    recommendation="REMOVE the statement about overriding DND (Do Not Disturb) registration. Replace with: 'We will only contact you if you have explicitly opted-in to receive communications. You can unsubscribe at any time.'",
                    example="We respect your communication preferences. You can choose to receive: ☐ Admission updates (opt-in required), ☐ Event notifications (opt-in required). We will not contact you unless you have provided explicit consent.",
                    why_it_matters="Stating you will contact users 'even if DND is activated' violates GDPR consent requirements (Article 7). Consent must be freely given - ignoring user's DND preference makes consent invalid and exposes you to telemarketing regulation violations."
                ))

        # Check for vague security language
        if "collect data" in policy_lower and "encryption" not in policy_lower:
            issues.append(PolicyIssue(
                control="Security Measures",
                severity="HIGH",
                missing_element="Vague security statements - no specific technical measures mentioned",
                recommendation="Add specific security measures: encryption methods (TLS, AES-256), access controls, authentication, security audits, incident response procedures.",
                example="We implement the following security measures: (1) TLS 1.3 encryption for data transmission, (2) AES-256 encryption for data at rest, (3) Multi-factor authentication for staff access, (4) Regular security audits and penetration testing, (5) 24/7 security monitoring, (6) Incident response plan with 72-hour breach notification.",
                why_it_matters="GDPR Article 32 requires 'appropriate technical and organizational measures'. Vague statements like 'we keep data secure' are insufficient and won't protect you in case of a data breach investigation."
            ))

        # Check for third-party sharing without details
        if ("third party" in policy_lower or "share" in policy_lower) and "processor agreement" not in policy_lower:
            issues.append(PolicyIssue(
                control="Third-Party Data Sharing",
                severity="HIGH",
                missing_element="No explanation of data processor agreements or safeguards",
                recommendation="Specify: (1) Which third parties receive data, (2) What data is shared, (3) Purpose of sharing, (4) Legal basis, (5) Data processing agreements in place, (6) User rights regarding third parties.",
                example="We share your data with the following third parties under GDPR-compliant data processing agreements: (1) Hosting Provider: Amazon Web Services (data storage), (2) Email Service: SendGrid (admission notifications), (3) Analytics: Google Analytics (website usage - anonymized). All third parties are bound by GDPR Article 28 processor agreements.",
                why_it_matters="GDPR Article 28 requires written contracts with data processors. Without documenting processor agreements and specifying safeguards, you're jointly liable for any processor's data breach or misuse."
            ))

        return issues
