"""
Main Stock Analysis Orchestrator
Coordinates all agents and generates the final report
"""

import sys
import os

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.news_analyst import NewsAnalystAgent
from agents.statistical_expert import StatisticalExpertAgent
from agents.financial_expert import FinancialExpertAgent
from agents.investment_synthesizer import InvestmentSynthesizerAgent
from agents.forecaster import ForecasterAgent
from utils.data_fetcher import DataFetcher
from utils.ollama_client import OllamaClient
from utils.visualizations import StockVisualizer
from config import STOCK_SYMBOLS, STOCK_NAMES, OUTPUT_DIR

import json


class StockAnalysisOrchestrator:
    """
    Orchestrates the multi-agent stock analysis workflow
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.news_agent = NewsAnalystAgent()
        self.stats_agent = StatisticalExpertAgent()
        self.financial_agent = FinancialExpertAgent()
        self.forecaster_agent = ForecasterAgent()
        self.synthesizer_agent = InvestmentSynthesizerAgent()
        self.visualizer = StockVisualizer()
        
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        client = OllamaClient()
        return client.is_available()
    
    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Run complete analysis for a single stock
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary containing all analyses
        """
        print(f"\n{'='*80}")
        print(f"🔍 Starting analysis for {symbol} - {STOCK_NAMES.get(symbol, symbol)}")
        print(f"{'='*80}\n")
        
        # Step 1: Fetch data
        print("📊 Step 1/6: Fetching stock price data...")
        stock_data = self.data_fetcher.get_stock_prices(symbol)
        stock_formatted = self.data_fetcher.format_price_data_for_agent(stock_data)

        print("📰 Step 2/6: Fetching news data...")
        news_data = self.data_fetcher.get_news(
            symbol,
            STOCK_NAMES.get(symbol, symbol)
        )
        news_formatted = self.data_fetcher.format_news_for_agent(news_data)

        # Step 2: Run agents
        print("\n🤖 Running AI Agents...\n")

        # News Analysis
        print("🗞️  Step 3/6: News Analysis...")
        news_result = self.news_agent.analyze(news_formatted, symbol)
        print("✅ News analysis complete\n")

        # Statistical Analysis
        print("📈 Step 4/6: Statistical Analysis...")
        stats_result = self.stats_agent.analyze(
            stock_formatted,
            stock_data.get('historical_close', []),
            symbol
        )
        print("✅ Statistical analysis complete\n")

        # Forecasting
        print("🔮 Step 5/6: Time Series Forecasting...")
        forecast_result = self.forecaster_agent.analyze(
            prices=stock_data.get('historical_close', []),
            dates=stock_data.get('historical_dates', []),
            symbol=symbol,
            forecast_days=10
        )

        # Generate forecast charts
        forecast_charts = self.visualizer.create_multi_timeframe_chart(symbol, forecast_result)
        forecast_result['charts'] = forecast_charts
        print("✅ Forecasting complete\n")

        # Financial Analysis
        print("💼 Step 6/6: Financial Analysis...")
        financial_result = self.financial_agent.analyze(stock_formatted, symbol)
        print("✅ Financial analysis complete\n")

        # Synthesis (includes forecast summary in context)
        forecast_summary = f"""
FORECAST SUMMARY:
- Next Day Prediction: ${forecast_result['summary']['next_day_prediction']:.2f} ({forecast_result['summary']['next_day_expected_return']})
- 10-Day Prediction: ${forecast_result['summary']['day_10_prediction']:.2f} ({forecast_result['summary']['day_10_expected_return']})
- Confidence: {forecast_result['summary']['confidence']}
"""
        synthesis_result = self.synthesizer_agent.synthesize(
            news_result['analysis'],
            stats_result['analysis'] + forecast_summary,
            financial_result['analysis'],
            symbol
        )
        print("✅ Investment synthesis complete\n")
        
        # Compile results
        results = {
            "symbol": symbol,
            "company_name": STOCK_NAMES.get(symbol, symbol),
            "analysis_date": datetime.now().isoformat(),
            "stock_data": stock_data,
            "news_data": news_data,
            "agents": {
                "news_analyst": news_result,
                "statistical_expert": stats_result,
                "forecaster": forecast_result,
                "financial_expert": financial_result,
                "investment_synthesizer": synthesis_result
            }
        }
        
        return results
    
    def save_results(self, results: Dict[str, Any], format: str = "json"):
        """Save analysis results to file"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        symbol = results['symbol']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"{OUTPUT_DIR}/{symbol}_analysis_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Results saved to: {filename}")
            return filename
        
        return None
    
    def run_all_stocks(self):
        """Run analysis for all configured stocks"""
        if not self.check_ollama():
            print("❌ Error: Ollama is not running!")
            print("Please start Ollama with: ollama serve")
            print("And make sure you have a model installed: ollama pull llama3.1:8b")
            return None
        
        print("\n🚀 Stock Investment Planner - Multi-Agent Analysis")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = []
        
        for symbol in STOCK_SYMBOLS:
            try:
                results = self.analyze_stock(symbol)
                all_results.append(results)
                
                # Save individual stock results
                self.save_results(results)
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("✅ Analysis complete!")
        print(f"📊 Analyzed {len(all_results)} stock(s)")
        print(f"{'='*80}\n")
        
        return all_results


def main():
    """Main entry point"""
    orchestrator = StockAnalysisOrchestrator()
    results = orchestrator.run_all_stocks()
    
    if results:
        print("\n💡 Next steps:")
        print("1. Review the JSON files in the 'output' directory")
        print("2. Run 'python generate_report.py' to create an HTML report")
        print("3. Push the HTML report to GitHub Pages")


if __name__ == "__main__":
    main()
