import json
from typing import Dict, List
from models.osint_report import OSINTReport
from models.risk_score import RiskScore

class RiskScorer:
    """Calculate overall risk score"""

    def __init__(self, config_path: str = 'config/gdpr_controls.json'):
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.weights = {k: v['weight'] for k, v in config['controls'].items()}

    def calculate_risk(
        self,
        gdpr_scores: Dict[str, float],
        osint_report: OSINTReport
    ) -> RiskScore:
        """Calculate overall risk score"""

        # Calculate base GDPR compliance score
        gdpr_score = 0.0
        compliant_count = 0

        for control, confidence in gdpr_scores.items():
            weight = self.weights.get(control, 0.1)
            gdpr_score += confidence * weight * 100

            if confidence >= 0.6:  # Threshold for compliance
                compliant_count += 1

        # Apply OSINT penalties
        penalties = 0.0

        # Breach penalty
        if osint_report.breach.has_breaches:
            penalties += 20

        # TLS penalty
        if not osint_report.tls.is_secure:
            penalties += 10

        # DNS penalty
        if osint_report.dns.security_score < 50:
            penalties += 5

        # Policy not found penalty
        if not osint_report.policy.found:
            penalties += 15

        # Final score (0-100)
        final_score = max(0, gdpr_score - penalties)

        # Determine risk level
        if final_score >= 70:
            risk_level = "LOW"
        elif final_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            gdpr_scores, osint_report
        )

        # Generate OSINT summary
        osint_summary = self._generate_osint_summary(osint_report)

        return RiskScore(
            overall_score=round(final_score, 1),
            risk_level=risk_level,
            gdpr_scores=gdpr_scores,
            recommendations=recommendations,
            osint_summary=osint_summary,
            compliant_controls=compliant_count,
            total_controls=len(gdpr_scores)
        )

    def _generate_recommendations(
        self,
        gdpr_scores: Dict[str, float],
        osint_report: OSINTReport
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # GDPR control recommendations
        for control, score in gdpr_scores.items():
            if score < 0.6:
                control_name = control.replace('_', ' ').title()
                recommendations.append(
                    f"⚠️ {control_name}: Policy lacks clear {control_name.lower()} provisions. "
                    "Add explicit statements addressing this GDPR requirement."
                )

        # OSINT recommendations
        if osint_report.breach.has_breaches:
            recommendations.append(
                f"🚨 Security Alert: {osint_report.breach.breach_count} data breach(es) found. "
                "Review security practices and notify affected users."
            )

        if not osint_report.tls.is_secure:
            recommendations.append(
                "🔒 TLS/SSL Issue: Certificate may be expired or using outdated protocol. "
                "Update to TLS 1.2+ and renew certificates."
            )

        if osint_report.dns.security_score < 50:
            recommendations.append(
                "📧 Email Security: Missing SPF/DMARC records. "
                "Configure email authentication to prevent spoofing."
            )

        if not osint_report.policy.found:
            recommendations.append(
                "📄 Privacy Policy Missing: No privacy policy detected. "
                "Create and publish a comprehensive GDPR-compliant privacy policy."
            )

        if not recommendations:
            recommendations.append("✅ No major issues detected. Continue monitoring compliance.")

        return recommendations[:10]  # Limit to top 10

    def _generate_osint_summary(self, osint_report: OSINTReport) -> str:
        """Generate OSINT findings summary"""
        parts = []

        parts.append(f"DNS Security: {osint_report.dns.details}")
        parts.append(f"TLS/SSL: {osint_report.tls.details}")
        parts.append(f"Breaches: {osint_report.breach.details}")
        parts.append(f"Policy: {osint_report.policy.details}")

        return " | ".join(parts)
