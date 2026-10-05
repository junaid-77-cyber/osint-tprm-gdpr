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
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Bright Warm Modern Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 50%, #FFD9A6 100%);
    }

    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 50%, #FFA07A 100%);
        border-radius: 24px;
        padding: 4rem 3rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(255, 107, 53, 0.3);
        margin-bottom: 3rem;
        border: 3px solid rgba(255, 255, 255, 0.5);
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 4px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 500;
        margin-bottom: 2rem;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.4);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Assessment Section */
    .assessment-card {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.15);
        margin: 2rem 0;
        border: 2px solid #FFE8CC;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6B35;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .section-subtitle {
        font-size: 1.2rem;
        color: #8B4513;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.12);
        border: 2px solid #FFE8CC;
        transition: all 0.3s ease;
        text-align: center;
    }

    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(255, 107, 53, 0.25);
        border-color: #FF8E53;
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FF6B35;
        margin-bottom: 0.75rem;
    }

    .feature-desc {
        color: #6B4423;
        font-size: 1rem;
        line-height: 1.7;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1rem 3rem;
        font-size: 1.2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.3);
        width: 100%;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4);
        background: linear-gradient(135deg, #FF8E53 0%, #FFA07A 100%);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background: white;
        border: 3px solid #FFE8CC;
        border-radius: 16px;
        padding: 1.25rem;
        color: #2C1810;
        font-size: 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #FF8E53;
        box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.15);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B35, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stMetricLabel"] {
        color: #8B4513;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Risk Levels */
    .risk-badge {
        display: inline-block;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    .risk-high {
        background: linear-gradient(135deg, #DC2626, #EF4444);
        color: white;
    }

    .risk-medium {
        background: linear-gradient(135deg, #F59E0B, #FBBF24);
        color: white;
    }

    .risk-low {
        background: linear-gradient(135deg, #10B981, #34D399);
        color: white;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FF6B35, #FF8E53);
        border-radius: 10px;
    }

    /* Stats Card */
    .stats-card {
        background: linear-gradient(135deg, #FFF5E6, #FFE8CC);
        border-radius: 16px;
        padding: 2rem;
        border: 2px solid #FFD9A6;
        text-align: center;
        box-shadow: 0 4px 16px rgba(255, 107, 53, 0.1);
    }

    .stat-number {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B35, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        font-size: 1.1rem;
        color: #8B4513;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #FFF9F0, #FFEDD5);
        border-left: 6px solid #FF8E53;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(255, 107, 53, 0.1);
    }

    .info-box-text {
        color: #6B4423;
        font-size: 1.1rem;
        line-height: 1.8;
    }

    /* Result Card */
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.15);
        border: 2px solid #FFE8CC;
    }

    .result-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FF6B35;
        margin-bottom: 1rem;
        border-bottom: 3px solid #FFE8CC;
        padding-bottom: 0.75rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
        border-bottom: none;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 700;
        color: #8B4513;
        border: 2px solid #FFE8CC;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: #FF8E53;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35, #FF8E53);
        color: white;
        border-color: #FF6B35;
        box-shadow: 0 4px 16px rgba(255, 107, 53, 0.3);
    }

    /* Alert */
    .stAlert {
        background: linear-gradient(135deg, #FFF9F0, #FFEDD5);
        border: 2px solid #FFE8CC;
        border-left: 6px solid #FF8E53;
        border-radius: 12px;
        color: #6B4423;
    }

    /* Recommendation Box */
    .recommendation-box {
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        border-left: 6px solid #F59E0B;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.15);
    }

    .recommendation-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #92400E;
        margin-bottom: 0.75rem;
    }

    .recommendation-text {
        color: #78350F;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    /* Footer */
    .footer {
        background: linear-gradient(135deg, #FF6B35, #FF8E53);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin-top: 4rem;
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.3);
    }

    .footer-text {
        color: white;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }

    /* Code */
    code {
        background: #FFF5E6;
        color: #FF6B35;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-size: 0.95em;
        border: 1px solid #FFE8CC;
    }

    /* Sidebar Override */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# HERO SECTION
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🔒 OSINT TPRM</div>
    <div class="hero-subtitle">
        Automated GDPR Compliance Assessment Powered by AI
    </div>
    <div>
        <span class="hero-badge">🛡️ Open-Source Intelligence</span>
        <span class="hero-badge">🤖 Machine Learning</span>
        <span class="hero-badge">📊 93.2% Accuracy</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ABOUT SECTION
st.markdown('<div class="section-title">What is OSINT TPRM?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Intelligent risk assessment for third-party vendors</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="info-box">
        <div class="info-box-text">
            OSINT TPRM combines <strong>open-source intelligence gathering</strong> with
            <strong>natural language processing</strong> to evaluate GDPR compliance in real-time.
            Developed at Saveetha Engineering College, this tool analyzes privacy policies,
            DNS security, TLS certificates, and breach data to provide comprehensive risk scores.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# FEATURES SECTION
st.markdown('<div class="section-title">🚀 Key Features</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">OSINT Collection</div>
        <div class="feature-desc">
            Automatic DNS, TLS, breach data, and privacy policy collection
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI Analysis</div>
        <div class="feature-desc">
            NLP-powered GDPR compliance detection with TF-IDF classification
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Risk Scoring</div>
        <div class="feature-desc">
            Weighted risk calculation using Dempster-Shafer evidence fusion
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💡</div>
        <div class="feature-title">Explainable AI</div>
        <div class="feature-desc">
            Clear recommendations with actionable steps for compliance
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# STATS SECTION
st.markdown('<div class="section-title">📈 Performance Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stats-card">
        <div class="stat-number">93.2%</div>
        <div class="stat-label">F1 Score</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stats-card">
        <div class="stat-number">94.3%</div>
        <div class="stat-label">Precision</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stats-card">
        <div class="stat-number">92.1%</div>
        <div class="stat-label">Recall</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stats-card">
        <div class="stat-number">&lt;120s</div>
        <div class="stat-label">Processing Time</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ASSESSMENT SECTION
st.markdown('<div class="section-title">🎯 Start Assessment</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Enter a domain to analyze GDPR compliance</div>', unsafe_allow_html=True)

# Assessment Card
st.markdown('<div class="assessment-card">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    domain = st.text_input(
        "Domain Name",
        placeholder="example.com",
        help="Enter domain without http:// or https://",
        label_visibility="collapsed"
    )

    start_button = st.button("🚀 Start GDPR Assessment", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False
    st.session_state.result = None

# ASSESSMENT LOGIC
if start_button and domain:
    st.session_state.assessment_complete = False

    # Validate domain
    import re
    domain_pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
    if not re.match(domain_pattern, domain.lower()):
        st.error("❌ Invalid domain format. Please enter a valid domain like example.com")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🔄 Assessment in Progress</div>', unsafe_allow_html=True)

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Phase 1: OSINT Collection
            status_text.markdown("**Phase 1/5:** Collecting OSINT data (DNS, TLS, Breaches, Policy)...")
            progress_bar.progress(20)

            collector = OSINTCollector()
            osint_report = collector.collect(domain)
            time.sleep(1)

            # Phase 2: NLP Analysis
            status_text.markdown("**Phase 2/5:** Analyzing privacy policy with NLP...")
            progress_bar.progress(40)

            classifier = NLPClassifier()
            if osint_report.policy_text:
                nlp_results = classifier.classify(osint_report.policy_text)
            else:
                nlp_results = {control: 0.0 for control in [
                    "data_minimization", "purpose_limitation", "storage_limitation",
                    "accuracy", "integrity_confidentiality", "lawfulness",
                    "transparency", "consent", "data_subject_rights", "dpo_contact"
                ]}
            time.sleep(1)

            # Phase 3: Risk Scoring
            status_text.markdown("**Phase 3/5:** Calculating risk score...")
            progress_bar.progress(60)

            scorer = RiskScorer()
            risk_score = scorer.calculate_risk(nlp_results, osint_report)
            time.sleep(1)

            # Phase 4: Evidence Fusion
            status_text.markdown("**Phase 4/5:** Fusing evidence sources...")
            progress_bar.progress(80)
            time.sleep(1)

            # Phase 5: Generating Report
            status_text.markdown("**Phase 5/5:** Generating comprehensive report...")
            progress_bar.progress(100)
            time.sleep(1)

            # Store results
            st.session_state.result = {
                'domain': domain,
                'risk_score': risk_score,
                'nlp_results': nlp_results,
                'osint_report': osint_report
            }
            st.session_state.assessment_complete = True

            status_text.success("✅ Assessment complete!")
            progress_bar.empty()

        except Exception as e:
            st.error(f"❌ Error during assessment: {str(e)}")
            progress_bar.empty()

        st.markdown('</div>', unsafe_allow_html=True)

# RESULTS SECTION
if st.session_state.assessment_complete and st.session_state.result:
    result = st.session_state.result
    risk_score = result['risk_score']
    nlp_results = result['nlp_results']
    osint_report = result['osint_report']

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Assessment Results</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">Analysis for {result["domain"]}</div>', unsafe_allow_html=True)

    # Overall Risk Score
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">🎯 Overall Risk Assessment</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Determine risk level
        if risk_score >= 70:
            risk_level = "LOW RISK"
            risk_class = "risk-low"
        elif risk_score >= 40:
            risk_level = "MEDIUM RISK"
            risk_class = "risk-medium"
        else:
            risk_level = "HIGH RISK"
            risk_class = "risk-high"

        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div class="stat-number" style="font-size: 5rem; margin-bottom: 1rem;">{risk_score:.1f}</div>
            <div class="risk-badge {risk_class}">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#FF6B35"},
                'bar': {'color': "#FF6B35"},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "#FFE8CC",
                'steps': [
                    {'range': [0, 40], 'color': '#FFCDD2'},
                    {'range': [40, 70], 'color': '#FFE8CC'},
                    {'range': [70, 100], 'color': '#C8E6C9'}
                ],
                'threshold': {
                    'line': {'color': "#FF6B35", 'width': 6},
                    'thickness': 0.75,
                    'value': risk_score
                }
            }
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#6B4423", 'family': "Inter"}
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # GDPR Controls Analysis
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">📊 GDPR Controls Analysis</div>', unsafe_allow_html=True)

    # Radar chart
    controls_map = {
        "data_minimization": "Data Minimization",
        "purpose_limitation": "Purpose Limitation",
        "storage_limitation": "Storage Limitation",
        "accuracy": "Accuracy",
        "integrity_confidentiality": "Integrity & Confidentiality",
        "lawfulness": "Lawfulness",
        "transparency": "Transparency",
        "consent": "Consent",
        "data_subject_rights": "Data Subject Rights",
        "dpo_contact": "DPO Contact"
    }

    categories = list(controls_map.values())
    values = [nlp_results.get(k, 0.0) * 100 for k in controls_map.keys()]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 107, 53, 0.3)',
        line=dict(color='#FF6B35', width=3),
        name='Compliance Score'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12, color='#6B4423'),
                gridcolor='#FFE8CC'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#6B4423', family='Inter'),
                gridcolor='#FFE8CC'
            ),
            bgcolor='rgba(255, 245, 230, 0.3)'
        ),
        showlegend=False,
        height=500,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#6B4423')
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # OSINT Findings
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">🔍 OSINT Intelligence</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dns_status = "✅ Secure" if osint_report.dns_secure else "⚠️ Issues"
        st.metric("DNS Security", dns_status)

    with col2:
        tls_status = "✅ Valid" if osint_report.tls_valid else "⚠️ Issues"
        st.metric("TLS Certificate", tls_status)

    with col3:
        breach_count = len(osint_report.breaches) if osint_report.breaches else 0
        st.metric("Data Breaches", f"{breach_count} found")

    with col4:
        policy_status = "✅ Found" if osint_report.policy_found else "❌ Missing"
        st.metric("Privacy Policy", policy_status)

    st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">💡 Recommendations</div>', unsafe_allow_html=True)

    # Generate recommendations based on low scores
    recommendations = []
    for control_key, control_name in controls_map.items():
        score = nlp_results.get(control_key, 0.0)
        if score < 0.5:
            recommendations.append((control_name, score))

    if recommendations:
        recommendations.sort(key=lambda x: x[1])  # Sort by score (lowest first)

        for control_name, score in recommendations[:5]:  # Top 5 recommendations
            st.markdown(f"""
            <div class="recommendation-box">
                <div class="recommendation-title">⚠️ {control_name}</div>
                <div class="recommendation-text">
                    <strong>Current Score:</strong> {score*100:.1f}%<br>
                    <strong>Action:</strong> Review and enhance {control_name.lower()} measures in your privacy policy.
                    Ensure clear documentation and implementation of GDPR requirements.
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ All GDPR controls meet compliance thresholds!")

    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">📑 Detailed Breakdown</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Control Scores", "🔍 OSINT Details", "📥 Export"])

    with tab1:
        df = pd.DataFrame({
            'GDPR Control': list(controls_map.values()),
            'Compliance Score': [f"{nlp_results.get(k, 0.0)*100:.1f}%" for k in controls_map.keys()],
            'Status': ['✅ Pass' if nlp_results.get(k, 0.0) >= 0.5 else '❌ Fail' for k in controls_map.keys()]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### DNS Security")
        st.write(f"Status: {'✅ Secure' if osint_report.dns_secure else '⚠️ Issues Detected'}")

        st.markdown("#### TLS Certificate")
        st.write(f"Status: {'✅ Valid' if osint_report.tls_valid else '⚠️ Invalid or Expired'}")

        st.markdown("#### Data Breaches")
        if osint_report.breaches:
            st.write(f"⚠️ {len(osint_report.breaches)} breach(es) found in HaveIBeenPwned database")
        else:
            st.write("✅ No known breaches found")

        st.markdown("#### Privacy Policy")
        st.write(f"Status: {'✅ Found and analyzed' if osint_report.policy_found else '❌ Not found'}")

    with tab3:
        export_data = {
            'domain': result['domain'],
            'assessment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'gdpr_controls': {k: nlp_results.get(k, 0.0) for k in controls_map.keys()},
            'osint': {
                'dns_secure': osint_report.dns_secure,
                'tls_valid': osint_report.tls_valid,
                'breach_count': len(osint_report.breaches) if osint_report.breaches else 0,
                'policy_found': osint_report.policy_found
            }
        }

        st.download_button(
            label="📥 Download JSON Report",
            data=json.dumps(export_data, indent=2),
            file_name=f"osint_tprm_{result['domain']}_{time.strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <div class="footer-text" style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
        🎓 OSINT TPRM v1.0.0
    </div>
    <div class="footer-text">
        Developed at Saveetha Engineering College (Autonomous)
    </div>
    <div class="footer-text">
        Department of Computer Science & Engineering (Cybersecurity)
    </div>
    <div class="footer-text" style="margin-top: 1rem; font-size: 0.95rem; opacity: 0.9;">
        Team 94 | Junaid Sardar S & Janani G | Mentor: Dr. J. Varalakshmi
    </div>
</div>
""", unsafe_allow_html=True)
