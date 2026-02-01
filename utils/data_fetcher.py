"""
Data Fetcher - Gets stock prices and news from free APIs
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import feedparser
from urllib.parse import quote
from config import ALPHA_VANTAGE_API_KEY, NEWS_API_KEY, DAYS_OF_PRICE_DATA, NEWS_LOOKBACK_DAYS


class DataFetcher:
    """Fetches stock data and news from free sources"""
    
    @staticmethod
    def get_stock_prices(symbol: str, days: int = DAYS_OF_PRICE_DATA) -> Dict[str, Any]:
        """
        Fetch historical stock prices using yfinance (100% free)
        
        Args:
            symbol: Stock ticker symbol (e.g., 'GOOGL')
            days: Number of days of historical data
            
        Returns:
            Dictionary with price data
        """
        try:
            stock = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Get current info
            info = stock.info
            
            return {
                "symbol": symbol,
                "company_name": info.get("longName", symbol),
                "current_price": info.get("currentPrice", hist['Close'].iloc[-1]),
                "previous_close": info.get("previousClose", hist['Close'].iloc[-2] if len(hist) > 1 else None),
                "day_change": info.get("currentPrice", hist['Close'].iloc[-1]) - info.get("previousClose", hist['Close'].iloc[-2] if len(hist) > 1 else 0),
                "day_change_percent": ((info.get("currentPrice", hist['Close'].iloc[-1]) - info.get("previousClose", hist['Close'].iloc[-2] if len(hist) > 1 else 0)) / info.get("previousClose", hist['Close'].iloc[-2] if len(hist) > 1 else 1)) * 100,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "avg_volume": info.get("averageVolume"),
                "historical_prices": {str(k): v for k, v in hist['Close'].to_dict().items()},
                "historical_dates": [str(date.date()) for date in hist.index],
                "historical_close": hist['Close'].tolist(),
                "historical_volume": hist['Volume'].tolist(),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "description": info.get("longBusinessSummary", ""),
                "fetched_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error fetching stock data: {str(e)}"}
    
    @staticmethod
    def get_news(symbol: str, company_name: str = None, days: int = NEWS_LOOKBACK_DAYS) -> List[Dict[str, Any]]:
        """
        Fetch recent news about the stock
        Uses Google News RSS (free, no API key needed)
        
        Args:
            symbol: Stock ticker symbol
            company_name: Company name for better search results
            days: How many days back to search
            
        Returns:
            List of news articles
        """
        news_items = []
        
        # Use company name if available, otherwise symbol
        search_term = company_name if company_name else symbol
        
        try:
            # Google News RSS feed (free)
            encoded_term = quote(search_term)
            url = f"https://news.google.com/rss/search?q={encoded_term}+stock&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries[:10]:  # Limit to top 10
                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Only include recent news
                if pub_date and pub_date < cutoff_date:
                    continue
                
                news_items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": pub_date.isoformat() if pub_date else "Unknown",
                    "source": entry.get("source", {}).get("title", "Unknown"),
                    "summary": entry.get("summary", "")
                })
            
            return news_items
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return [{"error": f"Could not fetch news: {str(e)}"}]
    
    @staticmethod
    def format_price_data_for_agent(data: Dict[str, Any]) -> str:
        """Format price data into a readable string for the agent"""
        if "error" in data:
            return f"Error: {data['error']}"
        
        output = f"""
STOCK PRICE DATA FOR {data['symbol']} - {data['company_name']}

Current Information (as of {data['fetched_at']}):
- Current Price: ${data['current_price']:.2f}
- Previous Close: ${data['previous_close']:.2f}
- Day Change: ${data['day_change']:.2f} ({data['day_change_percent']:.2f}%)
- Market Cap: ${data['market_cap']:,} if data['market_cap'] else 'N/A'
- P/E Ratio: {data['pe_ratio']:.2f} if data['pe_ratio'] else 'N/A'
- 52 Week High: ${data['52_week_high']:.2f}
- 52 Week Low: ${data['52_week_low']:.2f}
- Volume: {data['volume']:,}
- Average Volume: {data['avg_volume']:,}
- Sector: {data['sector']}
- Industry: {data['industry']}

Historical Prices (Last {len(data['historical_close'])} days):
{', '.join([f"${price:.2f}" for price in data['historical_close'][-10:]])}...

Company Description:
{data['description'][:500]}...
"""
        return output
    
    @staticmethod
    def format_news_for_agent(news_items: List[Dict[str, Any]]) -> str:
        """Format news into a readable string for the agent"""
        if not news_items:
            return "No recent news found."
        
        if "error" in news_items[0]:
            return f"Error: {news_items[0]['error']}"
        
        output = f"RECENT NEWS ({len(news_items)} articles):\n\n"
        
        for i, item in enumerate(news_items, 1):
            output += f"{i}. {item['title']}\n"
            output += f"   Source: {item['source']} | Published: {item['published']}\n"
            output += f"   {item['summary'][:200]}...\n"
            output += f"   Link: {item['link']}\n\n"
        
        return output


if __name__ == "__main__":
    # Test the data fetcher
    print("📊 Testing Stock Data Fetcher...\n")
    
    fetcher = DataFetcher()
    
    # Test stock prices
    print("Fetching GOOGL stock data...")
    stock_data = fetcher.get_stock_prices("GOOGL", days=30)
    print(fetcher.format_price_data_for_agent(stock_data))
    
    print("\n" + "="*80 + "\n")
    
    # Test news
    print("Fetching GOOGL news...")
    news = fetcher.get_news("GOOGL", "Google Alphabet")
    print(fetcher.format_news_for_agent(news))
