"""
News Analyst Agent - Analyzes recent news about the stock
"""

from utils.ollama_client import OllamaClient


class NewsAnalystAgent:
    """
    Agent specialized in analyzing news sentiment and impact on stock
    """
    
    SYSTEM_PROMPT = """You are a News Analyst specializing in financial markets and stock analysis.

Your role:
- Analyze recent news articles about a company/stock
- Identify positive, negative, and neutral news
- Assess the potential impact on stock price
- Highlight any major events, announcements, or concerns
- Provide a clear sentiment summary (Bullish/Bearish/Neutral)

Be concise, factual, and focus on actionable insights.
Avoid speculation - stick to what the news actually says.
"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.name = "News Analyst"
    
    def analyze(self, news_data: str, stock_symbol: str) -> dict:
        """
        Analyze news data and return insights
        
        Args:
            news_data: Formatted news articles as string
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with analysis results
        """
        
        prompt = f"""
Analyze the following recent news about {stock_symbol}:

{news_data}

Provide your analysis in the following format:

SENTIMENT: [Bullish/Bearish/Neutral]

KEY POSITIVE NEWS:
- [List positive developments]

KEY NEGATIVE NEWS:
- [List concerns or challenges]

MAJOR EVENTS:
- [List any significant announcements or events]

IMPACT ASSESSMENT:
[Brief assessment of how this news might impact the stock]

SUMMARY:
[2-3 sentence summary of the overall news landscape]
"""
        
        print(f"🗞️  {self.name} is analyzing news...")
        
        response = self.client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT
        )
        
        return {
            "agent": self.name,
            "analysis": response,
            "raw_data": news_data
        }


if __name__ == "__main__":
    # Test the agent
    from utils.data_fetcher import DataFetcher
    
    print("Testing News Analyst Agent...\n")
    
    fetcher = DataFetcher()
    news = fetcher.get_news("GOOGL", "Google Alphabet", days=2)
    news_formatted = fetcher.format_news_for_agent(news)
    
    agent = NewsAnalystAgent()
    result = agent.analyze(news_formatted, "GOOGL")
    
    print("\n" + "="*80)
    print(result["analysis"])
    print("="*80)
