# GitHub Repository Setup Guide

## Step-by-Step Instructions

### Step 1: Create Private Repository on GitHub

1. **Go to GitHub:** https://github.com/new

2. **Repository Settings:**
   - **Repository name:** `osint-tprm-gdpr`
   - **Description:** `OSINT-based GDPR compliance assessment tool with explainable AI risk scoring`
   - **Visibility:** ☑️ **Private** (IMPORTANT!)
   - **Initialize:** ☐ Do NOT check "Add README" (we already have one)
   - **License:** None (we have MIT in README)

3. **Click:** "Create repository"

### Step 2: Link Local Repository to GitHub

GitHub will show you commands. Use these in your terminal:

```bash
# Make sure you're in the mini-project directory
cd E:/research/mini-project

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/osint-tprm-gdpr.git

# Rename branch to main (if needed)
git branch -M main

# Push all commits to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

### Step 3: Verify Upload

After pushing, refresh your GitHub repository page. You should see:
- ✅ All 7 commits
- ✅ All files and directories
- ✅ README.md displayed on homepage
- ✅ "Private" label on repository

### Step 4: Configure Repository Settings (Optional)

**Go to Settings → General:**
- Add topics/tags: `gdpr`, `osint`, `compliance`, `streamlit`, `python`
- Update description if needed

**Go to Settings → Secrets and variables → Actions:**
- Add `HIBP_API_KEY` if you plan to use GitHub Actions

### Step 5: Invite Collaborator (Optional)

If working with Janani G:
1. Go to Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username or email
4. Send invitation

## Common Issues & Solutions

### Issue: "remote origin already exists"
```bash
# Remove existing remote and add new one
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/osint-tprm-gdpr.git
```

### Issue: Authentication Required
GitHub now requires personal access token instead of password.

**Solution:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy token
4. Use token as password when pushing

**Or use SSH (recommended):**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys
3. Use SSH URL: `git@github.com:YOUR_USERNAME/osint-tprm-gdpr.git`

### Issue: "failed to push some refs"
```bash
# Pull latest changes first (shouldn't be needed for new repo)
git pull origin main --rebase
git push origin main
```

## Verify Repository Structure on GitHub

Your GitHub repository should show:

```
osint-tprm-gdpr/
├── .env.example
├── .gitignore
├── README.md
├── SETUP.md
├── GITHUB_SETUP.md
├── requirements.txt
├── app.py
├── analysis/
│   ├── __init__.py
│   ├── nlp_classifier.py
│   └── risk_scorer.py
├── config/
│   └── gdpr_controls.json
├── models/
│   ├── __init__.py
│   ├── osint_report.py
│   ├── dns_findings.py
│   ├── tls_findings.py
│   ├── breach_findings.py
│   ├── policy_findings.py
│   └── risk_score.py
├── osint/
│   ├── __init__.py
│   ├── collector.py
│   ├── dns_checker.py
│   ├── tls_checker.py
│   ├── breach_checker.py
│   └── policy_scraper.py
├── data/
│   ├── training_policies/
│   └── trained_models/
├── scripts/
└── tests/
```

## Repository Insights

After setup, check:
- **Commits:** Should show 7 commits
- **Contributors:** 1 (you) + Claude Co-Author
- **Languages:** Python (majority), Markdown
- **Code frequency:** ~1020 lines

## Next Steps After GitHub Setup

1. **Share Repository:**
   - Share private repository with team members
   - Or generate access token for collaborators

2. **Enable GitHub Pages (Optional):**
   - Not needed for private code repo
   - Consider for public documentation

3. **Set Up CI/CD (Optional):**
   - Add `.github/workflows/test.yml` for automated testing
   - Run tests on every push

4. **Clone on Another Machine:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/osint-tprm-gdpr.git
   cd osint-tprm-gdpr
   pip install -r requirements.txt
   ```

## Security Notes

- ✅ `.env` file is in `.gitignore` (API keys never committed)
- ✅ Repository is **Private** (code not public)
- ✅ `.env.example` shows structure without actual keys
- ⚠️ Never commit real API keys to Git!

## Support

If you encounter issues:
1. Check GitHub documentation: https://docs.github.com
2. Verify Git is installed: `git --version`
3. Check remote: `git remote -v`
4. View commit history: `git log --oneline`

---

**Repository URL Template:**
`https://github.com/YOUR_USERNAME/osint-tprm-gdpr`

**Clone Command:**
`git clone https://github.com/YOUR_USERNAME/osint-tprm-gdpr.git`
