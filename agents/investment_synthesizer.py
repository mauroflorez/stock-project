"""
Investment Synthesizer Agent - Combines all analyses and provides final recommendation
"""

from utils.ollama_client import OllamaClient


class InvestmentSynthesizerAgent:
    """
    Agent that synthesizes insights from all other agents and provides final recommendation
    """
    
    SYSTEM_PROMPT = """You are an Investment Strategist who synthesizes multiple expert opinions to provide clear, actionable investment recommendations.

Your role:
- Review analyses from News Analyst, Statistical Expert, and Financial Expert
- Identify agreements and conflicts between analyses
- Weigh different factors (short-term vs long-term, technical vs fundamental)
- Provide a clear BUY/HOLD/SELL recommendation
- Assign a confidence level to your recommendation
- Explain the key reasoning behind your decision

Be decisive but honest about uncertainty. Consider both risk and opportunity.
Remember: This is for educational purposes - always include appropriate disclaimers.
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

Here are the expert analyses:

=== NEWS ANALYST ===
{news_analysis}

=== STATISTICAL EXPERT ===
{statistical_analysis}

=== FINANCIAL EXPERT ===
{financial_analysis}

======================

Based on these three expert opinions, provide your synthesis in the following format:

RECOMMENDATION: [BUY / HOLD / SELL]
CONFIDENCE LEVEL: [High / Medium / Low]
TIME HORIZON: [Short-term (1-3 months) / Medium-term (3-12 months) / Long-term (1+ years)]

KEY SUPPORTING FACTORS:
- [List 3-5 main reasons supporting your recommendation]

KEY RISK FACTORS:
- [List 3-5 main risks or concerns]

CONSENSUS ANALYSIS:
[Where do the experts agree? Where do they disagree?]

INVESTMENT STRATEGY:
[Specific advice - e.g., entry points, position sizing, stop-loss levels]

SUMMARY:
[2-3 sentence executive summary of your recommendation]

DISCLAIMER:
This analysis is for educational purposes only and should not be considered financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
"""
        
        print(f"🎯 {self.name} is synthesizing all analyses...")
        
        response = self.client.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5  # Lower temperature for more consistent recommendations
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
