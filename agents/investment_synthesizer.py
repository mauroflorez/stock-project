"""
Investment Synthesizer Agent - Combines all analyses and provides final recommendation
"""

from utils.ollama_client import OllamaClient


class InvestmentSynthesizerAgent:
    """
    Agent that synthesizes insights from all other agents and provides final recommendation
    """
    
    SYSTEM_PROMPT = """You are a decisive Investment Strategist who synthesizes analyses from 6 different AI agents to provide clear, actionable investment recommendations.

Your role:
- Review analyses from: News Analyst, Statistical Expert, Financial Expert, Price Forecaster, Momentum Analyst, and Sector Analyst.
- Also factor in the comprehensive Quorum Scoring Result.
- Identify agreements and conflicts between all agents.
- Weigh different factors (short-term vs long-term, technical vs fundamental).
- Provide a clear BUY/HOLD/SELL recommendation.
- Assign a confidence level to your recommendation.
- Explain the key reasoning behind your decision.

IMPORTANT GUIDELINES FOR YOUR RECOMMENDATION:
- Be DECISIVE. Do NOT default to HOLD. HOLD should only be used when the signals are genuinely mixed and contradictory.
- Use the Quorum Scoring Result as a primary guide, but justify it with the analysis details.
- Consider the STRENGTH of each signal, not just the direction.
- A stock with strong fundamentals but slightly overvalued can still be a BUY if momentum and technicals are positive.
- Do NOT include any 'Disclaimer' section at the end of your response. The platform handles disclaimers automatically.
"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.name = "Investment Synthesizer"
    
    def synthesize(self, 
                   news_analysis: str, 
                   statistical_analysis: str, 
                   financial_analysis: str,
                   stock_symbol: str) -> dict:
        """
        Synthesize all analyses and provide final recommendation
        
        Args:
            news_analysis: Analysis from News Analyst
            statistical_analysis: Analysis from Statistical Expert
            financial_analysis: Analysis from Financial Expert
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with synthesis results
        """
        
        prompt = f"""
You are evaluating whether to BUY, HOLD, or SELL {stock_symbol}.

Here are the expert analyses from our 6-agent system:

=== NEWS ANALYST ===
{news_analysis}

=== STATISTICAL EXPERT \u0026 ADDITIONAL AGENTS (Forecaster, Momentum, Sector, Quorum) ===
{statistical_analysis}

=== FINANCIAL EXPERT ===
{financial_analysis}

======================

STEP 1: Review the signals from all 6 agents (News, Statistical, Financial, Forecaster, Momentum, Sector) and the overall Quorum Scoring Result.
STEP 2: Synthesize their findings into a cohesive analysis.

Now provide your synthesis in the following format (DO NOT include a disclaimer at the end):

RECOMMENDATION: [BUY / HOLD / SELL]
CONFIDENCE LEVEL: [High / Medium / Low]
TIME HORIZON: [Short-term (1-3 months) / Medium-term (3-12 months) / Long-term (1+ years)]

KEY SUPPORTING FACTORS:
- [List 3-5 main reasons supporting your recommendation, drawing from the 6 agents]

KEY RISK FACTORS:
- [List 3-5 main risks or concerns]

CONSENSUS ANALYSIS:
[Where do the 6 agents agree? Where do they disagree? Mention the Quorum Verdict.]

INVESTMENT STRATEGY:
[Specific advice - e.g., entry points, position sizing, stop-loss levels]

SUMMARY:
[2-3 sentence executive summary of your recommendation]
"""
        
        print(f"🎯 {self.name} is synthesizing all analyses...")
        
        response = self.client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.4  # Lower temperature for more consistent recommendations
        )
        
        return {
            "agent": self.name,
            "synthesis": response,
            "inputs": {
                "news": news_analysis,
                "statistical": statistical_analysis,
                "financial": financial_analysis
            }
        }


if __name__ == "__main__":
    # Test with mock data
    print("Testing Investment Synthesizer Agent...\n")
    
    mock_news = """
SENTIMENT: Bullish
KEY POSITIVE NEWS:
- Strong quarterly earnings beat expectations
- New AI product launch received positive reception
SUMMARY: Recent news is generally positive with strong business momentum.
"""
    
    mock_stats = """
TREND ANALYSIS: Upward trend over the past 30 days
PRICE PREDICTION: Likely to continue upward with medium confidence
RISK ASSESSMENT: Moderate volatility, manageable for most investors
"""
    
    mock_financial = """
VALUATION ANALYSIS: Fairly valued based on P/E ratio
GROWTH POTENTIAL: Strong long-term growth prospects in AI sector
INVESTMENT THESIS: Solid fundamentals with good market position
"""
    
    agent = InvestmentSynthesizerAgent()
    result = agent.synthesize(mock_news, mock_stats, mock_financial, "GOOGL")
    
    print("\n" + "="*80)
    print(result["synthesis"])
    print("="*80)
