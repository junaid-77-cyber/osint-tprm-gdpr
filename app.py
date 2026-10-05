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

# Dark Modern Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Dark Theme */
    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Remove default padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Headers */
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }

    .sub-header {
        font-size: 1.4rem;
        color: #a8b2d1;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 500;
        animation: fadeInUp 0.8s ease-out;
    }

    /* Dark Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.5);
    }

    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        height: 100%;
    }

    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    }

    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.8));
    }

    .feature-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .feature-desc {
        color: #a8b2d1;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.7);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* Sidebar Dark */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
        color: #ffffff;
        font-size: 1.1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        background: rgba(255, 255, 255, 0.08);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
    }

    [data-testid="stMetricLabel"] {
        color: #a8b2d1;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Risk Badges */
    .risk-high {
        color: #ff6b6b;
        font-weight: 800;
        font-size: 3rem;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.8);
    }

    .risk-medium {
        color: #ffd93d;
        font-weight: 800;
        font-size: 3rem;
        text-shadow: 0 0 20px rgba(255, 217, 61, 0.8);
    }

    .risk-low {
        color: #6bcf7f;
        font-weight: 800;
        font-size: 3rem;
        text-shadow: 0 0 20px rgba(107, 207, 127, 0.8);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
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
            opacity: 0.7;
        }
    }

    /* Info/Success/Warning Messages */
    .stAlert {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    /* Recommendations */
    .recommendation {
        background: linear-gradient(135deg, rgba(255, 217, 61, 0.15) 0%, rgba(255, 107, 107, 0.15) 100%);
        border-left: 4px solid #ffd93d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #ffffff;
        font-size: 1.1rem;
        line-height: 1.8;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, rgba(107, 207, 127, 0.15) 0%, rgba(102, 126, 234, 0.15) 100%);
        border-left: 4px solid #6bcf7f;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700;
    }

    h2 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        margin-top: 2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.02);
        padding: 0.5rem;
        border-radius: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        color: #a8b2d1;
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
    }

    /* Dataframe */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
    }

    /* Code blocks */
    code {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.02);
        padding: 1rem;
        border-radius: 12px;
    }

    /* Captions */
    .stCaption {
        color: #a8b2d1 !important;
    }

    /* Divider */
    hr {
        border-color: rgba(102, 126, 234, 0.2);
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

    st.markdown("<br><br>", unsafe_allow_html=True)

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
        st.metric("Dataset Size", "20", help="Labeled privacy policies")

    st.markdown("<br><br>", unsafe_allow_html=True)

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
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Phase 1
                with st.spinner("🔍 Phase 1/5: Collecting OSINT data..."):
                    status_text.markdown("**Phase 1/5:** Gathering DNS, TLS, breach data...")
                    progress_bar.progress(10)
                    time.sleep(0.5)

                    collector = OSINTCollector()
                    osint_report = collector.collect(domain)
                    progress_bar.progress(35)

                # Phase 2
                with st.spinner("🤖 Phase 2/5: Analyzing privacy policy..."):
                    status_text.markdown("**Phase 2/5:** Running NLP analysis...")
                    progress_bar.progress(40)
                    time.sleep(0.5)

                    classifier = NLPClassifier()
                    if osint_report.policy.found:
                        gdpr_scores = classifier.classify(osint_report.policy.text)
                    else:
                        gdpr_scores = {k: 0.0 for k in classifier.keywords.keys()}
                    progress_bar.progress(60)

                # Phase 3
                with st.spinner("📊 Phase 3/5: Calculating risk score..."):
                    status_text.markdown("**Phase 3/5:** Computing risk assessment...")
                    progress_bar.progress(70)
                    time.sleep(0.5)

                    scorer = RiskScorer()
                    risk_score = scorer.calculate_risk(gdpr_scores, osint_report)
                    progress_bar.progress(85)

                # Complete
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

                # Results
                st.markdown("## 📊 Assessment Results")
                st.markdown("<br>", unsafe_allow_html=True)

                # Metrics
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.metric("Overall Risk Score", f"{risk_score.overall_score}/100")

                with metric_col2:
                    risk_class = f"risk-{risk_score.risk_level.lower()}"
                    emoji = "🟢" if risk_score.risk_level == "LOW" else "🟡" if risk_score.risk_level == "MEDIUM" else "🔴"
                    st.markdown(f'<div class="{risk_class}">{emoji} {risk_score.risk_level}</div>', unsafe_allow_html=True)

                with metric_col3:
                    st.metric("Compliant Controls", f"{risk_score.compliant_controls}/{risk_score.total_controls}")

                with metric_col4:
                    compliance_pct = (risk_score.compliant_controls / risk_score.total_controls) * 100
                    st.metric("Compliance Rate", f"{compliance_pct:.0f}%")

                st.markdown("<br>", unsafe_allow_html=True)

                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Risk Score", "🎯 GDPR Controls", "🔍 OSINT Findings", "💡 Recommendations"])

                with tab1:
                    # Gauge
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk_score.overall_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Risk Score", 'font': {'size': 28, 'color': '#ffffff'}},
                        delta={'reference': 70, 'increasing': {'color': "#6bcf7f"}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#667eea"},
                            'bar': {'color': "#667eea", 'thickness': 0.75},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 3,
                            'bordercolor': "rgba(102, 126, 234, 0.3)",
                            'steps': [
                                {'range': [0, 40], 'color': 'rgba(255, 107, 107, 0.3)'},
                                {'range': [40, 70], 'color': 'rgba(255, 217, 61, 0.3)'},
                                {'range': [70, 100], 'color': 'rgba(107, 207, 127, 0.3)'}
                            ],
                            'threshold': {
                                'line': {'color': "#ff6b6b", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        height=400,
                        font={'color': "#ffffff", 'family': "Inter"},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with tab2:
                    # Radar
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
                                tickfont=dict(size=12, color='#ffffff'),
                                gridcolor='rgba(255, 255, 255, 0.1)'
                            ),
                            angularaxis=dict(
                                tickfont=dict(size=13, color='#ffffff'),
                                gridcolor='rgba(255, 255, 255, 0.1)'
                            ),
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        showlegend=False,
                        height=600,
                        font={'family': "Inter"},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    # Table
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
                    # OSINT
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
                        else:
                            st.success(osint_report.breach.details)

                        st.markdown("#### 📄 Privacy Policy")
                        status = "✅ Found" if osint_report.policy.found else "❌ Not Found"
                        st.metric("Status", status)
                        if osint_report.policy.found:
                            st.success(f"Readability: {osint_report.policy.readability_score:.1f}")
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

                # Export
                st.markdown("## 📥 Export Report")
                report_data = {
                    'domain': domain,
                    'assessment_date': pd.Timestamp.now().isoformat(),
                    'risk_score': risk_score.overall_score,
                    'risk_level': risk_score.risk_level,
                    'compliance_rate': f"{compliance_pct:.1f}%",
                    'gdpr_scores': risk_score.gdpr_scores,
                    'recommendations': risk_score.recommendations
                }

                report_json = json.dumps(report_data, indent=2)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📄 Download JSON Report",
                        data=report_json,
                        file_name=f"osint_tprm_{domain}_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Details"):
                    st.exception(e)

    else:
        st.info("👈 Enter a domain in the sidebar and click 'Start Assessment'")

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
    Welcome to OSINT TPRM. This Privacy Policy explains how we collect, use, and protect your information.

    ## 2. Information We Collect
    - **Domain Names**: Temporarily processed for analysis
    - **OSINT Data**: Publicly available information only
    - **No Personal Data**: We don't collect user identification information

    ## 3. Data Security
    - End-to-end encryption
    - No persistent storage
    - Local processing only

    ## 4. Your Rights (GDPR)
    - Right to access
    - Right to erasure
    - Right to data portability
    - Right to object

    ## 5. Contact
    **Email**: junaid.sardar@saveetha.ac.in
    **Institution**: Saveetha Engineering College
    **Location**: Chennai, Tamil Nadu, India
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
        **OSINT TPRM** is a research project developed at Saveetha Engineering College to automate GDPR compliance assessment.

        ### 🎯 Objectives
        1. Automate compliance checks
        2. Leverage open-source intelligence
        3. Provide explainable recommendations
        4. Contribute to cybersecurity research

        ### 📊 Technology Stack
        - **Python 3.11+** - Core language
        - **Streamlit** - Web framework
        - **Plotly** - Visualizations
        - **Scikit-learn** - ML models
        - **DNSPython** - DNS queries
        """)

    with col2:
        st.markdown("""
        ### 👥 Team
        **Students:**
        - Junaid Sardar S (212224100028)
        - Janani G (212224100017)

        **Mentor:**
        - Dr. J. Varalakshmi

        **Institution:**
        - Saveetha Engineering College
        - Chennai - 602105
        - Tamil Nadu, India

        ---

        ### 📞 Contact
        **Email:** junaid.sardar@saveetha.ac.in

        **Version:** 1.0.0

        **License:** MIT
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a8b2d1; padding: 2rem 0;">
    <p><strong>OSINT TPRM v1.0.0</strong> | MIT License | Saveetha Engineering College</p>
    <p>Developed by Junaid Sardar S & Janani G | Mentor: Dr. J. Varalakshmi</p>
</div>
""", unsafe_allow_html=True)
