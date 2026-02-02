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

## Quick Reference: Adding New Stocks

1. Edit `config.py`:
   ```python
   STOCKS = ["GOOGL", "MSFT", "AAPL", "NVDA"]  # Add new symbol
   STOCK_NAMES = {
       # ... existing entries ...
       "NVDA": "NVIDIA Corporation",  # Add company name
   }
   ```

2. Run analysis and generate reports:
   ```bash
   python main.py
   python generate_report.py
   ```

3. Commit and push:
   ```bash
   git add .
   git commit -m "Add NVDA stock analysis"
   git push
   ```

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
├── generate_report.py         - HTML report generator (GitHub Pages)
└── app.py (Streamlit dashboard)
```

**Output Directories:**
- `reports/` - JSON analysis files (raw data)
- `docs/` - HTML reports for GitHub Pages

**Data Flow:**
1. `DataFetcher` gets stock prices from Yahoo Finance and news from Google RSS
2. `ForecasterAgent` fits ARIMA + Holt-Winters + Prophet ensemble models
3. Each AI agent processes relevant data via `OllamaClient`
4. `InvestmentSynthesizerAgent` combines all analyses
5. Results saved to `reports/` as JSON
6. `generate_report.py` creates static HTML for GitHub Pages in `docs/`
7. `app.py` provides interactive Streamlit dashboard

## Configuration

All settings in `config.py`:
- `STOCKS` - List of ticker symbols to analyze
- `STOCK_NAMES` - Dictionary mapping symbols to company names
- `OLLAMA_MODEL` - LLM model name (default: deepseek-r1:8b)
- `PREDICTION_DAYS` - Forecast horizon (default: 30)
- `OUTPUT_DIR` - JSON output directory (`reports/`)

## HTML Report Generator

The `generate_report.py` file creates static HTML reports with:

**Index Page (`docs/index.html`):**
- Summary table with all stocks
- Columns: Symbol, Price, Sparkline trend, Prediction, News/Technical/Fundamental badges, Final recommendation
- Color-coded badges (green=bullish, orange=neutral, red=bearish)

**Individual Stock Pages (`docs/{symbol}.html`):**
- Executive Summary with brief insights from each agent
- Price forecast with interactive Plotly charts
- Detailed analysis sections with proper HTML formatting

**Key Methods:**
- `markdown_to_html()` - Converts markdown to proper HTML
- `generate_sparkline_svg()` - Creates inline SVG trend charts
- `extract_*_sentiment/outlook()` - Parses agent recommendations
- `generate_executive_summary()` - Creates concise summary section

## Deployment to GitHub Pages

```bash
# After running analysis
python main.py
python generate_report.py
git add docs/
git commit -m "Update stock analysis reports"
git push
```

GitHub Pages serves from the `/docs` folder.

## Lessons Learned

### HTML Report Generation
- Agent outputs contain markdown formatting that must be converted to HTML
- Use regex to convert `**bold**` to `<strong>`, lists to `<ul>/<ol>`, etc.
- Section headers in ALL CAPS (e.g., `SENTIMENT:`) work well for parsing
- Summary extraction should clean markdown artifacts before display
- Sparklines work well as inline SVGs for quick trend visualization

### Agent Output Parsing
- Agents output structured text with section headers (SENTIMENT:, TREND:, etc.)
- Parse these sections to extract key values for summary displays
- Always clean extracted text of markdown formatting for display in badges/summaries
- The synthesis agent's RECOMMENDATION and CONFIDENCE lines are key outputs

### Data Handling
- Historical prices come as dict with timestamp keys - convert to list for sparklines
- yfinance returns Pandas Timestamps that need string conversion for JSON
- Always use UTF-8 encoding for file writes (Windows compatibility)

### CSS/Styling
- Use CSS Grid for responsive layouts
- Color-coded badges improve scannability (green/orange/red)
- Executive summary section provides quick overview before detailed analysis
- Mobile-responsive design uses `minmax()` in grid columns

## Known Issues Fixed

- Windows console encoding: `sys.stdout.reconfigure(encoding='utf-8')`
- Config variable naming: aliases for backward compatibility
- URL encoding: Company names with spaces properly encoded
- JSON serialization: Pandas Timestamp keys converted to strings
- File encoding: UTF-8 for all file writes
- Markdown in HTML: Convert `**text**` to `<strong>` tags before rendering

## Legacy Files (Not Used)

The following files are from an older single-file architecture and are no longer used:
- `agents.py` - replaced by `agents/` directory
- `data_fetcher.py` (root) - replaced by `utils/data_fetcher.py`
- `ollama_utils.py` - replaced by `utils/ollama_client.py`
- `predictions.py` - replaced by `agents/forecaster.py`
- `stock_analyzer.py` - replaced by `main.py`
- `report_generator.py` - replaced by `generate_report.py`
- `run_analysis.py` - replaced by `main.py`
