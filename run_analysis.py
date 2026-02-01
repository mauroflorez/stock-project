#!/usr/bin/env python3
"""
Main Runner Script
Coordinates the entire analysis pipeline and generates reports
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_analyzer import StockAnalyzer
from report_generator import HTMLReportGenerator
from ollama_utils import check_ollama_status
from config import STOCKS, OUTPUT_DIR, GITHUB_REPO_DIR


def setup_directories():
    """Create necessary directories"""
    directories = [OUTPUT_DIR, GITHUB_REPO_DIR]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory ready: {directory}")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("Checking prerequisites...\n")
    
    # Check Ollama
    print("1. Checking Ollama...")
    status = check_ollama_status()
    
    if not status["running"]:
        print("   ✗ Ollama is not running!")
        print("   → Start Ollama:")
        print("      macOS/Windows: Ollama should start automatically")
        print("      Linux: Run 'ollama serve' in a terminal")
        return False
    
    print("   ✓ Ollama is running")
    
    if not status["model_ready"]:
        print(f"   ✗ Model '{status['configured_model']}' not found!")
        print(f"   → Pull the model: ollama pull {status['configured_model']}")
        return False
    
    print(f"   ✓ Model '{status['configured_model']}' is ready")
    
    # Check Python packages
    print("\n2. Checking Python packages...")
    required_packages = ['yfinance', 'pandas', 'requests', 'jinja2']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} not found!")
            print(f"   → Install: pip install {package}")
            return False
    
    print("\n✓ All prerequisites met!\n")
    return True


def run_analysis():
    """Run the complete analysis pipeline"""
    
    print("="*70)
    print("STOCK INVESTMENT PLANNER - ANALYSIS PIPELINE")
    print("="*70)
    print()
    
    # Setup
    setup_directories()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Please fix the issues above and try again.")
        return False
    
    # Run analysis for each stock
    all_results = []
    today = datetime.now().strftime('%Y%m%d')
    
    for ticker in STOCKS:
        print(f"\n{'='*70}")
        print(f"Analyzing {ticker}")
        print(f"{'='*70}\n")
        
        try:
            # Run analysis
            analyzer = StockAnalyzer(ticker)
            results = analyzer.run_complete_analysis()
            
            if "error" in results:
                print(f"\n✗ Analysis failed for {ticker}")
                continue
            
            all_results.append(results)
            
            # Save JSON report
            json_file = os.path.join(OUTPUT_DIR, f"{ticker}_analysis_{today}.json")
            analyzer.save_to_json(json_file)
            
            # Generate HTML report
            generator = HTMLReportGenerator()
            html_file = os.path.join(GITHUB_REPO_DIR, f"{ticker}_report.html")
            generator.generate_report(results, html_file)
            
            print(f"\n✓ Completed analysis for {ticker}")
            
        except Exception as e:
            print(f"\n✗ Error analyzing {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Generate index page
    if all_results:
        print(f"\n{'='*70}")
        print("Generating index page...")
        print(f"{'='*70}\n")
        
        generator = HTMLReportGenerator()
        index_file = os.path.join(GITHUB_REPO_DIR, "index.html")
        generator.generate_index_page(all_results, index_file)
        
        # Save combined JSON
        combined_json = os.path.join(OUTPUT_DIR, f"all_stocks_{today}.json")
        with open(combined_json, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n{'='*70}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*70}")
        print(f"\nResults saved to:")
        print(f"  - JSON reports: {OUTPUT_DIR}/")
        print(f"  - HTML reports: {GITHUB_REPO_DIR}/")
        print(f"\nNext steps:")
        print(f"  1. Open {GITHUB_REPO_DIR}/index.html in your browser")
        print(f"  2. Push to GitHub Pages (see deploy_to_github.sh)")
        print()
        
        return True
    
    else:
        print("\n✗ No successful analyses completed.")
        return False


if __name__ == "__main__":
    success = run_analysis()
    sys.exit(0 if success else 1)
