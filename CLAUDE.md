# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test Ollama connection
python utils/ollama_client.py

# Run stock analysis
python main.py

# Generate HTML reports (after analysis)
python generate_report.py

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
│   ├── news_analyst.py      - Analyzes news sentiment
│   ├── statistical_expert.py - Time series predictions (Prophet)
│   ├── financial_expert.py   - Fundamental analysis
│   └── investment_synthesizer.py - Final buy/hold/sell recommendation
└── utils/
    ├── ollama_client.py     - Ollama API wrapper
    └── data_fetcher.py      - Stock data (yfinance) & news (Google RSS)
```

**Data Flow:**
1. `DataFetcher` gets stock prices from Yahoo Finance and news from Google RSS
2. Each agent processes relevant data via `OllamaClient`
3. `InvestmentSynthesizerAgent` combines all analyses
4. Results saved to `reports/` as JSON
5. `generate_report.py` creates HTML for GitHub Pages

## Configuration

All settings in `config.py`:
- `STOCKS` - List of ticker symbols to analyze
- `OLLAMA_MODEL` - LLM model name (default: deepseek-r1:8b)
- `PREDICTION_DAYS` - Forecast horizon (default: 30)
- `OUTPUT_DIR` - JSON output directory
- `GITHUB_REPO_DIR` - HTML reports for GitHub Pages

## Known Issues Fixed

- Windows console encoding: `sys.stdout.reconfigure(encoding='utf-8')` in main.py
- Config variable naming: aliases added for backward compatibility (STOCK_SYMBOLS, MAX_TOKENS, etc.)
- URL encoding: Company names with spaces now properly encoded in news fetcher
- JSON serialization: Pandas Timestamp keys converted to strings
