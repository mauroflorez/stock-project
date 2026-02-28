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
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "avg_volume": info.get("averageVolume"),
                # Fundamental metrics
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
                "profit_margins": info.get("profitMargins"),
                "return_on_equity": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "free_cashflow": info.get("freeCashflow"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation_key": info.get("recommendationKey"),
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
        
        # Helper for safe formatting
        def fmt(val, prefix='', suffix='', fmt_str='.2f'):
            if val is None:
                return 'N/A'
            return f"{prefix}{val:{fmt_str}}{suffix}"
        
        def fmt_pct(val):
            if val is None:
                return 'N/A'
            return f"{val*100:.1f}%"
        
        def fmt_int(val, prefix='$'):
            if val is None:
                return 'N/A'
            return f"{prefix}{val:,}"

        output = f"""
STOCK PRICE DATA FOR {data['symbol']} - {data['company_name']}

Current Information (as of {data['fetched_at']}):
- Current Price: ${data['current_price']:.2f}
- Previous Close: ${data['previous_close']:.2f}
- Day Change: ${data['day_change']:.2f} ({data['day_change_percent']:.2f}%)
- Market Cap: {fmt_int(data['market_cap'])}
- Sector: {data['sector']}
- Industry: {data['industry']}

Valuation Metrics:
- P/E Ratio (Trailing): {fmt(data['pe_ratio'])}
- P/E Ratio (Forward): {fmt(data.get('forward_pe'))}
- PEG Ratio: {fmt(data.get('peg_ratio'))}
- 52 Week High: {fmt(data['52_week_high'], prefix='$')}
- 52 Week Low: {fmt(data['52_week_low'], prefix='$')}

Growth & Profitability:
- Earnings Growth: {fmt_pct(data.get('earnings_growth'))}
- Revenue Growth: {fmt_pct(data.get('revenue_growth'))}
- Profit Margins: {fmt_pct(data.get('profit_margins'))}
- Return on Equity (ROE): {fmt_pct(data.get('return_on_equity'))}

Financial Health:
- Debt-to-Equity: {fmt(data.get('debt_to_equity'))}
- Free Cash Flow: {fmt_int(data.get('free_cashflow'))}
- Beta: {fmt(data.get('beta'))}
- Dividend Yield: {fmt_pct(data.get('dividend_yield'))}

Analyst Data:
- Target Price (Mean): {fmt(data.get('target_mean_price'), prefix='$')}
- Recommendation: {data.get('recommendation_key', 'N/A')}

Volume:
- Volume: {fmt_int(data['volume'], prefix='')}
- Average Volume: {fmt_int(data['avg_volume'], prefix='')}

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
