"""
Statistical Expert Agent - Performs time series analysis and predictions
"""

from utils.ollama_client import OllamaClient
import numpy as np
from typing import Dict, List


class StatisticalExpertAgent:
    """
    Agent specialized in statistical analysis and time series forecasting
    Uses both traditional statistical methods and LLM interpretation
    """
    
    SYSTEM_PROMPT = """You are a Statistical Expert specializing in time series analysis and stock price forecasting.

Your role:
- Analyze historical stock price data
- Identify trends, patterns, and volatility
- Interpret statistical metrics
- Provide data-driven predictions
- Assess the reliability of forecasts

Be precise, use statistical terminology correctly, and always acknowledge uncertainty.
Focus on what the data shows, not speculation.
"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.name = "Statistical Expert"
    
    def calculate_statistics(self, prices: List[float]) -> Dict:
        """Calculate basic statistical metrics"""
        prices_array = np.array(prices)
        
        # Calculate returns
        returns = np.diff(prices_array) / prices_array[:-1] * 100
        
        # Moving averages
        ma_7 = np.mean(prices_array[-7:]) if len(prices_array) >= 7 else np.mean(prices_array)
        ma_30 = np.mean(prices_array[-30:]) if len(prices_array) >= 30 else np.mean(prices_array)
        
        # Volatility (standard deviation of returns)
        volatility = np.std(returns) if len(returns) > 0 else 0
        
        # Trend (simple linear regression slope)
        if len(prices_array) > 1:
            x = np.arange(len(prices_array))
            slope = np.polyfit(x, prices_array, 1)[0]
            trend = "Upward" if slope > 0 else "Downward" if slope < 0 else "Flat"
        else:
            slope = 0
            trend = "Insufficient data"
        
        return {
            "current_price": prices_array[-1],
            "avg_price_7d": ma_7,
            "avg_price_30d": ma_30,
            "volatility": volatility,
            "avg_return": np.mean(returns) if len(returns) > 0 else 0,
            "max_return": np.max(returns) if len(returns) > 0 else 0,
            "min_return": np.min(returns) if len(returns) > 0 else 0,
            "trend": trend,
            "trend_slope": slope,
            "price_range": (np.min(prices_array), np.max(prices_array))
        }
    
    def analyze(self, price_data: str, prices: List[float], stock_symbol: str) -> dict:
        """
        Perform statistical analysis on price data
        
        Args:
            price_data: Formatted price data as string
            prices: List of historical prices
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with analysis results
        """
        
        # First, calculate statistics
        stats = self.calculate_statistics(prices)
        
        stats_summary = f"""
STATISTICAL METRICS:
- Current Price: ${stats['current_price']:.2f}
- 7-Day Moving Average: ${stats['avg_price_7d']:.2f}
- 30-Day Moving Average: ${stats['avg_price_30d']:.2f}
- Volatility (Std Dev of Returns): {stats['volatility']:.2f}%
- Average Daily Return: {stats['avg_return']:.2f}%
- Max Daily Return: {stats['max_return']:.2f}%
- Min Daily Return: {stats['min_return']:.2f}%
- Trend: {stats['trend']} (slope: {stats['trend_slope']:.4f})
- Price Range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}
"""
        
        prompt = f"""
Analyze the following statistical data for {stock_symbol}:

{stats_summary}

Historical Price Data:
{price_data}

Provide your analysis in the following format:

TREND ANALYSIS:
[Describe the overall trend - is it bullish, bearish, or sideways?]

VOLATILITY ASSESSMENT:
[Comment on the price volatility - is it high, low, stable?]

MOVING AVERAGES:
[Interpret the relationship between current price and moving averages]

PRICE PREDICTION (NEXT 7 DAYS):
[Based on the statistical patterns, provide a cautious prediction]
[Include confidence level: High/Medium/Low]

STATISTICAL INSIGHTS:
[Key takeaways from the data]

RISK ASSESSMENT:
[Comment on the risk based on volatility and trends]
"""
        
        print(f"📈 {self.name} is analyzing price data...")
        
        response = self.client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT
        )
        
        return {
            "agent": self.name,
            "analysis": response,
            "statistics": stats,
            "raw_data": price_data
        }


if __name__ == "__main__":
    # Test the agent
    from utils.data_fetcher import DataFetcher
    
    print("Testing Statistical Expert Agent...\n")
    
    fetcher = DataFetcher()
    stock_data = fetcher.get_stock_prices("GOOGL", days=60)
    price_formatted = fetcher.format_price_data_for_agent(stock_data)
    
    agent = StatisticalExpertAgent()
    result = agent.analyze(
        price_formatted, 
        stock_data['historical_close'], 
        "GOOGL"
    )
    
    print("\n" + "="*80)
    print(result["analysis"])
    print("\n" + "="*80)
    print("\nCalculated Statistics:")
    for key, value in result["statistics"].items():
        print(f"  {key}: {value}")
