# 📊 Stock Investment Planner

AI-powered multi-agent system for stock analysis using **100% local AI models** with Ollama. No API costs, runs completely on your machine!

## 🌟 Features

- **4 Specialized AI Agents:**
  - 📰 **News Analyst** - Analyzes recent news and sentiment
  - 📈 **Statistical Analyst** - Time series predictions using Prophet/ARIMA
  - 💼 **Financial Expert** - Fundamental analysis and company evaluation
  - 🎯 **Investment Synthesizer** - Final buy/hold/sell recommendation

- **100% Local & Free:**
  - Uses Ollama for AI (no API costs!)
  - Free data sources (Yahoo Finance, Google News)
  - Runs completely offline after setup

- **Beautiful Reports:**
  - Interactive HTML dashboards
  - Automated GitHub Pages deployment
  - Mobile-responsive design

- **Automated:**
  - Schedule daily analysis runs
  - Auto-deploy to GitHub Pages
  - JSON exports for further analysis

## 📋 Prerequisites

### Required

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Ollama** (for local AI)
   - **macOS**: Download from https://ollama.com
   - **Windows**: Download from https://ollama.com
   - **Linux**:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```

3. **Git** (for GitHub Pages)
   ```bash
   git --version
   ```

### Recommended

- **8GB+ RAM** (16GB better for larger models)
- **10GB free disk space**
- Stable internet connection (for data fetching)

## 🚀 Quick Start

### Step 1: Install Ollama Model

```bash
# Recommended model (best quality)
ollama pull deepseek-r1:8b

# Alternative (faster)
ollama pull llama3.1:8b

# Start Ollama (if not running)
ollama serve
```

### Step 2: Clone/Download This Project

```bash
# If you have the files, navigate to the directory
cd stock-investment-planner

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Configure Your Stocks

Edit `config.py`:

```python
# Add your stocks here
STOCKS = ["GOOGL", "AAPL", "MSFT"]

# Set your preferred run time
RUN_TIME = "09:00"  # 9 AM daily
TIMEZONE = "America/Los_Angeles"
```

### Step 4: Test the System

```bash
# Test Ollama connection
python ollama_utils.py

# Test data fetching
python data_fetcher.py

# Run first analysis
python run_analysis.py
```

This will create reports in the `stock-reports-github/` folder!

### Step 5: View Your Reports

```bash
# Open the HTML report in your browser
open stock-reports-github/index.html
# or on Linux: xdg-open stock-reports-github/index.html
# or on Windows: start stock-reports-github/index.html
```

## 🌐 Deploy to GitHub Pages

### Setup (One Time)

1. **Run setup script:**
   ```bash
   bash setup_github.sh
   ```
   Enter your GitHub username and repository name.

2. **Create repository on GitHub:**
   - Go to https://github.com/new
   - Name: `stock-analysis` (or whatever you chose)
   - Make it **Public**
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub:**
   ```bash
   cd stock-reports-github
   git push -u origin main
   ```

4. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main`, folder: `/ (root)`
   - Save

5. **Your site will be live at:**
   ```
   https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
   ```

### Update Reports (Daily)

After running analysis:

```bash
bash deploy_to_github.sh
```

This automatically commits and pushes new reports to GitHub Pages!

## ⏰ Automate Daily Analysis

### Option 1: Python Scheduler (Recommended)

```bash
# Run the scheduler (keeps running)
python scheduler.py
```

This will:
- Run analysis daily at your configured time
- Auto-deploy to GitHub Pages
- Keep running in the background

**To run 24/7:**

```bash
# Using nohup (Linux/Mac)
nohup python scheduler.py > scheduler.log 2>&1 &

# Or use screen
screen -S stock-planner
python scheduler.py
# Press Ctrl+A then D to detach
```

### Option 2: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/stock-investment-planner && python run_analysis.py && bash deploy_to_github.sh
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\stock-investment-planner\run_analysis.py`
7. Save and enable

## 📁 Project Structure

```
stock-investment-planner/
├── config.py                 # Configuration (stocks, schedule, etc.)
├── requirements.txt          # Python dependencies
├── ollama_utils.py          # Ollama API integration
├── data_fetcher.py          # Stock data & news fetching
├── predictions.py           # Time series forecasting
├── agents.py                # 4 AI agents
├── stock_analyzer.py        # Main analysis orchestrator
├── report_generator.py      # HTML report generation
├── run_analysis.py          # Main runner script
├── scheduler.py             # Automated scheduling
├── setup_github.sh          # GitHub Pages setup
├── deploy_to_github.sh      # Deployment script
└── stock-reports-github/    # Output directory (git repo)
    ├── index.html           # Dashboard
    ├── GOOGL_report.html    # Individual stock reports
    └── ...
```

## 🔧 Configuration Options

### config.py

```python
# Ollama Settings
OLLAMA_MODEL = "deepseek-r1:8b"  # AI model to use
OLLAMA_BASE_URL = "http://localhost:11434"

# Stocks to Analyze
STOCKS = ["GOOGL", "AAPL", "MSFT"]

# Analysis Settings
DAYS_OF_HISTORICAL_DATA = 365  # 1 year
PREDICTION_DAYS = 30           # Forecast 30 days ahead
MAX_NEWS_ARTICLES = 10         # News articles to analyze

# Scheduling
RUN_TIME = "09:00"             # 24-hour format
TIMEZONE = "America/Los_Angeles"

# Output
OUTPUT_DIR = "reports"                    # JSON reports
GITHUB_REPO_DIR = "stock-reports-github"  # HTML for GitHub
```

## 📊 Understanding the Output

### JSON Reports (`reports/` folder)
- Detailed JSON with all data and analyses
- Good for further processing/analysis
- One file per stock per day

### HTML Reports (`stock-reports-github/` folder)
- Beautiful visual dashboards
- Mobile-friendly
- Auto-deployed to GitHub Pages
- `index.html` = Main dashboard
- `{TICKER}_report.html` = Individual stock reports

## 🐛 Troubleshooting

### "Cannot connect to Ollama"

```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# Or restart the Ollama app (Mac/Windows)
```

### "Model not found"

```bash
# Pull the model
ollama pull deepseek-r1:8b

# Verify it's installed
ollama list
```

### "No module named 'prophet'"

```bash
# Prophet can be tricky, try:
pip install prophet --break-system-packages

# On Mac with M1/M2:
conda install -c conda-forge prophet
```

### "Analysis takes too long"

1. Use a smaller/faster model:
   ```python
   OLLAMA_MODEL = "llama3.1:8b"  # Faster than deepseek-r1
   ```

2. Reduce token limits in `config.py`:
   ```python
   MAX_OLLAMA_TOKENS = 2000  # Lower from 4000
   ```

3. Analyze fewer stocks at once

### GitHub Pages not updating

1. Check if push succeeded:
   ```bash
   cd stock-reports-github
   git status
   ```

2. Verify GitHub Pages is enabled in repository settings

3. Wait 2-3 minutes for GitHub to build the site

4. Check GitHub Actions tab for build errors

## 💰 Cost Breakdown

### 100% Free Setup:
- ✅ Ollama (local AI): **FREE**
- ✅ Stock data (Yahoo Finance): **FREE**
- ✅ News (Google News RSS): **FREE**
- ✅ GitHub Pages hosting: **FREE**
- ✅ Time series analysis: **FREE**

### Total Monthly Cost: **$0.00**

No subscriptions, no API fees, no hidden costs!

## ⚠️ Important Disclaimers

**This tool is for EDUCATIONAL purposes only:**

- ❌ NOT professional financial advice
- ❌ NOT a registered investment advisor
- ❌ NOT guaranteed to be accurate
- ✅ Always consult a qualified financial advisor
- ✅ Do your own research (DYOR)
- ✅ Invest responsibly

**Past performance does not guarantee future results.**

## 🤝 Contributing

Feel free to:
- Add more stocks
- Improve agent prompts
- Add new data sources
- Enhance visualizations
- Share your improvements!

## 📝 License

This project is for educational purposes. Use at your own risk.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Test each component individually
4. Check `ollama_utils.py` and `data_fetcher.py` test modes

## 🎯 Next Steps

After setup:

1. ✅ Run your first analysis
2. ✅ View the HTML reports
3. ✅ Deploy to GitHub Pages
4. ✅ Set up automation
5. ✅ Add more stocks
6. ✅ Customize agent prompts
7. ✅ Share your results!

---

**Happy Investing! 📈💰**

(Remember: This is not financial advice! Always DYOR and consult professionals.)
