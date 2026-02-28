"""
Financial Expert Agent - Provides fundamental analysis and company insights
Now with deterministic fundamental scoring based on real financial metrics
"""

from utils.ollama_client import OllamaClient
from typing import Dict, Any, Optional


class FinancialExpertAgent:
    """
    Agent specialized in fundamental analysis and company evaluation
    Now computes a deterministic fundamental signal from real financial data
    """
    
    SYSTEM_PROMPT = """You are a Financial Expert specializing in fundamental analysis and company valuation.

Your role:
- Analyze company fundamentals (P/E, PEG, ROE, margins, debt ratios)
- Evaluate the company's competitive position
- Assess financial health and growth potential
- Consider industry trends and market conditions
- Provide long-term investment perspective

Use specific numbers from the data provided. Be definitive in your valuation assessment.
Do NOT default to "fairly valued" - take a clear position based on the metrics.
"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.name = "Financial Expert"
    
    def compute_fundamental_signal(self, stock_data: Dict[str, Any]) -> Dict:
        """
        Compute a deterministic fundamental signal from financial metrics.
        Returns a dict with signal, score, and reasoning.
        """
        score = 0.0  # -3 to +3
        reasons = []
        
        # 1. PEG Ratio (most reliable single valuation metric)
        peg = stock_data.get('peg_ratio')
        if peg is not None:
            if peg < 1.0:
                score += 1.5
                reasons.append(f"PEG={peg:.2f} (<1.0 = undervalued relative to growth)")
            elif peg < 1.5:
                score += 0.5
                reasons.append(f"PEG={peg:.2f} (reasonably valued)")
            elif peg > 2.5:
                score -= 1.5
                reasons.append(f"PEG={peg:.2f} (>2.5 = expensive relative to growth)")
            elif peg > 1.5:
                score -= 0.5
                reasons.append(f"PEG={peg:.2f} (slightly expensive)")
        
        # 2. Absolute P/E level (high P/E = expensive regardless of growth)
        pe = stock_data.get('pe_ratio')
        fwd_pe = stock_data.get('forward_pe')
        if pe is not None:
            if pe > 100:
                score -= 1.0
                reasons.append(f"P/E={pe:.0f} (>100 = extremely expensive)")
            elif pe > 40:
                score -= 0.5
                reasons.append(f"P/E={pe:.0f} (>40 = expensive)")
            elif pe < 15:
                score += 0.5
                reasons.append(f"P/E={pe:.0f} (<15 = value territory)")
        
        # 3. P/E vs Forward P/E (earnings momentum)
        if pe is not None and fwd_pe is not None:
            if fwd_pe < pe * 0.80:  # Forward P/E 20%+ lower
                score += 0.5
                reasons.append(f"Forward P/E ({fwd_pe:.1f}) << Trailing P/E ({pe:.1f}): earnings accelerating")
            elif fwd_pe > pe * 1.1:
                score -= 0.5
                reasons.append(f"Forward P/E ({fwd_pe:.1f}) > Trailing P/E ({pe:.1f}): earnings decelerating")
        
        # 4. Return on Equity (quality of business)
        roe = stock_data.get('return_on_equity')
        if roe is not None:
            if roe > 0.25:
                score += 0.5
                reasons.append(f"ROE={roe*100:.0f}% (>25% = excellent capital efficiency)")
            elif roe < 0.08:
                score -= 0.5
                reasons.append(f"ROE={roe*100:.0f}% (<8% = poor capital efficiency)")
        
        # 5. Earnings Growth
        eg = stock_data.get('earnings_growth')
        if eg is not None:
            if eg > 0.30:
                score += 0.5
                reasons.append(f"Earnings Growth={eg*100:.0f}% (>30% = strong)")
            elif eg < -0.05:
                score -= 0.5
                reasons.append(f"Earnings Growth={eg*100:.0f}% (negative = declining)")
        
        # 6. Debt-to-Equity
        dte = stock_data.get('debt_to_equity')
        if dte is not None:
            if dte > 200:
                score -= 0.5
                reasons.append(f"Debt/Equity={dte:.0f} (>200 = heavily leveraged)")
            elif dte < 30:
                score += 0.25
                reasons.append(f"Debt/Equity={dte:.0f} (<30 = low leverage)")
        
        # 7. Price vs Analyst Target
        target = stock_data.get('target_mean_price')
        current = stock_data.get('current_price')
        if target is not None and current is not None and current > 0:
            upside = (target - current) / current * 100
            if upside > 20:
                score += 0.5
                reasons.append(f"Analyst target ${target:.0f} → {upside:.0f}% upside")
            elif upside < -10:
                score -= 0.5
                reasons.append(f"Analyst target ${target:.0f} → {upside:.0f}% downside")
        
        # 8. Price vs 52-week range (proximity to highs/lows)
        high_52 = stock_data.get('52_week_high')
        low_52 = stock_data.get('52_week_low')
        if high_52 and low_52 and current and (high_52 - low_52) > 0:
            position = (current - low_52) / (high_52 - low_52)
            if position > 0.90:
                score -= 0.5
                reasons.append(f"Near 52-week high ({position:.0%} of range) = potentially overheated")
            elif position < 0.30:
                score += 0.5
                reasons.append(f"Near 52-week low ({position:.0%} of range) = potential value")
        
        # Determine signal (raised threshold for UNDERVALUED)
        if score >= 1.5:
            signal = "UNDERVALUED"
        elif score <= -1.0:
            signal = "OVERVALUED"
        else:
            signal = "FAIR"
        
        return {
            "signal": signal,
            "score": round(score, 2),
            "reasons": reasons
        }
    
    def analyze(self, stock_data: str, stock_symbol: str, raw_stock_data: Dict = None) -> dict:
        """
        Perform fundamental analysis on the company
        
        Args:
            stock_data: Formatted stock data including fundamentals
            stock_symbol: Stock ticker symbol
            raw_stock_data: Raw data dict (for computing fundamental signal)
            
        Returns:
            Dictionary with analysis results
        """
        
        # Compute deterministic fundamental signal if raw data available
        fund_signal = None
        signal_context = ""
        if raw_stock_data:
            fund_signal = self.compute_fundamental_signal(raw_stock_data)
            signal_context = f"""
COMPUTED FUNDAMENTAL SIGNAL: {fund_signal['signal']} (score: {fund_signal['score']})
Reasoning:
{chr(10).join('  - ' + r for r in fund_signal['reasons'])}
"""
        
        prompt = f"""
Provide a fundamental analysis for {stock_symbol} based on the following data:

{signal_context}

{stock_data}

The fundamental signal has been computed as {fund_signal['signal'] if fund_signal else 'N/A'}.
Use this as your primary guidance but explain WHY based on the financial metrics.

Provide your analysis in the following format:

SIGNAL: {fund_signal['signal'] if fund_signal else 'FAIR'}

COMPANY OVERVIEW:
[Brief description of what the company does and its market position]

VALUATION ANALYSIS:
[Evaluate P/E, PEG, forward P/E and other valuation metrics]
[Is the stock overvalued, undervalued, or fairly valued?]

GROWTH & PROFITABILITY:
[Evaluate earnings growth, revenue growth, profit margins, ROE]

FINANCIAL HEALTH:
[Assess debt levels, cash flow, and overall financial strength]

COMPETITIVE ADVANTAGES:
[Identify key strengths or moats]

RISKS & CONCERNS:
[Highlight potential risks or challenges]

INVESTMENT THESIS:
[Summarize the case for/against investing in this stock]
"""
        
        print(f"💼 {self.name} is analyzing company fundamentals...")
        
        response = self.client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT
        )
        
        result = {
            "agent": self.name,
            "analysis": response,
            "raw_data": stock_data
        }
        
        if fund_signal:
            result["fundamental_signal"] = fund_signal
        
        return result


if __name__ == "__main__":
    # Test the agent
    from utils.data_fetcher import DataFetcher
    
    print("Testing Financial Expert Agent...\n")
    
    fetcher = DataFetcher()
    stock_data = fetcher.get_stock_prices("GOOGL", days=60)
    stock_formatted = fetcher.format_price_data_for_agent(stock_data)
    
    agent = FinancialExpertAgent()
    
    # Test fundamental signal computation
    signal = agent.compute_fundamental_signal(stock_data)
    print(f"Signal: {signal['signal']} (score: {signal['score']})")
    for r in signal['reasons']:
        print(f"  - {r}")
    
    result = agent.analyze(stock_formatted, "GOOGL", raw_stock_data=stock_data)
    
    print("\n" + "="*80)
    print(result["analysis"])
    print("="*80)
