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
from agents.momentum_analyst import MomentumAnalystAgent
from agents.sector_analyst import SectorAnalystAgent
from agents.quorum_scorer import QuorumScorer
from utils.data_fetcher import DataFetcher
from utils.ollama_client import OllamaClient
from utils.visualizations import StockVisualizer
from utils.prediction_tracker import PredictionTracker
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
        self.momentum_agent = MomentumAnalystAgent()
        self.sector_agent = SectorAnalystAgent()
        self.synthesizer_agent = InvestmentSynthesizerAgent()
        self.quorum_scorer = QuorumScorer()
        self.prediction_tracker = PredictionTracker()
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
        print("📊 Step 1/8: Fetching stock price data...")
        stock_data = self.data_fetcher.get_stock_prices(symbol)
        stock_formatted = self.data_fetcher.format_price_data_for_agent(stock_data)

        print("📰 Step 2/8: Fetching news data...")
        news_data = self.data_fetcher.get_news(
            symbol,
            STOCK_NAMES.get(symbol, symbol)
        )
        news_formatted = self.data_fetcher.format_news_for_agent(news_data)

        # Step 2: Run agents
        print("\n🤖 Running AI Agents...\n")

        # News Analysis (LLM)
        print("🗞️  Step 3/8: News Analysis...")
        news_result = self.news_agent.analyze(news_formatted, symbol)
        print("✅ News analysis complete\n")

        # Statistical Analysis (LLM + Python indicators)
        print("📈 Step 4/8: Statistical Analysis...")
        stats_result = self.stats_agent.analyze(
            stock_formatted,
            stock_data.get('historical_close', []),
            symbol
        )
        print("✅ Statistical analysis complete\n")

        # Forecasting
        print("🔮 Step 5/8: Time Series Forecasting...")
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

        # Financial Analysis (LLM + Python scoring)
        print("💼 Step 6/8: Financial Analysis...")
        financial_result = self.financial_agent.analyze(stock_formatted, symbol, raw_stock_data=stock_data)
        print("✅ Financial analysis complete\n")

        # Momentum Analysis (Python only - no LLM)
        print("🚀 Step 7/8: Momentum Analysis...")
        momentum_result = self.momentum_agent.analyze(
            stock_data.get('historical_close', []),
            stock_data.get('historical_volume', []),
            symbol
        )
        print(f"   Signal: {momentum_result['momentum_signal']} (score: {momentum_result['momentum_score']})")
        print("✅ Momentum analysis complete\n")

        # Sector Analysis (Python only - no LLM)
        print("🏢 Step 8/8: Sector Analysis...")
        sector_result = self.sector_agent.analyze(
            stock_data.get('historical_close', []),
            stock_data.get('sector', 'Unknown'),
            symbol
        )
        print(f"   Signal: {sector_result['sector_signal']} (score: {sector_result['sector_score']})")
        print("✅ Sector analysis complete\n")

        # === Quorum Scoring ===
        # Determine forecast direction
        forecast_dir = "flat"
        try:
            next_day_ret = forecast_result['summary'].get('next_day_expected_return', '0%')
            ret_val = float(next_day_ret.replace('%', '').replace('+', ''))
            if ret_val > 0.5:
                forecast_dir = "up"
            elif ret_val < -0.5:
                forecast_dir = "down"
        except (ValueError, TypeError):
            pass
        
        # Get deterministic signals
        tech_signal = stats_result.get('statistics', {}).get('technical_signal', 'NEUTRAL')
        tech_score = stats_result.get('statistics', {}).get('technical_score', 0.0)
        fund_signal = financial_result.get('fundamental_signal', {}).get('signal', 'FAIR')
        fund_score = financial_result.get('fundamental_signal', {}).get('score', 0.0)
        
        # Extract news sentiment from LLM output
        from generate_report import HTMLReportGenerator
        report_gen = HTMLReportGenerator()
        news_sentiment, _ = report_gen.extract_news_sentiment(news_result['analysis'])
        
        quorum_result = self.quorum_scorer.compute(
            news_signal=news_sentiment,
            technical_signal=tech_signal,
            technical_score=tech_score,
            fundamental_signal=fund_signal,
            fundamental_score=fund_score,
            momentum_signal=momentum_result['momentum_signal'],
            momentum_score=momentum_result['momentum_score'],
            sector_signal=sector_result['sector_signal'],
            sector_score=sector_result['sector_score'],
            forecast_direction=forecast_dir
        )
        
        print(f"🎯 Quorum Verdict: {quorum_result['recommendation']} "
              f"({quorum_result['strength']}, confidence: {quorum_result['confidence']:.1%})")
        print(f"   {quorum_result['consensus']}\n")

        # Synthesis (includes forecast + quorum context)
        forecast_summary = f"""
FORECAST SUMMARY:
- Next Day Prediction: ${forecast_result['summary']['next_day_prediction']:.2f} ({forecast_result['summary']['next_day_expected_return']})
- 10-Day Prediction: ${forecast_result['summary']['day_10_prediction']:.2f} ({forecast_result['summary']['day_10_expected_return']})
- Confidence: {forecast_result['summary']['confidence']}

QUORUM SCORING RESULT:
- Recommendation: {quorum_result['recommendation']} ({quorum_result['strength']})
- Confidence: {quorum_result['confidence']:.1%}
- Momentum: {momentum_result['momentum_signal']}
- Sector: {sector_result['sector_signal']}
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
                "momentum_analyst": momentum_result,
                "sector_analyst": sector_result,
                "investment_synthesizer": synthesis_result
            },
            "quorum": quorum_result
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
                
                # Record prediction for future evaluation
                quorum = results.get('quorum', {})
                current_price = results.get('stock_data', {}).get('current_price', 0)
                if quorum and current_price:
                    self.prediction_tracker.record_prediction(
                        symbol, quorum, current_price, results.get('agents', {})
                    )
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("✅ Analysis complete!")
        print(f"📊 Analyzed {len(all_results)} stock(s)")
        print(f"{'='*80}\n")
        
        # Print prediction accuracy report
        self.prediction_tracker.print_report()
        
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
