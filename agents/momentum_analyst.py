"""
Momentum Analyst Agent - Evaluates price momentum, relative strength, and volume trends
Pure Python computation - no LLM needed for signal generation
"""

import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class MomentumAnalystAgent:
    """
    Agent that computes momentum-based signals:
    - Relative Strength vs S&P 500 (SPY)
    - Rate of Change (ROC) at multiple timeframes
    - On-Balance Volume (OBV) trend
    - Price vs key moving averages
    """
    
    def __init__(self):
        self.name = "Momentum Analyst"
        self._spy_cache = None
    
    def _get_spy_returns(self, days: int = 60) -> Optional[np.ndarray]:
        """Fetch S&P 500 (SPY) returns for relative strength calculation"""
        if self._spy_cache is not None:
            return self._spy_cache
        try:
            spy = yf.Ticker("SPY")
            end = datetime.now()
            start = end - timedelta(days=days + 10)
            hist = spy.history(start=start, end=end)
            if not hist.empty:
                closes = hist['Close'].values
                self._spy_cache = np.diff(closes) / closes[:-1]
                return self._spy_cache
        except Exception:
            pass
        return None
    
    def analyze(self, prices: List[float], volumes: List[float], 
                stock_symbol: str) -> Dict[str, Any]:
        """
        Compute momentum signals from price and volume data.
        
        Args:
            prices: Historical closing prices
            volumes: Historical volume data
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with momentum analysis results
        """
        prices_arr = np.array(prices)
        volumes_arr = np.array(volumes) if volumes else None
        
        score = 0.0
        reasons = []
        
        # 1. Rate of Change (multiple timeframes)
        roc_5 = self._rate_of_change(prices_arr, 5)
        roc_10 = self._rate_of_change(prices_arr, 10)
        roc_20 = self._rate_of_change(prices_arr, 20)
        
        if roc_5 is not None:
            if roc_5 > 3:
                score += 0.5
                reasons.append(f"5-day ROC: +{roc_5:.1f}% (strong short-term momentum)")
            elif roc_5 < -3:
                score -= 0.5
                reasons.append(f"5-day ROC: {roc_5:.1f}% (weak short-term momentum)")
        
        if roc_20 is not None:
            if roc_20 > 5:
                score += 0.5
                reasons.append(f"20-day ROC: +{roc_20:.1f}% (strong medium-term momentum)")
            elif roc_20 < -5:
                score -= 0.5
                reasons.append(f"20-day ROC: {roc_20:.1f}% (weak medium-term momentum)")
        
        # 2. Relative Strength vs S&P 500
        spy_returns = self._get_spy_returns()
        if spy_returns is not None and len(prices_arr) > 20:
            stock_returns = np.diff(prices_arr) / prices_arr[:-1]
            # Compare last 20 days
            min_len = min(20, len(stock_returns), len(spy_returns))
            stock_perf = np.sum(stock_returns[-min_len:]) * 100
            spy_perf = np.sum(spy_returns[-min_len:]) * 100
            rel_strength = stock_perf - spy_perf
            
            if rel_strength > 3:
                score += 1.0
                reasons.append(f"Outperforming S&P 500 by {rel_strength:.1f}pp (20d)")
            elif rel_strength < -3:
                score -= 1.0
                reasons.append(f"Underperforming S&P 500 by {abs(rel_strength):.1f}pp (20d)")
            else:
                reasons.append(f"Tracking S&P 500 (diff: {rel_strength:+.1f}pp)")
        
        # 3. Volume analysis (if available)
        if volumes_arr is not None and len(volumes_arr) > 20:
            obv_signal = self._obv_trend(prices_arr, volumes_arr)
            avg_vol_recent = np.mean(volumes_arr[-5:])
            avg_vol_longer = np.mean(volumes_arr[-20:])
            vol_ratio = avg_vol_recent / avg_vol_longer if avg_vol_longer > 0 else 1.0
            
            if obv_signal == "accumulation":
                score += 0.5
                reasons.append(f"OBV trending up (accumulation, vol ratio: {vol_ratio:.2f}x)")
            elif obv_signal == "distribution":
                score -= 0.5
                reasons.append(f"OBV trending down (distribution, vol ratio: {vol_ratio:.2f}x)")
            
            # Volume surge check
            if vol_ratio > 1.5:
                # High volume in direction of price move
                if roc_5 and roc_5 > 0:
                    score += 0.25
                    reasons.append(f"High volume on rally ({vol_ratio:.1f}x avg)")
                elif roc_5 and roc_5 < 0:
                    score -= 0.25
                    reasons.append(f"High volume on decline ({vol_ratio:.1f}x avg)")
        
        # 4. Trend consistency (are short/medium/long trends aligned?)
        if roc_5 is not None and roc_10 is not None and roc_20 is not None:
            all_positive = roc_5 > 0 and roc_10 > 0 and roc_20 > 0
            all_negative = roc_5 < 0 and roc_10 < 0 and roc_20 < 0
            if all_positive:
                score += 0.5
                reasons.append("All timeframe ROCs positive (consistent uptrend)")
            elif all_negative:
                score -= 0.5
                reasons.append("All timeframe ROCs negative (consistent downtrend)")
        
        # Determine signal
        if score >= 1.0:
            signal = "BULLISH"
        elif score <= -1.0:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"
        
        return {
            "agent": self.name,
            "momentum_signal": signal,
            "momentum_score": round(score, 2),
            "momentum_reasons": reasons,
            "metrics": {
                "roc_5d": roc_5,
                "roc_10d": roc_10,
                "roc_20d": roc_20,
            }
        }
    
    def _rate_of_change(self, prices: np.ndarray, period: int) -> Optional[float]:
        """Calculate Rate of Change (ROC) over a period"""
        if len(prices) <= period:
            return None
        return ((prices[-1] - prices[-period-1]) / prices[-period-1]) * 100
    
    def _obv_trend(self, prices: np.ndarray, volumes: np.ndarray) -> str:
        """Calculate On-Balance Volume trend direction"""
        if len(prices) < 20 or len(volumes) < 20:
            return "neutral"
        
        # Calculate OBV
        obv = [0]
        min_len = min(len(prices), len(volumes))
        for i in range(1, min_len):
            if prices[i] > prices[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif prices[i] < prices[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        obv_arr = np.array(obv)
        
        # Check OBV trend over last 20 periods
        obv_recent = obv_arr[-20:]
        x = np.arange(len(obv_recent))
        slope = np.polyfit(x, obv_recent, 1)[0]
        
        # Normalize slope by average volume
        avg_vol = np.mean(volumes[-20:])
        if avg_vol > 0:
            norm_slope = slope / avg_vol
            if norm_slope > 0.1:
                return "accumulation"
            elif norm_slope < -0.1:
                return "distribution"
        
        return "neutral"


if __name__ == "__main__":
    from utils.data_fetcher import DataFetcher
    from config import STOCK_SYMBOLS
    
    print("Testing Momentum Analyst Agent...\n")
    
    fetcher = DataFetcher()
    agent = MomentumAnalystAgent()
    
    for symbol in STOCK_SYMBOLS[:5]:
        data = fetcher.get_stock_prices(symbol, days=60)
        if "error" in data:
            continue
        result = agent.analyze(
            data['historical_close'],
            data.get('historical_volume', []),
            symbol
        )
        print(f"{symbol}: {result['momentum_signal']} (score: {result['momentum_score']})")
        for r in result['momentum_reasons']:
            print(f"  - {r}")
        print()
