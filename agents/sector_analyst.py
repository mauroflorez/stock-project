"""
Sector Analyst Agent - Evaluates stock performance relative to its sector
Pure Python computation - no LLM needed for signal generation
"""

import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


# Sector ETF mapping
SECTOR_ETFS = {
    "Technology": "XLK",
    "Communication Services": "XLC",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Healthcare": "XLV",
    "Financial Services": "XLF",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Basic Materials": "XLB",
}


class SectorAnalystAgent:
    """
    Agent that evaluates a stock's position within its sector:
    - Performance vs sector ETF
    - Beta relative to sector
    - Sector momentum
    """
    
    def __init__(self):
        self.name = "Sector Analyst"
        self._etf_cache = {}
    
    def _get_etf_data(self, etf_symbol: str, days: int = 60) -> Optional[Dict]:
        """Fetch sector ETF price data"""
        if etf_symbol in self._etf_cache:
            return self._etf_cache[etf_symbol]
        try:
            etf = yf.Ticker(etf_symbol)
            end = datetime.now()
            start = end - timedelta(days=days + 10)
            hist = etf.history(start=start, end=end)
            if not hist.empty:
                data = {
                    'closes': hist['Close'].values,
                    'returns': np.diff(hist['Close'].values) / hist['Close'].values[:-1]
                }
                self._etf_cache[etf_symbol] = data
                return data
        except Exception:
            pass
        return None
    
    def analyze(self, prices: List[float], sector: str, 
                stock_symbol: str) -> Dict[str, Any]:
        """
        Analyze stock's position within its sector.
        
        Args:
            prices: Historical closing prices
            sector: Stock's sector (from yfinance)
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with sector analysis results
        """
        prices_arr = np.array(prices)
        score = 0.0
        reasons = []
        
        # Find corresponding sector ETF
        etf_symbol = SECTOR_ETFS.get(sector)
        sector_comparison = None
        
        if etf_symbol:
            etf_data = self._get_etf_data(etf_symbol)
            if etf_data is not None:
                stock_returns = np.diff(prices_arr) / prices_arr[:-1]
                etf_returns = etf_data['returns']
                
                # Compare last 20 days performance
                min_len = min(20, len(stock_returns), len(etf_returns))
                if min_len > 5:
                    stock_perf = np.sum(stock_returns[-min_len:]) * 100
                    etf_perf = np.sum(etf_returns[-min_len:]) * 100
                    rel_perf = stock_perf - etf_perf
                    
                    sector_comparison = {
                        'etf': etf_symbol,
                        'stock_return_20d': round(stock_perf, 2),
                        'sector_return_20d': round(etf_perf, 2),
                        'relative_performance': round(rel_perf, 2)
                    }
                    
                    if rel_perf > 5:
                        score += 1.0
                        reasons.append(f"Sector leader: +{rel_perf:.1f}pp vs {etf_symbol} (20d)")
                    elif rel_perf > 2:
                        score += 0.5
                        reasons.append(f"Outperforming sector by {rel_perf:.1f}pp vs {etf_symbol}")
                    elif rel_perf < -5:
                        score -= 1.0
                        reasons.append(f"Sector laggard: {rel_perf:.1f}pp vs {etf_symbol} (20d)")
                    elif rel_perf < -2:
                        score -= 0.5
                        reasons.append(f"Underperforming sector by {abs(rel_perf):.1f}pp vs {etf_symbol}")
                    else:
                        reasons.append(f"In-line with sector ({rel_perf:+.1f}pp vs {etf_symbol})")
                    
                    # Sector momentum (is the sector itself trending?)
                    if etf_perf > 3:
                        score += 0.5
                        reasons.append(f"Sector ({sector}) in uptrend: +{etf_perf:.1f}% (20d)")
                    elif etf_perf < -3:
                        score -= 0.5
                        reasons.append(f"Sector ({sector}) in downtrend: {etf_perf:.1f}% (20d)")
        else:
            reasons.append(f"No sector ETF mapping for '{sector}'")
        
        # Price momentum within range (regardless of sector)
        if len(prices_arr) >= 20:
            perf_20d = ((prices_arr[-1] - prices_arr[-20]) / prices_arr[-20]) * 100
            if perf_20d > 8:
                score += 0.5
                reasons.append(f"Strong absolute momentum: +{perf_20d:.1f}% (20d)")
            elif perf_20d < -8:
                score -= 0.5
                reasons.append(f"Weak absolute momentum: {perf_20d:.1f}% (20d)")
        
        # Determine signal
        if score >= 1.0:
            signal = "BULLISH"
        elif score <= -1.0:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"
        
        return {
            "agent": self.name,
            "sector_signal": signal,
            "sector_score": round(score, 2),
            "sector_reasons": reasons,
            "sector": sector,
            "sector_comparison": sector_comparison
        }


if __name__ == "__main__":
    from utils.data_fetcher import DataFetcher
    from config import STOCK_SYMBOLS
    
    print("Testing Sector Analyst Agent...\n")
    
    fetcher = DataFetcher()
    agent = SectorAnalystAgent()
    
    for symbol in STOCK_SYMBOLS[:5]:
        data = fetcher.get_stock_prices(symbol, days=60)
        if "error" in data:
            continue
        result = agent.analyze(
            data['historical_close'],
            data.get('sector', 'Unknown'),
            symbol
        )
        print(f"{symbol} ({data.get('sector','?')}): {result['sector_signal']} (score: {result['sector_score']})")
        for r in result['sector_reasons']:
            print(f"  - {r}")
        print()
