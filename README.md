# OSINT TPRM - GDPR Compliance Assessment Tool

AI-powered third-party risk management system using OSINT and explainable risk scoring.

## Features
- 🔍 OSINT data collection (DNS, TLS, breach, policy)
- 🤖 NLP analysis with keyword classification
- 📊 Interactive Streamlit dashboard
- 📝 Explainable AI recommendations
- ✅ Automated GDPR compliance assessment

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your HaveIBeenPwned API key (get from https://haveibeenpwned.com/API/Key)

### Run Application
```bash
streamlit run app.py
```

## Architecture
- **OSINT Collection Layer**: DNS security, TLS validation, breach data, privacy policy scraping
- **NLP Analysis Layer**: Keyword-based GDPR control detection
- **Risk Scoring**: Weighted aggregation with OSINT penalties
- **Presentation Layer**: Streamlit dashboard with Plotly visualizations

## Project Structure
```
mini-project/
├── app.py                  # Main Streamlit application
├── models/                 # Pydantic data models
├── osint/                  # OSINT collection modules
├── analysis/               # NLP and risk scoring
├── explainer/              # Recommendation generator
├── config/                 # GDPR controls and weights
└── data/                   # Training data
```

## Technologies
- Python 3.11+
- Streamlit (UI framework)
- Plotly (visualizations)
- DNSPython (DNS checks)
- BeautifulSoup (web scraping)
- Pydantic (data validation)

## Authors
- Junaid Sardar S (212224100028)
- Janani G (212224100017)
- Mentor: Dr. J. Varalakshmi
- Institution: Saveetha Engineering College (Autonomous), Chennai

## License
MIT License
