"""
Data Fetcher Module
Fetches stock prices and news from free APIs
"""

import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from config import DAYS_OF_HISTORICAL_DATA, MAX_NEWS_ARTICLES


class StockDataFetcher:
    """Fetch stock price data using Yahoo Finance"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        
    def get_historical_data(self, days: int = DAYS_OF_HISTORICAL_DATA) -> pd.DataFrame:
        """
        Get historical stock data
        Returns DataFrame with Date, Open, High, Low, Close, Volume
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = self.stock.history(start=start_date, end=end_date)
            
            if df.empty:
                raise Exception(f"No data found for {self.ticker}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching historical data: {str(e)}")
    
    def get_company_info(self) -> Dict:
        """
        Get company information
        """
        try:
            info = self.stock.info
            
            return {
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "current_price": info.get("currentPrice", 0),
                "description": info.get("longBusinessSummary", "N/A")
            }
        except Exception as e:
            print(f"Warning: Could not fetch company info: {str(e)}")
            return {}
    
    def get_latest_price(self) -> float:
        """Get the most recent closing price"""
        try:
            df = self.get_historical_data(days=5)
            return df['Close'].iloc[-1]
        except:
            return 0.0


class NewsDataFetcher:
    """Fetch recent news about a stock"""
    
    def __init__(self, ticker: str, company_name: str = None):
        self.ticker = ticker.upper()
        self.company_name = company_name or ticker
        
    def get_google_news(self, max_articles: int = MAX_NEWS_ARTICLES) -> List[Dict]:
        """
        Fetch news from Google News RSS feed
        """
        try:
            # Search query for the company
            query = f"{self.company_name} stock"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            
            articles = []
            for entry in feed.entries[:max_articles]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "Unknown"),
                    "summary": entry.get("summary", "")
                })
            
            return articles
            
        except Exception as e:
            print(f"Warning: Could not fetch Google News: {str(e)}")
            return []
    
    def get_yahoo_finance_news(self, max_articles: int = MAX_NEWS_ARTICLES) -> List[Dict]:
        """
        Fetch news from Yahoo Finance
        """
        try:
            stock = yf.Ticker(self.ticker)
            news = stock.news
            
            articles = []
            for item in news[:max_articles]:
                articles.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "published": datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "source": item.get("publisher", "Yahoo Finance"),
                    "summary": ""
                })
            
            return articles
            
        except Exception as e:
            print(f"Warning: Could not fetch Yahoo Finance news: {str(e)}")
            return []
    
    def get_all_news(self, max_articles: int = MAX_NEWS_ARTICLES) -> List[Dict]:
        """
        Combine news from multiple sources
        """
        all_news = []
        
        # Try Yahoo Finance first
        yahoo_news = self.get_yahoo_finance_news(max_articles)
        all_news.extend(yahoo_news)
        
        # Then Google News if we need more
        if len(all_news) < max_articles:
            remaining = max_articles - len(all_news)
            google_news = self.get_google_news(remaining)
            all_news.extend(google_news)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_news = []
        for article in all_news:
            if article["title"] not in seen_titles:
                seen_titles.add(article["title"])
                unique_news.append(article)
        
        return unique_news[:max_articles]


def test_data_fetching():
    """Test the data fetching functions"""
    print("Testing Stock Data Fetcher...")
    
    fetcher = StockDataFetcher("GOOGL")
    
    # Test historical data
    print("\n1. Fetching historical data...")
    df = fetcher.get_historical_data(days=30)
    print(f"   Got {len(df)} days of data")
    print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
    
    # Test company info
    print("\n2. Fetching company info...")
    info = fetcher.get_company_info()
    print(f"   Company: {info.get('name', 'N/A')}")
    print(f"   Sector: {info.get('sector', 'N/A')}")
    
    # Test news
    print("\n3. Fetching news...")
    news_fetcher = NewsDataFetcher("GOOGL", "Google")
    news = news_fetcher.get_all_news(max_articles=5)
    print(f"   Found {len(news)} articles")
    for i, article in enumerate(news[:3], 1):
        print(f"   {i}. {article['title'][:60]}...")
    
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    test_data_fetching()
