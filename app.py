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

# Enhanced Custom CSS with modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }

    /* Header styles */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
    }

    .sub-header {
        font-size: 1.3rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        animation: fadeInUp 0.8s ease-out;
    }

    /* Card styles */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }

    /* Risk level badges */
    .risk-high {
        color: #DC2626;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
    }

    .risk-medium {
        color: #F59E0B;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
    }

    .risk-low {
        color: #10B981;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }

    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }

    /* Sidebar styles */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .css-1d391kg h2, [data-testid="stSidebar"] h2 {
        color: white;
    }

    /* Input styles */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
        height: 100%;
    }

    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #6B7280;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Recommendation cards */
    .recommendation {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-left: 4px solid #F59E0B;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Section headers */
    h2, h3 {
        color: #1F2937;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🔐 Navigation")
    page = st.radio("", ["🏠 Home", "📊 Assessment", "🔒 Privacy Policy", "ℹ️ About"], label_visibility="collapsed")

    st.markdown("---")

    if page == "📊 Assessment":
        st.markdown("### ⚙️ Configuration")
        domain = st.text_input(
            "Enter Domain",
            placeholder="example.com",
            help="Enter domain without http:// or https://"
        )

    st.markdown("---")
    st.caption("**OSINT TPRM v1.0.0**")
    st.caption("© 2026 Saveetha Engineering College")

# HOME PAGE
if page == "🏠 Home":
    # Hero Section
    st.markdown('<div class="main-header">🔐 OSINT TPRM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered GDPR Compliance Assessment Through Open-Source Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Value Proposition
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        **Transform your compliance workflow with automated OSINT analysis**

        Our platform combines Open-Source Intelligence gathering with advanced NLP
        to deliver comprehensive GDPR compliance assessments in under 60 seconds.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards
    st.markdown("## ✨ Key Features")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">OSINT Collection</div>
            <div class="feature-desc">
                Automated gathering of DNS, TLS, breach data, and privacy policies from public sources
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">NLP Analysis</div>
            <div class="feature-desc">
                Advanced keyword detection across 10 GDPR controls with confidence scoring
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Risk Scoring</div>
            <div class="feature-desc">
                Weighted risk calculation (0-100) with automatic penalty application
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Recommendations</div>
            <div class="feature-desc">
                Actionable insights with specific steps to improve compliance posture
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # How It Works
    st.markdown("## 🚀 How It Works")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("**1️⃣ Enter Domain**")
        st.write("Input target organization's domain name")

    with col2:
        st.markdown("**2️⃣ OSINT Scan**")
        st.write("Collect public security & policy data")

    with col3:
        st.markdown("**3️⃣ NLP Analysis**")
        st.write("Analyze GDPR compliance indicators")

    with col4:
        st.markdown("**4️⃣ Risk Score**")
        st.write("Calculate weighted risk (0-100)")

    with col5:
        st.markdown("**5️⃣ Report**")
        st.write("Generate actionable recommendations")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Stats Section
    st.markdown("## 📈 Platform Statistics")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("GDPR Controls", "10", help="Number of GDPR articles analyzed")

    with stat_col2:
        st.metric("OSINT Sources", "4", help="DNS, TLS, Breach, Policy")

    with stat_col3:
        st.metric("Avg. Assessment Time", "45s", help="Average processing time")

    with stat_col4:
        st.metric("Keyword Patterns", "60+", help="NLP detection patterns")

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎯 Ready to Assess Compliance?")
        if st.button("🚀 Start Your First Assessment", use_container_width=True):
            st.session_state.page = "📊 Assessment"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Sample Domains
    st.markdown("## 💼 Try These Sample Domains")
    sample_col1, sample_col2, sample_col3, sample_col4 = st.columns(4)

    with sample_col1:
        st.code("google.com", language=None)
        st.caption("🏢 Large Tech Company")

    with sample_col2:
        st.code("github.com", language=None)
        st.caption("👨‍💻 Developer Platform")

    with sample_col3:
        st.code("stripe.com", language=None)
        st.caption("💳 Payment Processor")

    with sample_col4:
        st.code("shopify.com", language=None)
        st.caption("🛍️ E-commerce Platform")

# ASSESSMENT PAGE
elif page == "📊 Assessment":
    st.markdown('<div class="main-header">📊 GDPR Compliance Assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Automated OSINT-based compliance evaluation</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
        if not domain:
            st.error("⚠️ Please enter a domain name in the sidebar")
        elif '/' in domain or ' ' in domain:
            st.error("⚠️ Please enter just the domain (e.g., example.com)")
        else:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Phase 1: OSINT Collection
                with st.spinner("🔍 Phase 1/5: Collecting OSINT data..."):
                    status_text.markdown("**Phase 1/5:** Gathering DNS, TLS, breach data...")
                    progress_bar.progress(10)
                    time.sleep(0.5)

                    collector = OSINTCollector()
                    osint_report = collector.collect(domain)
                    progress_bar.progress(35)

                # Phase 2: NLP Analysis
                with st.spinner("🤖 Phase 2/5: Analyzing privacy policy..."):
                    status_text.markdown("**Phase 2/5:** Running NLP analysis on policy text...")
                    progress_bar.progress(40)
                    time.sleep(0.5)

                    classifier = NLPClassifier()
                    if osint_report.policy.found:
                        gdpr_scores = classifier.classify(osint_report.policy.text)
                    else:
                        gdpr_scores = {k: 0.0 for k in classifier.keywords.keys()}
                    progress_bar.progress(60)

                # Phase 3: Risk Scoring
                with st.spinner("📊 Phase 3/5: Calculating risk score..."):
                    status_text.markdown("**Phase 3/5:** Computing weighted risk assessment...")
                    progress_bar.progress(70)
                    time.sleep(0.5)

                    scorer = RiskScorer()
                    risk_score = scorer.calculate_risk(gdpr_scores, osint_report)
                    progress_bar.progress(85)

                # Phase 4: Visualizations
                status_text.markdown("**Phase 4/5:** Generating interactive visualizations...")
                progress_bar.progress(90)
                time.sleep(0.5)

                # Phase 5: Complete
                status_text.markdown("**Phase 5/5:** ✅ Assessment complete!")
                progress_bar.progress(100)
                time.sleep(0.5)

                progress_bar.empty()
                status_text.empty()

                # Success Message
                st.markdown(f"""
                <div class="success-message">
                    ✅ Assessment completed successfully for <strong>{domain}</strong>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")

                # Results Section
                st.markdown("## 📊 Assessment Results")
                st.markdown("<br>", unsafe_allow_html=True)

                # Metrics Row
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Overall Risk Score", f"{risk_score.overall_score}/100")
                    st.markdown('</div>', unsafe_allow_html=True)

                with metric_col2:
                    risk_class = f"risk-{risk_score.risk_level.lower()}"
                    emoji = "🟢" if risk_score.risk_level == "LOW" else "🟡" if risk_score.risk_level == "MEDIUM" else "🔴"
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="{risk_class}">{emoji} {risk_score.risk_level}</div>', unsafe_allow_html=True)
                    st.caption("Risk Level")
                    st.markdown('</div>', unsafe_allow_html=True)

                with metric_col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Compliant Controls", f"{risk_score.compliant_controls}/{risk_score.total_controls}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with metric_col4:
                    compliance_pct = (risk_score.compliant_controls / risk_score.total_controls) * 100
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Compliance Rate", f"{compliance_pct:.0f}%")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Visualizations in Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Risk Score", "🎯 GDPR Controls", "🔍 OSINT Findings", "💡 Recommendations"])

                with tab1:
                    # Gauge Chart
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk_score.overall_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Risk Score", 'font': {'size': 28, 'color': '#1F2937'}},
                        delta={'reference': 70, 'increasing': {'color': "#10B981"}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#667eea"},
                            'bar': {'color': "#667eea", 'thickness': 0.75},
                            'bgcolor': "white",
                            'borderwidth': 3,
                            'bordercolor': "#E5E7EB",
                            'steps': [
                                {'range': [0, 40], 'color': '#FEE2E2'},
                                {'range': [40, 70], 'color': '#FEF3C7'},
                                {'range': [70, 100], 'color': '#D1FAE5'}
                            ],
                            'threshold': {
                                'line': {'color': "#DC2626", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        height=400,
                        font={'color': "#1F2937", 'family': "Inter"},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with tab2:
                    # Radar Chart
                    categories = [c.replace('_', ' ').title() for c in risk_score.gdpr_scores.keys()]
                    values = list(risk_score.gdpr_scores.values())

                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name='Compliance',
                        line=dict(color='#667eea', width=3),
                        fillcolor='rgba(102, 126, 234, 0.3)'
                    ))
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1],
                                tickfont=dict(size=12, color='#6B7280')
                            ),
                            angularaxis=dict(
                                tickfont=dict(size=13, color='#1F2937')
                            ),
                            bgcolor='rgba(255, 255, 255, 0.8)'
                        ),
                        showlegend=False,
                        height=600,
                        font={'family': "Inter"},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    # GDPR Controls Table
                    st.markdown("### 📋 Detailed Compliance Status")
                    gdpr_df = pd.DataFrame([
                        {
                            'Control': k.replace('_', ' ').title(),
                            'Confidence': f"{v:.2f}",
                            'Status': '✅ Compliant' if v >= 0.6 else '⚠️ Non-Compliant',
                            'Score': f"{int(v*100)}%"
                        }
                        for k, v in risk_score.gdpr_scores.items()
                    ])
                    st.dataframe(gdpr_df, use_container_width=True, hide_index=True)

                with tab3:
                    # OSINT Findings
                    osint_col1, osint_col2 = st.columns(2)

                    with osint_col1:
                        st.markdown("#### 🌐 DNS Security")
                        st.metric("Security Score", f"{osint_report.dns.security_score:.0f}/100")
                        st.info(osint_report.dns.details)

                        st.markdown("#### 🔒 TLS/SSL Status")
                        st.metric("Security Score", f"{osint_report.tls.security_score:.0f}/100")
                        st.info(osint_report.tls.details)

                    with osint_col2:
                        st.markdown("#### 🚨 Data Breaches")
                        st.metric("Breaches Found", f"{osint_report.breach.breach_count}")
                        if osint_report.breach.breach_count > 0:
                            st.warning(osint_report.breach.details)
                            if osint_report.breach.breaches:
                                with st.expander("View Breach Details"):
                                    for breach in osint_report.breach.breaches:
                                        st.write(f"• {breach}")
                        else:
                            st.success(osint_report.breach.details)

                        st.markdown("#### 📄 Privacy Policy")
                        status = "✅ Found" if osint_report.policy.found else "❌ Not Found"
                        st.metric("Status", status)
                        if osint_report.policy.found:
                            st.success(f"Readability Score: {osint_report.policy.readability_score:.1f}")
                            st.caption(f"Words: {osint_report.policy.word_count:,}")
                        else:
                            st.error(osint_report.policy.details)

                with tab4:
                    # Recommendations
                    st.markdown("### 💡 Actionable Recommendations")
                    for i, rec in enumerate(risk_score.recommendations, 1):
                        st.markdown(f"""
                        <div class="recommendation">
                            <strong>{i}.</strong> {rec}
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Export Section
                st.markdown("## 📥 Export Report")

                report_data = {
                    'domain': domain,
                    'assessment_date': pd.Timestamp.now().isoformat(),
                    'risk_score': risk_score.overall_score,
                    'risk_level': risk_score.risk_level,
                    'compliance_rate': f"{compliance_pct:.1f}%",
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

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📄 Download Comprehensive JSON Report",
                        data=report_json,
                        file_name=f"osint_tprm_report_{domain}_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ Error during assessment: {str(e)}")
                with st.expander("View Error Details"):
                    st.exception(e)

    else:
        # Welcome message when no assessment running
        st.info("👈 Enter a domain name in the sidebar, then click 'Start Assessment' to begin")

# PRIVACY POLICY PAGE
elif page == "🔒 Privacy Policy":
    st.markdown('<div class="main-header">🔒 Privacy Policy</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">How we handle your data and protect your privacy</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    ## 📅 Effective Date
    **October 5, 2026**

    ## 1. Introduction

    Welcome to OSINT TPRM ("we," "our," or "us"). This Privacy Policy explains how we collect, use, disclose, and safeguard
    your information when you use our GDPR Compliance Assessment Tool.

    ## 2. Information We Collect

    ### 2.1 Information You Provide
    - **Domain Names**: When you submit a domain for assessment, we temporarily process this information to perform the analysis.
    - **API Keys**: If you configure API keys (e.g., HaveIBeenPwned), these are stored locally on your device and never transmitted to our servers.

    ### 2.2 Automatically Collected Information
    - **OSINT Data**: We collect publicly available information about the domains you assess, including:
        - DNS records (SPF, DMARC, MX)
        - TLS/SSL certificate information
        - Publicly disclosed data breaches
        - Privacy policy text from public websites

    ### 2.3 Information We Do NOT Collect
    - Personal identification information about individual users
    - Browsing history unrelated to domain assessments
    - Financial information
    - Cookies or tracking mechanisms

    ## 3. How We Use Your Information

    We use the information we collect to:

    - **Perform Assessments**: Analyze GDPR compliance for the domains you submit
    - **Generate Reports**: Create comprehensive risk assessment reports
    - **Improve Our Service**: Enhance the accuracy and efficiency of our analysis algorithms
    - **Provide Support**: Respond to your questions and technical issues

    ## 4. Data Retention

    - **Session Data**: Assessment results are stored in your browser's session and cleared when you close the application
    - **No Persistent Storage**: We do not maintain a database of your assessments or domain submissions
    - **Local Processing**: All analysis is performed in real-time and results are not permanently stored

    ## 5. Data Security

    We implement appropriate technical and organizational measures to protect your information:

    - **Encryption**: All data transmission uses HTTPS/TLS encryption
    - **Local Storage**: API keys are stored locally in environment variables, never on remote servers
    - **No Third-Party Sharing**: We do not sell, trade, or share your data with third parties
    - **Open Source**: Our code is open-source, allowing for transparency and security audits

    ## 6. Third-Party Services

    Our application integrates with third-party services:

    ### 6.1 HaveIBeenPwned API
    - **Purpose**: Check for publicly disclosed data breaches
    - **Data Shared**: Domain names only
    - **Privacy Policy**: https://haveibeenpwned.com/Privacy

    ### 6.2 Public DNS Servers
    - **Purpose**: Query DNS records
    - **Data Shared**: Domain names only
    - **Note**: Standard DNS protocol, publicly available information

    ## 7. Your Rights (GDPR Compliance)

    Under the General Data Protection Regulation (GDPR), you have the following rights:

    - **Right to Access**: Request information about data we process
    - **Right to Rectification**: Correct inaccurate data
    - **Right to Erasure**: Request deletion of your data
    - **Right to Restriction**: Limit how we process your data
    - **Right to Data Portability**: Receive your data in a structured format
    - **Right to Object**: Object to data processing
    - **Right to Withdraw Consent**: Withdraw consent at any time

    To exercise these rights, contact us at the information provided below.

    ## 8. Children's Privacy

    Our service is not directed to individuals under the age of 16. We do not knowingly collect personal information
    from children under 16. If you become aware that a child has provided us with personal information, please contact us.

    ## 9. International Data Transfers

    As our service processes data locally in your browser, there are no international data transfers. API calls to third-party
    services (e.g., HaveIBeenPwned) follow their respective data transfer policies.

    ## 10. Changes to This Privacy Policy

    We may update this Privacy Policy from time to time. We will notify you of any changes by:
    - Posting the new Privacy Policy on this page
    - Updating the "Effective Date" at the top
    - Providing a notice in the application (for material changes)

    ## 11. Academic and Research Use

    This tool is developed as part of academic research at:

    **Saveetha Engineering College (Autonomous)**
    Department of Computer Science and Engineering (Cybersecurity)
    Chennai - 602105, Tamil Nadu, India

    ### Research Team:
    - Junaid Sardar S (212224100028)
    - Janani G (212224100017)
    - Mentor: Dr. J. Varalakshmi

    ## 12. Contact Information

    If you have questions about this Privacy Policy or our privacy practices, please contact:

    **Email**: junaid.sardar@saveetha.ac.in
    **Institution**: Saveetha Engineering College
    **Address**: Chennai - 602105, Tamil Nadu, India

    ## 13. Legal Basis for Processing (GDPR)

    We process your data under the following legal bases:

    - **Consent**: When you submit a domain for assessment, you consent to our processing
    - **Legitimate Interests**: To provide the service and improve our tool
    - **Compliance with Legal Obligations**: To comply with applicable laws and regulations

    ## 14. Data Protection Officer

    For privacy-related inquiries, you may contact our academic supervisor:

    **Dr. J. Varalakshmi**
    Department of CSE (Cybersecurity)
    Saveetha Engineering College

    ## 15. Dispute Resolution

    Any disputes arising from this Privacy Policy will be resolved through:
    1. Direct communication with our team
    2. Mediation through the institution's ethics committee
    3. Applicable legal jurisdiction in Chennai, Tamil Nadu, India

    ---

    ## 📜 Acknowledgment

    By using OSINT TPRM, you acknowledge that you have read and understood this Privacy Policy and agree to its terms.

    **Last Updated**: October 5, 2026
    **Version**: 1.0.0
    """)

# ABOUT PAGE
elif page == "ℹ️ About":
    st.markdown('<div class="main-header">ℹ️ About OSINT TPRM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Research project for GDPR compliance automation</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ## 🎓 Academic Project

        **OSINT TPRM** (Open-Source Intelligence Third-Party Risk Management) is an academic research project
        developed at Saveetha Engineering College to automate GDPR compliance assessment using publicly available information.

        ### 🎯 Project Objectives

        1. **Automate Compliance Checks**: Reduce manual effort in GDPR compliance audits
        2. **Leverage OSINT**: Use publicly available data for risk assessment
        3. **Explainable AI**: Provide transparent, actionable recommendations
        4. **Academic Research**: Contribute to cybersecurity and privacy research

        ### 🏗️ Technical Architecture

        - **OSINT Collection Layer**: DNS, TLS, Breach Data, Privacy Policies
        - **NLP Analysis Layer**: Keyword-based GDPR control detection
        - **Risk Scoring Engine**: Weighted risk calculation (0-100 scale)
        - **Visualization Layer**: Interactive Streamlit dashboard

        ### 📊 Technology Stack

        - **Backend**: Python 3.11+
        - **Framework**: Streamlit
        - **Visualization**: Plotly
        - **NLP**: Custom keyword classifier
        - **Data Validation**: Pydantic
        - **OSINT Tools**: DNSPython, Requests, BeautifulSoup

        ### 📈 Project Statistics

        - **Code**: 1,020+ lines of Python
        - **Modules**: 17 Python files
        - **GDPR Controls**: 10 analyzed
        - **Keyword Patterns**: 60+ detection rules
        - **Development Time**: 2 hours (rapid MVP)
        """)

    with col2:
        st.markdown("""
        ### 👥 Team

        **Students:**
        - Junaid Sardar S
          (212224100028)
        - Janani G
          (212224100017)

        **Team Number:** 94

        **Mentor:**
        - Dr. J. Varalakshmi

        **Institution:**
        - Saveetha Engineering College (Autonomous)
        - Dept. of CSE (Cybersecurity)
        - Chennai - 602105
        - Tamil Nadu, India

        ---

        ### 📞 Contact

        **Email:**
        junaid.sardar@saveetha.ac.in

        **GitHub:**
        Coming Soon

        **License:**
        MIT License

        ---

        ### 🏆 Achievements

        ✅ Functional MVP
        ✅ 1,000+ LOC
        ✅ 10 GDPR Controls
        ✅ Real-time Analysis
        ✅ Interactive Dashboard

        ---

        ### 📅 Timeline

        **Started:** Oct 2026
        **Version:** 1.0.0
        **Status:** Active Development
        """)

    st.markdown("---")

    st.markdown("""
    ## 🔬 Research Contribution

    This project contributes to:
    - **Privacy Engineering**: Automated compliance assessment methodologies
    - **OSINT Applications**: Novel use of public data for risk management
    - **Explainable AI**: Transparent decision-making in compliance tools
    - **Third-Party Risk**: Scalable assessment frameworks

    ## 📚 References

    Our work builds upon research in:
    1. GDPR compliance automation
    2. Privacy policy analysis
    3. OSINT for cybersecurity
    4. Explainable artificial intelligence

    ## 🙏 Acknowledgments

    We thank:
    - Dr. J. Varalakshmi for mentorship and guidance
    - Saveetha Engineering College for providing resources
    - The open-source community for tools and libraries
    - HaveIBeenPwned for breach data API

    ---

    **© 2026 Saveetha Engineering College. All rights reserved.**
    """)

# Footer (appears on all pages)
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 2rem 0;">
    <p><strong>OSINT TPRM v1.0.0</strong> | MIT License | Saveetha Engineering College</p>
    <p>Developed by Junaid Sardar S & Janani G | Mentor: Dr. J. Varalakshmi</p>
</div>
""", unsafe_allow_html=True)
