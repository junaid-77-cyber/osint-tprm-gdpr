import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from osint.collector import OSINTCollector
from analysis.nlp_classifier import NLPClassifier
from analysis.risk_scorer import RiskScorer
import json

# Page configuration
st.set_page_config(
    page_title="OSINT TPRM - GDPR Compliance",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-medium {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔍 OSINT TPRM</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">GDPR Compliance Assessment using OSINT & Explainable AI</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    domain = st.text_input(
        "Enter Domain",
        placeholder="example.com",
        help="Enter domain without http:// or https://"
    )

    st.markdown("---")

    with st.expander("📚 About"):
        st.markdown("""
        **OSINT TPRM** is an AI-powered third-party risk management tool that:

        - 🔍 Collects OSINT data (DNS, TLS, Breaches, Policy)
        - 🤖 Analyzes privacy policies with NLP
        - 📊 Calculates risk scores (0-100)
        - 📝 Provides explainable recommendations

        **Authors:** Junaid Sardar S, Janani G
        **Mentor:** Dr. J. Varalakshmi
        **Institution:** Saveetha Engineering College
        """)

    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. Enter a domain name (e.g., example.com)
        2. Click "Start Assessment"
        3. Wait for analysis to complete (~30-60 seconds)
        4. Review risk score and recommendations
        5. Download report as JSON

        **Note:** Requires HaveIBeenPwned API key in .env file
        """)

    st.markdown("---")
    st.caption("v1.0.0 | MIT License")

# Main content
if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
    if not domain:
        st.error("Please enter a domain name")
    else:
        # Validate domain
        if '/' in domain or ' ' in domain:
            st.error("Please enter just the domain (e.g., example.com)")
        else:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Phase 1: OSINT Collection
                status_text.text("Phase 1/5: Collecting OSINT data...")
                progress_bar.progress(10)

                collector = OSINTCollector()
                osint_report = collector.collect(domain)
                progress_bar.progress(35)

                # Phase 2: NLP Analysis
                status_text.text("Phase 2/5: Analyzing privacy policy with NLP...")
                progress_bar.progress(40)

                classifier = NLPClassifier()
                if osint_report.policy.found:
                    gdpr_scores = classifier.classify(osint_report.policy.text)
                else:
                    # No policy found - all scores = 0
                    gdpr_scores = {k: 0.0 for k in classifier.keywords.keys()}
                progress_bar.progress(60)

                # Phase 3: Risk Scoring
                status_text.text("Phase 3/5: Calculating risk score...")
                progress_bar.progress(70)

                scorer = RiskScorer()
                risk_score = scorer.calculate_risk(gdpr_scores, osint_report)
                progress_bar.progress(85)

                # Phase 4: Generate visualizations
                status_text.text("Phase 4/5: Generating visualizations...")
                progress_bar.progress(90)

                # Complete
                status_text.text("Phase 5/5: Complete!")
                progress_bar.progress(100)

                st.success(f"✅ Assessment complete for **{domain}**")

                # Display Results
                st.markdown("---")
                st.header("📊 Assessment Results")

                # Risk Score Section
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Overall Risk Score", f"{risk_score.overall_score}/100")

                with col2:
                    risk_class = f"risk-{risk_score.risk_level.lower()}"
                    st.markdown(
                        f'<div style="font-size: 2rem;" class="{risk_class}">{"🟢" if risk_score.risk_level == "LOW" else "🟡" if risk_score.risk_level == "MEDIUM" else "🔴"} {risk_score.risk_level}</div>',
                        unsafe_allow_html=True
                    )

                with col3:
                    st.metric(
                        "Compliant Controls",
                        f"{risk_score.compliant_controls}/{risk_score.total_controls}"
                    )

                with col4:
                    compliance_pct = (risk_score.compliant_controls / risk_score.total_controls) * 100
                    st.metric("Compliance Rate", f"{compliance_pct:.0f}%")

                # Gauge Chart
                st.subheader("🎯 Risk Score Gauge")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=risk_score.overall_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Score", 'font': {'size': 24}},
                    delta={'reference': 70, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 40], 'color': '#ffcccc'},
                            {'range': [40, 70], 'color': '#ffffcc'},
                            {'range': [70, 100], 'color': '#ccffcc'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)

                # GDPR Controls Radar Chart
                st.subheader("📡 GDPR Controls Compliance")

                categories = list(risk_score.gdpr_scores.keys())
                values = list(risk_score.gdpr_scores.values())

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=[c.replace('_', ' ').title() for c in categories],
                    fill='toself',
                    name='Compliance'
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=False,
                    height=500
                )
                st.plotly_chart(fig_radar, use_container_width=True)

                # GDPR Controls Table
                st.subheader("📋 Detailed GDPR Controls")
                gdpr_df = pd.DataFrame([
                    {
                        'Control': k.replace('_', ' ').title(),
                        'Confidence': f"{v:.2f}",
                        'Status': '✅ Compliant' if v >= 0.6 else '⚠️ Non-Compliant'
                    }
                    for k, v in risk_score.gdpr_scores.items()
                ])
                st.dataframe(gdpr_df, use_container_width=True)

                # OSINT Findings
                st.subheader("🔍 OSINT Findings")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "DNS Security",
                        f"{osint_report.dns.security_score:.0f}/100",
                        delta=None
                    )
                    st.caption(osint_report.dns.details)

                with col2:
                    st.metric(
                        "TLS/SSL",
                        f"{osint_report.tls.security_score:.0f}/100",
                        delta=None
                    )
                    st.caption(osint_report.tls.details)

                with col3:
                    st.metric(
                        "Breach Status",
                        f"{osint_report.breach.breach_count} Found",
                        delta=None
                    )
                    st.caption(osint_report.breach.details)

                with col4:
                    st.metric(
                        "Privacy Policy",
                        "Found" if osint_report.policy.found else "Not Found",
                        delta=None
                    )
                    if osint_report.policy.found:
                        st.caption(f"Readability: {osint_report.policy.readability_score:.1f}")

                # Recommendations
                st.subheader("💡 Recommendations")
                for i, rec in enumerate(risk_score.recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")

                # Download Report
                st.markdown("---")
                st.subheader("📥 Export Report")

                report_data = {
                    'domain': domain,
                    'assessment_date': pd.Timestamp.now().isoformat(),
                    'risk_score': risk_score.overall_score,
                    'risk_level': risk_score.risk_level,
                    'gdpr_scores': risk_score.gdpr_scores,
                    'osint_summary': risk_score.osint_summary,
                    'recommendations': risk_score.recommendations,
                    'osint_details': {
                        'dns': osint_report.dns.model_dump(),
                        'tls': osint_report.tls.model_dump(),
                        'breach': osint_report.breach.model_dump(),
                        'policy': {
                            'found': osint_report.policy.found,
                            'url': osint_report.policy.url,
                            'word_count': osint_report.policy.word_count,
                            'readability_score': osint_report.policy.readability_score
                        }
                    }
                }

                report_json = json.dumps(report_data, indent=2)

                st.download_button(
                    label="📄 Download JSON Report",
                    data=report_json,
                    file_name=f"osint_tprm_report_{domain}.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"❌ Error during assessment: {str(e)}")
                st.exception(e)

else:
    # Welcome screen
    st.info("👈 Enter a domain in the sidebar and click 'Start Assessment' to begin")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 OSINT Collection")
        st.markdown("""
        - DNS Security (SPF, DMARC)
        - TLS/SSL Certificate
        - Data Breach History
        - Privacy Policy Detection
        """)

    with col2:
        st.markdown("### 🤖 NLP Analysis")
        st.markdown("""
        - 10 GDPR Controls
        - Keyword Detection
        - Readability Scoring
        - Confidence Calculation
        """)

    with col3:
        st.markdown("### 📊 Risk Scoring")
        st.markdown("""
        - Weighted Aggregation
        - OSINT Penalties
        - Risk Level (LOW/MED/HIGH)
        - Actionable Recommendations
        """)

    st.markdown("---")

    # Sample domains
    st.subheader("💡 Try These Sample Domains")
    st.markdown("""
    - `google.com` - Large tech company
    - `github.com` - Developer platform
    - `stripe.com` - Payment processor
    - `shopify.com` - E-commerce platform
    """)
