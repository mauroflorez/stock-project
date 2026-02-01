"""
Configuration file for Stock Investment Planner
"""

# Ollama Configuration
OLLAMA_MODEL = "deepseek-r1:8b"  # Change to "llama3.1:8b" if preferred
OLLAMA_BASE_URL = "http://localhost:11434"

# Stock Configuration
STOCKS = ["GOOGL", "MSFT", "AAPL"]
STOCK_SYMBOLS = STOCKS  # Alias for compatibility
STOCK_NAMES = {
    "GOOGL": "Alphabet Inc.",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla Inc.",
}

# Analysis Settings
DAYS_OF_HISTORICAL_DATA = 365  # One year of historical data
DAYS_OF_PRICE_DATA = DAYS_OF_HISTORICAL_DATA  # Alias for compatibility
PREDICTION_DAYS = 30  # How many days to predict forward

# News Settings
MAX_NEWS_ARTICLES = 10  # Number of recent news articles to analyze
NEWS_LOOKBACK_DAYS = 7  # Days to look back for news

# API Keys (not required - using free sources)
ALPHA_VANTAGE_API_KEY = None  # Not needed - using yfinance
NEWS_API_KEY = None  # Not needed - using Google News RSS

# Cost Protection (not needed for local, but good practice)
MAX_OLLAMA_TOKENS = 4000  # Max tokens per request
MAX_TOKENS = MAX_OLLAMA_TOKENS  # Alias for compatibility
TEMPERATURE = 0.7  # Creativity level (0.0-1.0)

# Output Settings
OUTPUT_DIR = "reports"
GITHUB_REPO_DIR = "stock-reports-github"  # Your GitHub Pages repo directory

# Schedule Settings (for automation)
RUN_TIME = "09:00"  # Daily run time (24-hour format)
TIMEZONE = "America/Los_Angeles"  # Your timezone
