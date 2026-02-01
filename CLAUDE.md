# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test Ollama connection
python utils/ollama_client.py

# Run stock analysis (CLI)
python main.py

# Generate HTML reports (after analysis)
python generate_report.py

# Run Streamlit dashboard (recommended)
streamlit run app.py

# Run with scheduler (daily automation)
python scheduler.py
```

**Prerequisites:**
- Ollama running locally (`ollama serve`)
- Model installed: `ollama pull deepseek-r1:8b`

## Architecture

Multi-agent stock analysis system using local Ollama LLM:

```
main.py (orchestrator)
├── agents/
│   ├── news_analyst.py        - Analyzes news sentiment
│   ├── statistical_expert.py  - Basic statistical analysis
│   ├── forecaster.py          - ARIMA/Prophet time series forecasting
│   ├── financial_expert.py    - Fundamental analysis
│   └── investment_synthesizer.py - Final buy/hold/sell recommendation
├── utils/
│   ├── ollama_client.py       - Ollama API wrapper
│   ├── data_fetcher.py        - Stock data (yfinance) & news (Google RSS)
│   └── visualizations.py      - Plotly/Matplotlib chart generation
└── app.py (Streamlit dashboard)
```

**Data Flow:**
1. `DataFetcher` gets stock prices from Yahoo Finance and news from Google RSS
2. `ForecasterAgent` fits ARIMA + Holt-Winters + Prophet ensemble models
3. Each AI agent processes relevant data via `OllamaClient`
4. `InvestmentSynthesizerAgent` combines all analyses
5. Results saved to `reports/` as JSON
6. `generate_report.py` creates static HTML for GitHub Pages
7. `app.py` provides interactive Streamlit dashboard

## Configuration

All settings in `config.py`:
- `STOCKS` - List of ticker symbols to analyze
- `OLLAMA_MODEL` - LLM model name (default: deepseek-r1:8b)
- `PREDICTION_DAYS` - Forecast horizon (default: 30)
- `OUTPUT_DIR` - JSON output directory
- `GITHUB_REPO_DIR` - HTML reports for GitHub Pages

## Forecaster Agent

The `ForecasterAgent` uses an ensemble of models:
- **ARIMA(5,1,0)** - Autoregressive Integrated Moving Average
- **Holt-Winters** - Exponential smoothing with damped trend
- **Prophet** - Facebook's time series forecasting (if available)

Outputs:
- Next day prediction with 95% confidence interval
- 10-day prediction with confidence interval
- Historical data for 1y/1m/10d timeframes
- Interactive charts via Plotly

## Streamlit App

Run `streamlit run app.py` for interactive dashboard with:
- Stock selector dropdown
- Interactive price charts with forecast overlay
- Confidence interval visualization
- Model comparison charts
- Full AI agent analysis on demand

## Deployment Options

**GitHub Pages (Static HTML):**
- Run `python generate_report.py`
- Push `docs/` folder to GitHub
- Enable Pages from `/docs` folder

**Streamlit Cloud (Interactive):**
1. Push repo to GitHub
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Set `app.py` as main file
5. Note: Requires Ollama running locally (limited on cloud)

## Known Issues Fixed

- Windows console encoding: `sys.stdout.reconfigure(encoding='utf-8')`
- Config variable naming: aliases for backward compatibility
- URL encoding: Company names with spaces properly encoded
- JSON serialization: Pandas Timestamp keys converted to strings
- File encoding: UTF-8 for all file writes
