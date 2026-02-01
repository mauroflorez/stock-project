# 📋 Installation Checklist

Follow these steps to get your Stock Investment Planner running!

## ✅ Step-by-Step Setup

### 1. Install Prerequisites

- [ ] **Python 3.8 or higher**
  - Check: `python3 --version`
  - Install: https://www.python.org/downloads/

- [ ] **Ollama** (for local AI)
  - Check: `ollama --version`
  - Install: https://ollama.com
  - macOS/Windows: Download installer
  - Linux: `curl -fsSL https://ollama.com/install.sh | sh`

- [ ] **Git** (optional, for GitHub Pages)
  - Check: `git --version`
  - Install: https://git-scm.com

### 2. Install Ollama Model

```bash
# Pull the recommended model (5GB download)
ollama pull deepseek-r1:8b

# Alternative (faster, 4.7GB)
ollama pull llama3.1:8b

# Verify installation
ollama list
```

### 3. Install Python Dependencies

```bash
cd stock-investment-planner

# Install all required packages
pip install -r requirements.txt

# If that fails, try:
pip install -r requirements.txt --break-system-packages
```

### 4. Test Your Installation

```bash
# Test Ollama connection
python3 ollama_utils.py

# Should output:
# ✓ Ollama is running
# ✓ Model 'deepseek-r1:8b' is ready
# Test generation successful
```

```bash
# Test data fetching
python3 data_fetcher.py

# Should output:
# ✓ Got 30 days of data
# ✓ Found X news articles
```

### 5. Configure Your Stocks

Edit `config.py`:

```python
# Change this line to analyze your preferred stocks
STOCKS = ["GOOGL", "AAPL", "MSFT"]

# Set your timezone
TIMEZONE = "America/Los_Angeles"  # or your timezone

# Set when to run daily
RUN_TIME = "09:00"  # 9 AM
```

### 6. Run Your First Analysis

```bash
# Run the complete analysis
python3 run_analysis.py

# This will:
# 1. Check Ollama is running
# 2. Fetch stock data for Google
# 3. Run all 4 AI agents
# 4. Generate HTML reports
# 5. Save to stock-reports-github/
```

**This will take 5-10 minutes for the first run!**

### 7. View Your Reports

```bash
# macOS
open stock-reports-github/index.html

# Linux
xdg-open stock-reports-github/index.html

# Windows
start stock-reports-github/index.html
```

You should see a beautiful dashboard with your analysis!

## 🌐 Optional: Deploy to GitHub Pages

### 8. Set Up GitHub Repository

```bash
# Run the setup script
bash setup_github.sh

# Follow the prompts:
# - Enter your GitHub username
# - Enter repository name (e.g., "stock-analysis")
```

### 9. Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: (what you entered in setup)
3. Make it **Public**
4. **DO NOT** initialize with README
5. Click "Create repository"

### 10. Push to GitHub

```bash
cd stock-reports-github
git push -u origin main
```

### 11. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Scroll to **Pages** section
4. Under "Source":
   - Select branch: **main**
   - Select folder: **/ (root)**
5. Click **Save**

### 12. View Your Live Site!

Your site will be available at:
```
https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
```

**Note**: First deployment takes 2-5 minutes to go live.

## ⏰ Optional: Set Up Automation

### Option A: Python Scheduler (Easiest)

```bash
# Start the scheduler
python3 scheduler.py

# This will:
# - Run analysis daily at configured time
# - Auto-deploy to GitHub Pages
# - Keep running in background
```

To keep it running 24/7:

```bash
# Linux/Mac - using nohup
nohup python3 scheduler.py > scheduler.log 2>&1 &

# Or using screen
screen -S stock-planner
python3 scheduler.py
# Press Ctrl+A then D to detach
```

### Option B: Cron Job (Linux/Mac)

```bash
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/stock-investment-planner && python3 run_analysis.py && bash deploy_to_github.sh
```

### Option C: Task Scheduler (Windows)

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name it: "Stock Analysis"
4. Trigger: **Daily** at **9:00 AM**
5. Action: **Start a program**
6. Program: `C:\Python\python.exe`
7. Arguments: `C:\path\to\stock-investment-planner\run_analysis.py`
8. **Finish** and enable

## 📊 Daily Workflow

Once automated, the system will:

1. **Every day at 9 AM:**
   - Fetch latest stock data
   - Analyze with 4 AI agents
   - Generate HTML reports
   - Deploy to GitHub Pages

2. **You can manually run:**
   ```bash
   python3 run_analysis.py      # Run analysis
   bash deploy_to_github.sh     # Deploy to GitHub
   ```

3. **View results:**
   - Local: `stock-reports-github/index.html`
   - Online: `https://YOUR-USERNAME.github.io/YOUR-REPO/`

## 🔧 Troubleshooting

### Problem: "Cannot connect to Ollama"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve

# Or start the Ollama app (Mac/Windows)
```

### Problem: "Model not found"

```bash
# Pull the model
ollama pull deepseek-r1:8b

# Verify
ollama list
```

### Problem: "prophet module not found"

```bash
# Try installing Prophet
pip install prophet --break-system-packages

# On Mac M1/M2
brew install cmake
pip install prophet
```

### Problem: Analysis is slow

1. Use faster model:
   ```python
   # In config.py
   OLLAMA_MODEL = "llama3.1:8b"
   ```

2. Reduce token limits:
   ```python
   # In config.py
   MAX_OLLAMA_TOKENS = 2000
   ```

3. Analyze fewer stocks

### Problem: GitHub Pages not updating

1. Check git status:
   ```bash
   cd stock-reports-github
   git status
   ```

2. Manual push:
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```

3. Wait 2-3 minutes for GitHub to build

4. Check **Actions** tab on GitHub for errors

## ✅ Quick Test Commands

```bash
# Test everything
python3 ollama_utils.py      # Test Ollama
python3 data_fetcher.py      # Test data
python3 run_analysis.py      # Full analysis

# View results
open stock-reports-github/index.html
```

## 📝 Configuration Quick Reference

**config.py** - Main settings:
```python
OLLAMA_MODEL = "deepseek-r1:8b"  # AI model
STOCKS = ["GOOGL", "AAPL"]       # Stocks to analyze
RUN_TIME = "09:00"               # Daily run time
TIMEZONE = "America/Los_Angeles" # Your timezone
```

## 🎯 Success Checklist

After completing setup, you should have:

- [ ] Ollama installed and running
- [ ] deepseek-r1:8b model downloaded
- [ ] Python dependencies installed
- [ ] First analysis completed successfully
- [ ] HTML reports generated
- [ ] (Optional) GitHub Pages deployed
- [ ] (Optional) Automation configured

## 🎉 You're Done!

Your Stock Investment Planner is now ready!

**What's Next?**
- Add more stocks to config.py
- Customize AI agent prompts in agents.py
- Share your GitHub Pages site
- Set up automation for daily updates

**Remember:** This is for educational purposes only. Not financial advice!

---

Need help? Check README.md for detailed documentation!
