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
        """Calculate comprehensive statistical and technical metrics"""
        prices_array = np.array(prices)
        
        # Calculate returns
        returns = np.diff(prices_array) / prices_array[:-1] * 100
        
        # Moving averages
        ma_7 = np.mean(prices_array[-7:]) if len(prices_array) >= 7 else np.mean(prices_array)
        ma_20 = np.mean(prices_array[-20:]) if len(prices_array) >= 20 else np.mean(prices_array)
        ma_30 = np.mean(prices_array[-30:]) if len(prices_array) >= 30 else np.mean(prices_array)
        ma_50 = np.mean(prices_array[-50:]) if len(prices_array) >= 50 else np.mean(prices_array)
        ma_200 = np.mean(prices_array) if len(prices_array) >= 200 else None  # Need full history
        
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
        
        # === RSI (14-day) ===
        rsi = self._calculate_rsi(prices_array, period=14)
        
        # === MACD (12, 26, 9) ===
        macd_line, signal_line, macd_hist = self._calculate_macd(prices_array)
        
        # === Bollinger Bands (20-day, 2 std) ===
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger(prices_array, period=20)
        
        # === Compute deterministic technical signal ===
        tech_score = 0  # -3 to +3
        tech_reasons = []
        
        # RSI signal
        if rsi is not None:
            if rsi > 70:
                tech_score -= 1
                tech_reasons.append(f"RSI={rsi:.0f} (overbought)")
            elif rsi < 30:
                tech_score += 1
                tech_reasons.append(f"RSI={rsi:.0f} (oversold, bullish)")
            else:
                tech_reasons.append(f"RSI={rsi:.0f} (neutral zone)")
        
        # MACD signal
        if macd_hist is not None:
            if macd_hist > 0 and macd_line > signal_line:
                tech_score += 1
                tech_reasons.append("MACD above signal (bullish crossover)")
            elif macd_hist < 0 and macd_line < signal_line:
                tech_score -= 1
                tech_reasons.append("MACD below signal (bearish crossover)")
        
        # Price vs Bollinger Bands
        current = prices_array[-1]
        if bb_upper is not None:
            if current > bb_upper:
                tech_score -= 1
                tech_reasons.append(f"Price above upper Bollinger (${bb_upper:.2f})")
            elif current < bb_lower:
                tech_score += 1
                tech_reasons.append(f"Price below lower Bollinger (${bb_lower:.2f})")
        
        # Golden/Death cross (50 vs 200 MA)
        if ma_200 is not None:
            if ma_50 > ma_200:
                tech_score += 0.5
                tech_reasons.append("Golden Cross (50MA > 200MA)")
            elif ma_50 < ma_200:
                tech_score -= 0.5
                tech_reasons.append("Death Cross (50MA < 200MA)")
        
        # Price vs 50-day MA
        if current > ma_50:
            tech_score += 0.5
            tech_reasons.append(f"Price above 50-day MA (${ma_50:.2f})")
        else:
            tech_score -= 0.5
            tech_reasons.append(f"Price below 50-day MA (${ma_50:.2f})")
        
        # Determine signal
        if tech_score >= 1:
            technical_signal = "BULLISH"
        elif tech_score <= -1:
            technical_signal = "BEARISH"
        else:
            technical_signal = "NEUTRAL"
        
        return {
            "current_price": prices_array[-1],
            "avg_price_7d": ma_7,
            "avg_price_20d": ma_20,
            "avg_price_30d": ma_30,
            "avg_price_50d": ma_50,
            "avg_price_200d": ma_200,
            "volatility": volatility,
            "avg_return": np.mean(returns) if len(returns) > 0 else 0,
            "max_return": np.max(returns) if len(returns) > 0 else 0,
            "min_return": np.min(returns) if len(returns) > 0 else 0,
            "trend": trend,
            "trend_slope": slope,
            "price_range": (np.min(prices_array), np.max(prices_array)),
            "rsi_14": rsi,
            "macd_line": macd_line,
            "macd_signal": signal_line,
            "macd_histogram": macd_hist,
            "bollinger_upper": bb_upper,
            "bollinger_middle": bb_middle,
            "bollinger_lower": bb_lower,
            "technical_signal": technical_signal,
            "technical_score": tech_score,
            "technical_reasons": tech_reasons
        }
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        # Smoothed RSI using Wilder's method
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: np.ndarray, fast=12, slow=26, signal=9):
        """Calculate MACD line, signal line, and histogram"""
        if len(prices) < slow + signal:
            return None, None, None
        
        def ema(data, period):
            multiplier = 2 / (period + 1)
            result = [data[0]]
            for i in range(1, len(data)):
                result.append((data[i] - result[-1]) * multiplier + result[-1])
            return np.array(result)
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line[-1], signal_line[-1], histogram[-1]
    
    def _calculate_bollinger(self, prices: np.ndarray, period=20, num_std=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        recent = prices[-period:]
        middle = np.mean(recent)
        std = np.std(recent)
        upper = middle + num_std * std
        lower = middle - num_std * std
        
        return upper, middle, lower
    
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
        
        # Calculate comprehensive statistics + technical indicators
        stats = self.calculate_statistics(prices)
        
        # Build a rich summary for the LLM
        rsi_str = f"{stats['rsi_14']:.1f}" if stats['rsi_14'] is not None else "N/A"
        macd_str = f"{stats['macd_line']:.2f}" if stats['macd_line'] is not None else "N/A"
        macd_sig_str = f"{stats['macd_signal']:.2f}" if stats['macd_signal'] is not None else "N/A"
        bb_upper_str = f"${stats['bollinger_upper']:.2f}" if stats['bollinger_upper'] is not None else "N/A"
        bb_lower_str = f"${stats['bollinger_lower']:.2f}" if stats['bollinger_lower'] is not None else "N/A"
        ma_200_str = f"${stats['avg_price_200d']:.2f}" if stats['avg_price_200d'] is not None else "N/A (need more data)"
        
        stats_summary = f"""
COMPUTED TECHNICAL SIGNAL: {stats['technical_signal']} (score: {stats['technical_score']:.1f})
Signal reasoning:
{chr(10).join('  - ' + r for r in stats['technical_reasons'])}

STATISTICAL METRICS:
- Current Price: ${stats['current_price']:.2f}
- 7-Day Moving Average: ${stats['avg_price_7d']:.2f}
- 20-Day Moving Average: ${stats['avg_price_20d']:.2f}
- 50-Day Moving Average: ${stats['avg_price_50d']:.2f}
- 200-Day Moving Average: {ma_200_str}
- Volatility (Std Dev of Returns): {stats['volatility']:.2f}%
- Average Daily Return: {stats['avg_return']:.2f}%
- Max Daily Return: {stats['max_return']:.2f}%
- Min Daily Return: {stats['min_return']:.2f}%
- Trend: {stats['trend']} (slope: {stats['trend_slope']:.4f})
- Price Range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}

TECHNICAL INDICATORS:
- RSI (14-day): {rsi_str}  [<30 = oversold/bullish, >70 = overbought/bearish]
- MACD Line: {macd_str}  |  Signal Line: {macd_sig_str}  [MACD > Signal = bullish]
- Bollinger Upper: {bb_upper_str}  |  Lower: {bb_lower_str}  [Price outside bands = extreme]
"""
        
        prompt = f"""
Analyze the following statistical data and technical indicators for {stock_symbol}:

{stats_summary}

Historical Price Data (recent):
{price_data}

The technical signal has been computed as {stats['technical_signal']}.
Use this as your primary guidance but explain WHY based on the indicators.

Provide your analysis in the following format:

SIGNAL: {stats['technical_signal']}

TREND ANALYSIS:
[Describe the overall trend based on moving averages and slope]

TECHNICAL INDICATORS:
[Interpret RSI, MACD, and Bollinger Bands - what do they tell us?]

VOLATILITY ASSESSMENT:
[Comment on the price volatility]

PRICE PREDICTION (NEXT 7 DAYS):
[Based on the technical indicators, provide a prediction]
[Include confidence level: High/Medium/Low]

STATISTICAL INSIGHTS:
[Key takeaways - be specific about numbers]

RISK ASSESSMENT:
[Comment on the risk based on volatility and technical signals]
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
