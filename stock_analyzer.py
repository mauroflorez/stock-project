"""
Main Stock Analyzer
Orchestrates all agents and generates complete analysis
"""

import json
from datetime import datetime
from typing import Dict
from data_fetcher import StockDataFetcher, NewsDataFetcher
from predictions import TimeSeriesPredictor
from agents import (
    NewsAnalystAgent, 
    StatisticalAnalystAgent, 
    FinancialExpertAgent, 
    SynthesisAgent
)
from ollama_utils import check_ollama_status
from config import STOCKS
import traceback


class StockAnalyzer:
    """Main analyzer that coordinates all components"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.analysis_results = {}
        self.timestamp = datetime.now()
        
        # Initialize agents
        self.news_agent = NewsAnalystAgent()
        self.stats_agent = StatisticalAnalystAgent()
        self.financial_agent = FinancialExpertAgent()
        self.synthesis_agent = SynthesisAgent()
        
    def run_complete_analysis(self) -> dict:
        """
        Run the complete 4-agent analysis pipeline
        """
        print(f"\n{'='*60}")
        print(f"Starting analysis for {self.ticker}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Fetch all data
            print("Step 1: Fetching data...")
            data = self._fetch_all_data()
            
            # Step 2: Run statistical predictions
            print("\nStep 2: Running time series predictions...")
            predictions = self._run_predictions(data['historical_data'])
            
            # Step 3: Run Agent 1 - News Analysis
            print("\nStep 3: Agent 1 - News Analyst analyzing...")
            news_analysis = self.news_agent.analyze(
                self.ticker,
                data['company_info'].get('name', self.ticker),
                data['news']
            )
            
            # Step 4: Run Agent 2 - Statistical Analysis
            print("\nStep 4: Agent 2 - Statistical Analyst analyzing...")
            stats_analysis = self.stats_agent.analyze(
                self.ticker,
                data['historical_data'],
                predictions
            )
            
            # Step 5: Run Agent 3 - Financial Expert
            print("\nStep 5: Agent 3 - Financial Expert analyzing...")
            financial_analysis = self.financial_agent.analyze(
                self.ticker,
                data['company_info'],
                data['historical_data']
            )
            
            # Step 6: Run Agent 4 - Synthesis
            print("\nStep 6: Agent 4 - Synthesis Agent generating recommendation...")
            current_price = data['historical_data']['Close'].iloc[-1]
            synthesis = self.synthesis_agent.synthesize(
                self.ticker,
                data['company_info'].get('name', self.ticker),
                news_analysis,
                stats_analysis,
                financial_analysis,
                current_price
            )
            
            # Compile results
            self.analysis_results = {
                "ticker": self.ticker,
                "company_name": data['company_info'].get('name', self.ticker),
                "timestamp": self.timestamp.isoformat(),
                "current_price": float(current_price),
                "data": {
                    "company_info": data['company_info'],
                    "latest_news": data['news'][:5],  # Top 5 for summary
                    "predictions": predictions
                },
                "agent_analyses": {
                    "news_analysis": news_analysis,
                    "statistical_analysis": stats_analysis,
                    "fundamental_analysis": financial_analysis,
                    "final_recommendation": synthesis
                }
            }
            
            print(f"\n{'='*60}")
            print("✓ Analysis complete!")
            print(f"{'='*60}\n")
            
            return self.analysis_results
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}\n{traceback.format_exc()}"
            print(f"\n✗ {error_msg}")
            return {"error": error_msg, "ticker": self.ticker}
    
    def _fetch_all_data(self) -> Dict:
        """Fetch all required data for analysis"""
        
        # Fetch stock data
        stock_fetcher = StockDataFetcher(self.ticker)
        historical_data = stock_fetcher.get_historical_data()
        company_info = stock_fetcher.get_company_info()
        
        print(f"  ✓ Fetched {len(historical_data)} days of price data")
        print(f"  ✓ Company: {company_info.get('name', self.ticker)}")
        
        # Fetch news
        news_fetcher = NewsDataFetcher(
            self.ticker, 
            company_info.get('name', self.ticker)
        )
        news = news_fetcher.get_all_news()
        
        print(f"  ✓ Fetched {len(news)} news articles")
        
        return {
            "historical_data": historical_data,
            "company_info": company_info,
            "news": news
        }
    
    def _run_predictions(self, historical_data) -> Dict:
        """Run time series predictions"""
        
        predictor = TimeSeriesPredictor(self.ticker)
        predictions = predictor.get_best_prediction(historical_data)
        volatility = predictor.calculate_volatility(historical_data)
        
        predictions['volatility'] = volatility
        
        print(f"  ✓ Prediction method: {predictions.get('method', 'N/A')}")
        print(f"  ✓ Forecast: {predictions.get('forecast_summary', 'N/A')}")
        
        return predictions
    
    def save_to_json(self, filepath: str):
        """Save analysis results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"✓ Saved analysis to {filepath}")


def analyze_all_stocks():
    """Analyze all configured stocks"""
    
    # Check Ollama first
    print("Checking Ollama status...")
    status = check_ollama_status()
    
    if not status["running"]:
        print("\n✗ ERROR: Ollama is not running!")
        print("  Start Ollama with: ollama serve")
        print("  Or on Mac/Windows: Ollama should start automatically")
        return
    
    if not status["model_ready"]:
        print(f"\n✗ ERROR: Model '{status['configured_model']}' not found!")
        print(f"  Pull it with: ollama pull {status['configured_model']}")
        return
    
    print(f"✓ Ollama is ready with model: {status['configured_model']}\n")
    
    # Analyze each stock
    all_results = []
    
    for ticker in STOCKS:
        try:
            analyzer = StockAnalyzer(ticker)
            results = analyzer.run_complete_analysis()
            all_results.append(results)
            
            # Save individual report
            output_file = f"reports/{ticker}_analysis_{datetime.now().strftime('%Y%m%d')}.json"
            analyzer.save_to_json(output_file)
            
        except Exception as e:
            print(f"\n✗ Failed to analyze {ticker}: {str(e)}")
            traceback.print_exc()
    
    return all_results


if __name__ == "__main__":
    import os
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Run analysis
    results = analyze_all_stocks()
    
    if results:
        print(f"\n{'='*60}")
        print(f"Completed analysis for {len(results)} stock(s)")
        print(f"{'='*60}\n")
