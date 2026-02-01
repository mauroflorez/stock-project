"""
Financial Expert Agent - Provides fundamental analysis and company insights
"""

from utils.ollama_client import OllamaClient


class FinancialExpertAgent:
    """
    Agent specialized in fundamental analysis and company evaluation
    """
    
    SYSTEM_PROMPT = """You are a Financial Expert specializing in fundamental analysis and company valuation.

Your role:
- Analyze company fundamentals (P/E ratio, market cap, sector performance)
- Evaluate the company's competitive position
- Assess financial health and growth potential
- Consider industry trends and market conditions
- Provide long-term investment perspective

Be thorough, use financial metrics correctly, and consider both quantitative and qualitative factors.
Balance optimism with realistic assessment.
"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.name = "Financial Expert"
    
    def analyze(self, stock_data: str, stock_symbol: str) -> dict:
        """
        Perform fundamental analysis on the company
        
        Args:
            stock_data: Formatted stock data including fundamentals
            stock_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with analysis results
        """
        
        prompt = f"""
Provide a fundamental analysis for {stock_symbol} based on the following data:

{stock_data}

Provide your analysis in the following format:

COMPANY OVERVIEW:
[Brief description of what the company does and its market position]

VALUATION ANALYSIS:
[Evaluate P/E ratio, market cap, and other valuation metrics]
[Is the stock overvalued, undervalued, or fairly valued?]

SECTOR & INDUSTRY POSITION:
[Comment on the sector health and company's competitive position]

FINANCIAL HEALTH:
[Assess the company's financial strength based on available metrics]

GROWTH POTENTIAL:
[Evaluate short-term and long-term growth prospects]

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
        
        return {
            "agent": self.name,
            "analysis": response,
            "raw_data": stock_data
        }


if __name__ == "__main__":
    # Test the agent
    from utils.data_fetcher import DataFetcher
    
    print("Testing Financial Expert Agent...\n")
    
    fetcher = DataFetcher()
    stock_data = fetcher.get_stock_prices("GOOGL", days=60)
    stock_formatted = fetcher.format_price_data_for_agent(stock_data)
    
    agent = FinancialExpertAgent()
    result = agent.analyze(stock_formatted, "GOOGL")
    
    print("\n" + "="*80)
    print(result["analysis"])
    print("="*80)
