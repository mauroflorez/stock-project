# Stock Investment Planner

AI-powered multi-agent system for stock analysis using **100% local AI models** with Ollama. No API costs, runs completely on your machine.

## Features

- **5 Specialized AI Agents:**
  - **News Analyst** - Analyzes recent news and sentiment
  - **Statistical Expert** - Technical analysis and trend detection
  - **Forecaster** - ARIMA/Holt-Winters/Prophet ensemble predictions
  - **Financial Expert** - Fundamental analysis and valuation
  - **Investment Synthesizer** - Final buy/hold/sell recommendation

- **100% Local & Free:**
  - Uses Ollama for AI (no API costs)
  - Free data sources (Yahoo Finance, Google News)
  - Runs completely offline after setup

- **Beautiful Reports:**
  - Summary table with sparkline trends and color-coded recommendations
  - Executive summary for quick insights
  - Interactive Plotly forecast charts
  - Mobile-responsive design
  - GitHub Pages deployment

## Prerequisites

1. **Python 3.8+**
2. **Ollama** - Download from https://ollama.com
3. **Git** (for GitHub Pages deployment)

**System Requirements:**
- 8GB+ RAM (16GB recommended)
- 10GB free disk space

## Quick Start

### 1. Install Ollama Model

```bash
ollama pull deepseek-r1:8b
ollama serve
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Stocks

Edit `config.py`:

```python
STOCKS = ["GOOGL", "AAPL", "MSFT"]
STOCK_NAMES = {
    "GOOGL": "Alphabet Inc.",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
}
```

### 4. Run Analysis

```bash
# Run the analysis pipeline
python main.py

# Generate HTML reports
python generate_report.py

# Open reports in browser
start docs/index.html  # Windows
open docs/index.html   # macOS
```

## Adding New Stocks

1. **Edit `config.py`:**
   ```python
   STOCKS = ["GOOGL", "MSFT", "AAPL", "NVDA"]  # Add symbol
   STOCK_NAMES = {
       # ... existing ...
       "NVDA": "NVIDIA Corporation",  # Add name
   }
   ```

2. **Run analysis and generate reports:**
   ```bash
   python main.py
   python generate_report.py
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add NVDA stock analysis"
   git push
   ```

## Project Structure

```
stock-project/
├── main.py                  # Analysis orchestrator
├── generate_report.py       # HTML report generator
├── config.py                # Configuration (stocks, model, etc.)
├── app.py                   # Streamlit dashboard
├── agents/
│   ├── news_analyst.py      # News sentiment analysis
│   ├── statistical_expert.py # Technical analysis
│   ├── forecaster.py        # Time series forecasting
│   ├── financial_expert.py  # Fundamental analysis
│   └── investment_synthesizer.py # Final recommendation
├── utils/
│   ├── ollama_client.py     # Ollama API wrapper
│   ├── data_fetcher.py      # Stock data & news fetching
│   └── visualizations.py    # Chart generation
├── reports/                 # JSON analysis output
└── docs/                    # HTML reports (GitHub Pages)
```

## GitHub Pages Deployment

1. **Enable GitHub Pages:**
   - Go to repository Settings > Pages
   - Source: Deploy from branch
   - Branch: `main`, folder: `/docs`

2. **After each analysis run:**
   ```bash
   python main.py
   python generate_report.py
   git add docs/
   git commit -m "Update stock analysis"
   git push
   ```

3. **Your site will be at:**
   ```
   https://YOUR-USERNAME.github.io/YOUR-REPO/
   ```

## Streamlit Dashboard

For an interactive experience:

```bash
streamlit run app.py
```

## Configuration Options

In `config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `OLLAMA_MODEL` | AI model to use | `deepseek-r1:8b` |
| `STOCKS` | List of ticker symbols | `["GOOGL", "MSFT", "AAPL"]` |
| `DAYS_OF_HISTORICAL_DATA` | Historical data range | `365` |
| `PREDICTION_DAYS` | Forecast horizon | `30` |
| `MAX_NEWS_ARTICLES` | News articles to analyze | `10` |

## Output

**HTML Reports (`docs/`):**
- `index.html` - Summary table with all stocks
- `{symbol}.html` - Detailed analysis per stock

**JSON Reports (`reports/`):**
- `{SYMBOL}_analysis_{timestamp}.json` - Raw analysis data

## Troubleshooting

**"Cannot connect to Ollama"**
```bash
ollama serve  # Start Ollama
ollama list   # Verify model is installed
```

**"Model not found"**
```bash
ollama pull deepseek-r1:8b
```

**"Analysis takes too long"**
- Use a faster model: `OLLAMA_MODEL = "llama3.1:8b"`
- Analyze fewer stocks at once

## Cost

**Total: $0.00/month**

- Ollama (local AI): Free
- Yahoo Finance data: Free
- Google News RSS: Free
- GitHub Pages hosting: Free

## Disclaimer

This tool is for **educational purposes only**. Not financial advice. Always consult a qualified financial advisor before making investment decisions.

## License

For educational purposes. Use at your own risk.
