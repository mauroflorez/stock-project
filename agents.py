"""
AI Agents Module
Four specialized agents for stock analysis
"""

from ollama_utils import OllamaAgent
from typing import Dict, List
import pandas as pd


class NewsAnalystAgent(OllamaAgent):
    """Agent 1: Analyzes recent news about the stock"""
    
    def __init__(self):
        system_prompt = """You are a financial news analyst expert. Your job is to analyze recent news articles about a stock and provide a concise summary of:
1. Overall sentiment (bullish, bearish, or neutral)
2. Key events or developments mentioned
3. Potential impact on stock price
4. Any risks or concerns mentioned

Be objective and fact-based. Limit your response to 200 words."""
        
        super().__init__(role="News Analyst", system_prompt=system_prompt)
    
    def analyze(self, ticker: str, company_name: str, news_articles: List[Dict]) -> str:
        """
        Analyze news articles and return summary
        """
        if not news_articles:
            return "No recent news articles found for analysis."
        
        # Format news for the agent
        news_text = f"Recent news about {company_name} ({ticker}):\n\n"
        for i, article in enumerate(news_articles, 1):
            news_text += f"{i}. {article['title']}\n"
            news_text += f"   Source: {article['source']}, Date: {article['published']}\n"
            if article.get('summary'):
                news_text += f"   Summary: {article['summary']}\n"
            news_text += "\n"
        
        prompt = f"{news_text}\n\nProvide a concise analysis of these news articles."
        
        return self.generate(prompt)


class StatisticalAnalystAgent(OllamaAgent):
    """Agent 2: Statistical analysis and predictions using time series"""
    
    def __init__(self):
        system_prompt = """You are a quantitative analyst and statistician expert in time series analysis. Given stock price data and statistical predictions, provide:
1. Analysis of recent price trends and patterns
2. Interpretation of the statistical predictions
3. Key statistics (volatility, momentum, etc.)
4. Statistical confidence in predictions

Be technical but clear. Limit your response to 250 words."""
        
        super().__init__(role="Statistical Analyst", system_prompt=system_prompt)
    
    def analyze(self, ticker: str, historical_data: pd.DataFrame, 
                predictions: Dict) -> str:
        """
        Analyze statistical data and predictions
        """
        # Calculate key statistics
        latest_price = historical_data['Close'].iloc[-1]
        price_30d_ago = historical_data['Close'].iloc[-30] if len(historical_data) >= 30 else historical_data['Close'].iloc[0]
        month_return = ((latest_price - price_30d_ago) / price_30d_ago) * 100
        
        volatility = historical_data['Close'].pct_change().std() * 100
        
        # Format data for agent
        stats_text = f"""Stock: {ticker}
Current Price: ${latest_price:.2f}
30-Day Return: {month_return:.2f}%
30-Day Volatility: {volatility:.2f}%

Recent Price History (last 10 days):
{historical_data[['Close']].tail(10).to_string()}

Statistical Predictions:
- Method: {predictions.get('method', 'N/A')}
- Predicted Trend: {predictions.get('trend', 'N/A')}
- Confidence Level: {predictions.get('confidence', 'N/A')}
- 30-Day Forecast: {predictions.get('forecast_summary', 'N/A')}
"""
        
        prompt = f"{stats_text}\n\nProvide your statistical analysis and interpretation."
        
        return self.generate(prompt)


class FinancialExpertAgent(OllamaAgent):
    """Agent 3: Company fundamentals and financial expert"""
    
    def __init__(self):
        system_prompt = """You are a fundamental analysis expert with deep knowledge of companies and financial metrics. Given company information, provide:
1. Company overview and business model assessment
2. Valuation analysis (P/E ratio, market cap, etc.)
3. Long-term prospects and competitive position
4. Financial health indicators

Be insightful and forward-looking. Limit your response to 250 words."""
        
        super().__init__(role="Financial Expert", system_prompt=system_prompt)
    
    def analyze(self, ticker: str, company_info: Dict, 
                historical_data: pd.DataFrame) -> str:
        """
        Analyze company fundamentals
        """
        current_price = historical_data['Close'].iloc[-1]
        year_ago_price = historical_data['Close'].iloc[-252] if len(historical_data) >= 252 else historical_data['Close'].iloc[0]
        year_return = ((current_price - year_ago_price) / year_ago_price) * 100
        
        # Format company data
        company_text = f"""Company: {company_info.get('name', ticker)}
Ticker: {ticker}
Sector: {company_info.get('sector', 'N/A')}
Industry: {company_info.get('industry', 'N/A')}

Financial Metrics:
- Current Price: ${company_info.get('current_price', current_price):.2f}
- Market Cap: ${company_info.get('market_cap', 0):,.0f}
- P/E Ratio: {company_info.get('pe_ratio', 'N/A')}
- 52-Week High: ${company_info.get('52_week_high', 0):.2f}
- 52-Week Low: ${company_info.get('52_week_low', 0):.2f}
- 1-Year Return: {year_return:.2f}%

Business Description:
{company_info.get('description', 'N/A')[:500]}...
"""
        
        prompt = f"{company_text}\n\nProvide your fundamental analysis of this company."
        
        return self.generate(prompt)


class SynthesisAgent(OllamaAgent):
    """Agent 4: Synthesizes all analyses into final recommendation"""
    
    def __init__(self):
        system_prompt = """You are a senior investment advisor synthesizing multiple expert analyses. Given analyses from news, statistical, and fundamental experts, provide:
1. Overall investment thesis
2. Clear recommendation: BUY, HOLD, or SELL
3. Key supporting reasons
4. Main risks to consider
5. Suggested action and time horizon

Be decisive but balanced. Acknowledge uncertainties. Limit response to 300 words.

IMPORTANT: Always include a disclaimer that this is not professional financial advice."""
        
        super().__init__(role="Investment Synthesizer", system_prompt=system_prompt)
    
    def synthesize(self, ticker: str, company_name: str, 
                   news_analysis: str, 
                   statistical_analysis: str,
                   fundamental_analysis: str,
                   current_price: float) -> str:
        """
        Synthesize all analyses into final recommendation
        """
        synthesis_prompt = f"""Stock Analysis for {company_name} ({ticker})
Current Price: ${current_price:.2f}

=== NEWS ANALYST REPORT ===
{news_analysis}

=== STATISTICAL ANALYST REPORT ===
{statistical_analysis}

=== FUNDAMENTAL ANALYST REPORT ===
{fundamental_analysis}

=== YOUR TASK ===
Synthesize these three expert analyses and provide your final investment recommendation with clear reasoning."""
        
        return self.generate(synthesis_prompt, max_tokens=5000)


def test_agents():
    """Test the agents with sample data"""
    print("Testing AI Agents...")
    
    # Test News Analyst
    print("\n1. Testing News Analyst...")
    news_agent = NewsAnalystAgent()
    sample_news = [
        {"title": "Google announces new AI products", "source": "TechCrunch", 
         "published": "2024-01-15", "summary": "Major AI launch"},
        {"title": "Alphabet stock rises on strong earnings", "source": "CNBC",
         "published": "2024-01-14", "summary": "Q4 results beat expectations"}
    ]
    result = news_agent.analyze("GOOGL", "Google", sample_news)
    print(f"   Result: {result[:100]}...")
    
    print("\n✓ Agent testing complete!")


if __name__ == "__main__":
    test_agents()
