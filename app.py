import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from osint.collector import OSINTCollector
from analysis.nlp_classifier import NLPClassifier
from analysis.risk_scorer import RiskScorer
import json
import time

# Page configuration
st.set_page_config(
    page_title="OSINT TPRM - GDPR Compliance Assessment",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Academic Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    * {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: #f5f7fa;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .sub-header {
        font-size: 1.1rem;
        color: #4a5568;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Professional Cards */
    .professional-card {
        background: white;
        border-radius: 4px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .feature-card {
        background: white;
        border-radius: 4px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        height: 100%;
        transition: box-shadow 0.2s ease;
    }

    .feature-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Buttons */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: background 0.2s ease;
        box-shadow: none;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
    }

    section[data-testid="stSidebar"] * {
        color: #2d3748;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background: white;
        border: 1px solid #cbd5e0;
        border-radius: 4px;
        padding: 0.75rem;
        color: #2d3748;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
    }

    [data-testid="stMetricLabel"] {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Risk Levels */
    .risk-high {
        color: #dc2626;
        font-weight: 700;
        font-size: 2rem;
    }

    .risk-medium {
        color: #ea580c;
        font-weight: 700;
        font-size: 2rem;
    }

    .risk-low {
        color: #16a34a;
        font-weight: 700;
        font-size: 2rem;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: #2563eb;
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #1a202c;
        font-weight: 700;
    }

    h2 {
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #4a5568;
        border-bottom: 2px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }

    /* Info boxes */
    .stAlert {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        border-radius: 4px;
    }

    /* Code blocks */
    code {
        background: #f1f5f9;
        color: #1e40af;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9em;
    }

    /* Captions */
    .stCaption {
        color: #64748b;
    }

    /* Success message */
    .success-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-left: 4px solid #16a34a;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #166534;
    }

    /* Recommendation box */
    .recommendation-box {
        background: #fffbeb;
        border: 1px solid #fde047;
        border-left: 4px solid #ea580c;
        border-radius: 4px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #1a202c;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("", ["Home", "Assessment", "Privacy Policy", "Terms & Conditions", "About"], label_visibility="collapsed")

    st.markdown("---")

    if page == "Assessment":
        st.markdown("### Configuration")
        domain = st.text_input(
            "Enter Domain",
            placeholder="example.com",
            help="Enter domain without protocol"
        )

    st.markdown("---")
    st.caption("OSINT TPRM v1.0.0")
    st.caption("Saveetha Engineering College")

# HOME PAGE
if page == "Home":
    st.markdown('<div class="main-header">OSINT TPRM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Automated GDPR compliance assessment through open-source intelligence analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main description
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        **Research-based compliance assessment tool**

        OSINT TPRM combines open-source intelligence gathering with natural language processing
        to evaluate GDPR compliance. Developed at Saveetha Engineering College as part of
        academic research in cybersecurity and privacy engineering.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Features
    st.markdown("## Core Capabilities")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">OSINT Collection</div>
            <div class="feature-desc">
                Automated gathering of DNS security records, TLS certificates,
                breach data, and privacy policy documents
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">NLP Analysis</div>
            <div class="feature-desc">
                Natural language processing for automated detection of GDPR
                control implementations across 10 regulatory requirements
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Risk Quantification</div>
            <div class="feature-desc">
                Weighted scoring algorithm producing 0-100 risk assessments
                with evidence-based penalty calculations
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">Technical Reporting</div>
            <div class="feature-desc">
                Structured recommendations with specific implementation
                steps and GDPR article references
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Technical Details
    st.markdown("## System Specifications")

    spec_col1, spec_col2 = st.columns(2)

    with spec_col1:
        st.markdown("""
        **Analysis Coverage**
        - 10 GDPR control categories
        - 4 OSINT data sources
        - 60+ keyword detection patterns
        - Multi-factor risk scoring
        """)

    with spec_col2:
        st.markdown("""
        **Technical Stack**
        - Python 3.11 + Streamlit
        - Scikit-learn (TF-IDF classification)
        - DNSPython, BeautifulSoup
        - Pydantic data validation
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Research Context
    st.markdown("## Research Project")
    st.markdown("""
    **Title:** Enhancing Third-Party Risk Management Through OSINT and Explainable Risk Scoring

    **Team:** Junaid Sardar S (212224100028), Janani G (212224100017)

    **Mentor:** Dr. J. Varalakshmi

    **Institution:** Saveetha Engineering College (Autonomous), Department of Computer Science and Engineering (Cybersecurity)

    **Status:** Academic research project with published methodology and results
    """)

# ASSESSMENT PAGE
elif page == "Assessment":
    st.markdown('<div class="main-header">GDPR Compliance Assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Automated evaluation based on OSINT data collection</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start Assessment", type="primary", use_container_width=True):
        if not domain:
            st.error("Please enter a domain name in the sidebar")
        elif '/' in domain or ' ' in domain:
            st.error("Please enter domain only (e.g., example.com)")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Phase 1
                status_text.markdown("**Phase 1/3:** Collecting OSINT data...")
                progress_bar.progress(10)
                time.sleep(0.3)

                collector = OSINTCollector()
                osint_report = collector.collect(domain)
                progress_bar.progress(40)

                # Phase 2
                status_text.markdown("**Phase 2/3:** Analyzing compliance indicators...")
                progress_bar.progress(50)
                time.sleep(0.3)

                classifier = NLPClassifier()
                if osint_report.policy.found:
                    gdpr_scores = classifier.classify(osint_report.policy.text)
                else:
                    gdpr_scores = {k: 0.0 for k in classifier.keywords.keys()}
                progress_bar.progress(70)

                # Phase 3
                status_text.markdown("**Phase 3/3:** Computing risk assessment...")
                progress_bar.progress(80)
                time.sleep(0.3)

                scorer = RiskScorer()
                risk_score = scorer.calculate_risk(gdpr_scores, osint_report)
                progress_bar.progress(100)

                progress_bar.empty()
                status_text.empty()

                # Success
                st.markdown(f"""
                <div class="success-box">
                    Assessment completed for <strong>{domain}</strong>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("## Results")

                # Metrics
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric("Risk Score", f"{risk_score.overall_score}/100")

                with m2:
                    risk_class = f"risk-{risk_score.risk_level.lower()}"
                    st.markdown(f'<div class="{risk_class}">{risk_score.risk_level}</div>', unsafe_allow_html=True)

                with m3:
                    st.metric("Compliant Controls", f"{risk_score.compliant_controls}/{risk_score.total_controls}")

                with m4:
                    compliance_pct = (risk_score.compliant_controls / risk_score.total_controls) * 100
                    st.metric("Compliance Rate", f"{compliance_pct:.0f}%")

                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Risk Analysis", "GDPR Controls", "OSINT Data", "Recommendations"])

                with tab1:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=risk_score.overall_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Risk Score", 'font': {'size': 24, 'color': '#1a202c'}},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#2563eb"},
                            'steps': [
                                {'range': [0, 40], 'color': '#fee2e2'},
                                {'range': [40, 70], 'color': '#ffedd5'},
                                {'range': [70, 100], 'color': '#dcfce7'}
                            ],
                            'threshold': {
                                'line': {'color': "#dc2626", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=350, font={'color': "#1a202c"})
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with tab2:
                    categories = [c.replace('_', ' ').title() for c in risk_score.gdpr_scores.keys()]
                    values = list(risk_score.gdpr_scores.values())

                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        line=dict(color='#2563eb', width=2),
                        fillcolor='rgba(37, 99, 235, 0.1)'
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        height=500
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    gdpr_df = pd.DataFrame([
                        {
                            'Control': k.replace('_', ' ').title(),
                            'Confidence': f"{v:.2f}",
                            'Status': 'Compliant' if v >= 0.6 else 'Non-Compliant',
                            'Score': f"{int(v*100)}%"
                        }
                        for k, v in risk_score.gdpr_scores.items()
                    ])
                    st.dataframe(gdpr_df, use_container_width=True, hide_index=True)

                with tab3:
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("**DNS Security**")
                        st.metric("Score", f"{osint_report.dns.security_score:.0f}/100")
                        st.caption(osint_report.dns.details)

                        st.markdown("**TLS Certificate**")
                        st.metric("Score", f"{osint_report.tls.security_score:.0f}/100")
                        st.caption(osint_report.tls.details)

                    with c2:
                        st.markdown("**Data Breaches**")
                        st.metric("Count", f"{osint_report.breach.breach_count}")
                        st.caption(osint_report.breach.details)

                        st.markdown("**Privacy Policy**")
                        status = "Found" if osint_report.policy.found else "Not Found"
                        st.metric("Status", status)
                        if osint_report.policy.found:
                            st.caption(f"Readability: {osint_report.policy.readability_score:.1f}")

                with tab4:
                    for i, rec in enumerate(risk_score.recommendations, 1):
                        st.markdown(f"""
                        <div class="recommendation-box">
                            <strong>{i}.</strong> {rec}
                        </div>
                        """, unsafe_allow_html=True)

                # Export
                st.markdown("---")
                report_data = {
                    'domain': domain,
                    'assessment_date': pd.Timestamp.now().isoformat(),
                    'risk_score': risk_score.overall_score,
                    'risk_level': risk_score.risk_level,
                    'gdpr_scores': risk_score.gdpr_scores,
                    'recommendations': risk_score.recommendations
                }

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="Download Assessment Report (JSON)",
                        data=json.dumps(report_data, indent=2),
                        file_name=f"assessment_{domain}_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                with st.expander("Details"):
                    st.exception(e)

    else:
        st.info("Enter a domain in the sidebar and click Start Assessment")

# PRIVACY POLICY PAGE
elif page == "Privacy Policy":
    st.markdown('<div class="main-header">Privacy Policy</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Data handling and privacy practices</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Effective Date:** October 5, 2026

    ## 1. Introduction

    OSINT TPRM is an academic research tool developed at Saveetha Engineering College.
    This policy explains our data handling practices.

    ## 2. Data Collection

    **Information Processed:**
    - Domain names submitted for assessment
    - Publicly available OSINT data (DNS records, TLS certificates, breach data, privacy policies)

    **Information NOT Collected:**
    - Personal identification information
    - User account data
    - Browsing history
    - Financial information
    - Authentication credentials

    ## 3. Data Usage

    Data is processed solely for:
    - Performing GDPR compliance assessments
    - Generating risk analysis reports
    - Academic research purposes

    ## 4. Data Storage

    - Session data only - No persistent database
    - Results cleared when browser session ends
    - No long-term data retention
    - All processing occurs locally

    ## 5. Data Security

    - HTTPS/TLS encryption for all connections
    - API keys stored locally in environment variables
    - No third-party data sharing or sales
    - Open-source codebase allows security audits

    ## 6. Third-Party Services

    **HaveIBeenPwned API:**
    - Purpose: Public breach data lookup
    - Data shared: Domain names only
    - Privacy policy: https://haveibeenpwned.com/Privacy

    **Public DNS Servers:**
    - Purpose: DNS record queries
    - Data shared: Domain names only

    ## 7. User Rights (GDPR Compliance)

    You have the right to:
    - Access information about data processing
    - Request data deletion
    - Object to processing
    - Data portability
    - Lodge complaints with supervisory authorities

    ## 8. Academic Use

    This tool is part of academic research at:

    **Saveetha Engineering College (Autonomous)**
    Department of Computer Science and Engineering (Cybersecurity)
    Chennai - 602105, Tamil Nadu, India

    Research Team:
    - Junaid Sardar S (212224100028)
    - Janani G (212224100017)
    - Mentor: Dr. J. Varalakshmi

    ## 9. Contact

    **Email:** junaid.sardar@saveetha.ac.in
    **Institution:** Saveetha Engineering College
    **Location:** Chennai, Tamil Nadu, India

    ## 10. Changes to Policy

    Updates will be posted with revised effective dates. Continued use constitutes acceptance of changes.

    ## 11. Legal Basis

    Processing is based on:
    - User consent (domain submission)
    - Legitimate interests (academic research)
    - Compliance with legal obligations

    ---

    **Last Updated:** October 5, 2026
    **Version:** 1.0.0
    """)

# TERMS & CONDITIONS PAGE
elif page == "Terms & Conditions":
    st.markdown('<div class="main-header">Terms and Conditions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Terms of use for OSINT TPRM assessment tool</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Effective Date:** October 5, 2026

    ## 1. Acceptance of Terms

    By accessing and using OSINT TPRM, you accept and agree to be bound by these terms.

    ## 2. Academic Research Tool

    OSINT TPRM is an **academic research project** developed at Saveetha Engineering College
    for educational and research purposes in cybersecurity and privacy engineering.

    ## 3. Permitted Use

    **Authorized Uses:**
    - Academic research and education
    - GDPR compliance evaluation
    - Security assessment of domains you own or have permission to assess
    - Internal risk management processes

    **Prohibited Uses:**
    - Unauthorized assessment of third-party domains
    - Malicious scanning or reconnaissance
    - Automated bulk scanning
    - Commercial use without permission
    - Any illegal activities

    ## 4. Accuracy and Limitations

    **No Warranties:**
    - Results provided "as is" without warranties
    - Automated assessments may contain errors
    - Should not replace professional legal advice
    - Not a substitute for comprehensive compliance audits

    **Limitations:**
    - Based on publicly available information only
    - Cannot assess internal compliance practices
    - Results valid only at time of assessment
    - May not reflect complete compliance status

    ## 5. User Responsibilities

    You are responsible for:
    - Ensuring authorization to assess submitted domains
    - Verifying results independently
    - Complying with applicable laws and regulations
    - Protecting any API keys or credentials
    - Not misusing or abusing the service

    ## 6. Intellectual Property

    **Project Ownership:**
    - Developed by Junaid Sardar S and Janani G
    - Under mentorship of Dr. J. Varalakshmi
    - Property of Saveetha Engineering College

    **License:**
    - MIT License (for code repository)
    - Academic use encouraged
    - Commercial use requires permission

    ## 7. Data and Privacy

    Refer to our Privacy Policy for detailed information on data handling practices.

    ## 8. Liability Limitations

    **Disclaimer:**
    - No liability for assessment accuracy
    - No liability for decisions based on results
    - No liability for indirect or consequential damages
    - Maximum liability limited to zero (free academic tool)

    ## 9. Service Availability

    - Service provided on best-effort basis
    - No guaranteed uptime or availability
    - May be modified or discontinued without notice
    - Academic project with limited support

    ## 10. Third-Party Services

    Use of third-party services (HaveIBeenPwned API, DNS servers) is subject to their respective terms.

    ## 11. Modifications

    These terms may be updated. Continued use after modifications constitutes acceptance.

    ## 12. Governing Law

    These terms are governed by the laws of India. Disputes subject to jurisdiction of
    Chennai, Tamil Nadu, India.

    ## 13. Academic Citations

    If using this tool in research or publications, please cite:

    *Junaid Sardar S., Janani G., "Enhancing Third-Party Risk Management Through OSINT
    and Explainable Risk Scoring," Saveetha Engineering College, 2026.*

    ## 14. Contact

    **Questions or concerns:**

    Email: junaid.sardar@saveetha.ac.in
    Institution: Saveetha Engineering College
    Address: Chennai - 602105, Tamil Nadu, India

    ## 15. Severability

    If any provision is found unenforceable, remaining provisions remain in effect.

    ---

    **Last Updated:** October 5, 2026
    **Version:** 1.0.0
    **Project:** OSINT TPRM (Third-Party Risk Management)
    """)

# ABOUT PAGE
elif page == "About":
    st.markdown('<div class="main-header">About OSINT TPRM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Academic research project in cybersecurity and privacy engineering</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ## Research Project

        OSINT TPRM (Open-Source Intelligence Third-Party Risk Management) is an academic
        research project focused on automating GDPR compliance assessment through
        open-source intelligence gathering and natural language processing.

        ### Objectives

        1. Automate manual GDPR compliance assessment processes
        2. Leverage publicly available data for risk evaluation
        3. Provide transparent, explainable assessment results
        4. Contribute to academic research in privacy engineering

        ### Technical Approach

        **Architecture:**
        - OSINT Collection Layer: DNS, TLS, breach data, privacy policies
        - NLP Analysis Layer: Keyword-based GDPR control detection
        - Risk Scoring Engine: Weighted calculation with evidence-based penalties
        - Reporting Layer: Structured recommendations with GDPR article references

        **Implementation:**
        - Python 3.11 with Streamlit framework
        - Scikit-learn for classification
        - Pydantic for data validation
        - Plotly for visualizations
        - Open-source codebase for transparency

        ### Research Contributions

        - Novel application of OSINT for compliance assessment
        - Automated NLP-based GDPR control detection
        - Evidence-based risk quantification methodology
        - Explainable assessment framework

        ### Dataset

        Training data: 20 privacy policies manually labeled across 10 GDPR control categories,
        covering technology, social media, finance, and e-commerce sectors.
        """)

    with col2:
        st.markdown("""
        ### Team

        **Students:**
        - Junaid Sardar S
          Register: 212224100028
        - Janani G
          Register: 212224100017

        **Team Number:** 94

        **Mentor:**
        - Dr. J. Varalakshmi

        **Institution:**
        - Saveetha Engineering College (Autonomous)
        - Department of CSE (Cybersecurity)
        - Chennai - 602105
        - Tamil Nadu, India

        ---

        ### Contact

        **Email:**
        junaid.sardar@saveetha.ac.in

        **Repository:**
        github.com/junaid-77-cyber/osint-tprm-gdpr

        **License:**
        MIT License

        ---

        ### Version

        **Current:** 1.0.0
        **Released:** October 2026
        **Status:** Active Research
        """)

    st.markdown("---")

    st.markdown("""
    ## Technical Specifications

    **Code Statistics:**
    - Total lines: 2000+
    - Python modules: 17
    - Core components: 4 layers
    - Test coverage: Manual validation
    - Documentation: Comprehensive

    **Performance:**
    - Average assessment time: 30-60 seconds
    - OSINT collection: 20-40 seconds
    - NLP analysis: 5-10 seconds
    - Risk calculation: <1 second

    **Supported Assessments:**
    - GDPR compliance evaluation
    - 10 regulatory control categories
    - Evidence-based risk scoring (0-100 scale)
    - Structured recommendation generation
    """)

    st.markdown("---")

    st.markdown("""
    ## Acknowledgments

    We thank:
    - Dr. J. Varalakshmi for guidance and mentorship
    - Saveetha Engineering College for research support
    - Open-source community for tools and libraries
    - HaveIBeenPwned for breach data API access

    ---

    **Saveetha Engineering College (Autonomous)**
    Department of Computer Science and Engineering (Cybersecurity)
    Academic Year 2026-2027
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem 0;">
    <p style="margin: 0;">OSINT TPRM v1.0.0 | MIT License</p>
    <p style="margin: 0;">Saveetha Engineering College (Autonomous) | Department of CSE (Cybersecurity)</p>
    <p style="margin: 0;">Junaid Sardar S | Janani G | Mentor: Dr. J. Varalakshmi</p>
</div>
""", unsafe_allow_html=True)
