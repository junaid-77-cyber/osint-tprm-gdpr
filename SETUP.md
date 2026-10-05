# Setup Instructions

## Prerequisites
- Python 3.11 or higher
- Git
- HaveIBeenPwned API key (get from https://haveibeenpwned.com/API/Key)

## Installation Steps

### 1. Clone Repository (after GitHub setup)
```bash
git clone https://github.com/YourUsername/osint-tprm-gdpr.git
cd osint-tprm-gdpr
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your HaveIBeenPwned API key:
```
HIBP_API_KEY=your_actual_api_key_here
```

### 4. Run Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## GitHub Repository Setup

### Create Private Repository on GitHub:

1. Go to https://github.com/new
2. Repository name: `osint-tprm-gdpr`
3. Description: "OSINT-based GDPR compliance assessment tool with explainable AI"
4. **Select:** ☑️ Private
5. **Do not** initialize with README (we already have one)
6. Click "Create repository"

### Push Existing Repository:

Run these commands in the `mini-project` directory:

```bash
git remote add origin https://github.com/YOUR_USERNAME/osint-tprm-gdpr.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Testing the Application

### Test with Sample Domains:
- `google.com`
- `github.com`
- `stripe.com`

### Expected Results:
- DNS/TLS checks complete
- Privacy policy detected (if available)
- Risk score calculated (0-100)
- GDPR compliance analysis
- Recommendations generated

## Troubleshooting

### Issue: "HIBP API key not configured"
**Solution:** Make sure your `.env` file exists with `HIBP_API_KEY=your_key`

### Issue: "Module not found"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "Privacy policy not found"
**Solution:** Normal for domains without accessible privacy policies. Tool will still provide OSINT analysis.

### Issue: DNS or TLS errors
**Solution:** Some domains may block automated checks. Try another domain.

## Project Structure

```
mini-project/
├── app.py                  # Main Streamlit application (365 lines)
├── requirements.txt        # Python dependencies
├── .env.example           # API key template
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── SETUP.md               # This file
├── models/                # Pydantic data models (7 files)
│   ├── osint_report.py
│   ├── dns_findings.py
│   ├── tls_findings.py
│   ├── breach_findings.py
│   ├── policy_findings.py
│   └── risk_score.py
├── osint/                 # OSINT collection modules (6 files)
│   ├── collector.py
│   ├── dns_checker.py
│   ├── tls_checker.py
│   ├── breach_checker.py
│   └── policy_scraper.py
├── analysis/              # NLP and risk scoring (3 files)
│   ├── nlp_classifier.py
│   ├── risk_scorer.py
│   └── __init__.py
├── config/                # Configuration files
│   └── gdpr_controls.json
└── data/                  # Training data (empty initially)
    ├── training_policies/
    └── trained_models/
```

## Next Steps

1. **Get HaveIBeenPwned API Key:**
   - Visit: https://haveibeenpwned.com/API/Key
   - Free tier: 1500 requests/month
   - Paid tier: $3.50/month (unlimited)

2. **Test the Application:**
   - Run `streamlit run app.py`
   - Test with multiple domains
   - Verify all OSINT checks work

3. **Customize:**
   - Modify `config/gdpr_controls.json` for different regulations
   - Adjust keyword patterns in `analysis/nlp_classifier.py`
   - Update scoring weights as needed

## Development

### Run in Development Mode:
```bash
streamlit run app.py --server.runOnSave true
```

Auto-reloads on file changes.

### Code Style:
- Follow PEP 8
- Use type hints
- Document functions with docstrings

### Git Workflow:
```bash
git add <files>
git commit -m "descriptive message"
git push origin main
```

## License
MIT License - See README.md for details
