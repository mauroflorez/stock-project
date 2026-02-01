#!/usr/bin/env python3
"""
Test script to verify the Stock Investment Planner setup
"""

import sys
import os

def test_ollama():
    """Test Ollama connection"""
    print("🔍 Testing Ollama connection...")
    try:
        from utils.ollama_client import OllamaClient
        client = OllamaClient()
        
        if not client.is_available():
            print("❌ Ollama is not running")
            print("   Start it with: ollama serve")
            return False
        
        print("✅ Ollama is running")
        
        models = client.list_models()
        if not models:
            print("⚠️  No models found")
            print("   Install one with: ollama pull llama3.1:8b")
            return False
        
        print(f"✅ Available models: {', '.join(models)}")
        
        # Test generation
        print("\n🧪 Testing model generation...")
        response = client.generate("Say 'test successful' in exactly 2 words.", max_tokens=10)
        if response:
            print(f"✅ Model response: {response[:100]}")
        else:
            print("❌ Model did not respond")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_fetching():
    """Test data fetching"""
    print("\n📊 Testing data fetching...")
    try:
        from utils.data_fetcher import DataFetcher
        
        fetcher = DataFetcher()
        
        # Test stock data
        print("   Fetching GOOGL stock data...")
        stock_data = fetcher.get_stock_prices("GOOGL", days=5)
        
        if "error" in stock_data:
            print(f"❌ Error fetching stock data: {stock_data['error']}")
            return False
        
        print(f"✅ Stock data retrieved (Current price: ${stock_data.get('current_price', 0):.2f})")
        
        # Test news
        print("   Fetching news...")
        news = fetcher.get_news("GOOGL", "Google", days=1)
        
        if news and "error" not in news[0]:
            print(f"✅ News retrieved ({len(news)} articles)")
        else:
            print("⚠️  Could not fetch news (this is okay, might be rate limited)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test all required imports"""
    print("\n📦 Testing Python dependencies...")
    
    required_packages = {
        'requests': 'requests',
        'yfinance': 'yfinance',
        'feedparser': 'feedparser',
        'numpy': 'numpy'
    }
    
    all_good = True
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} not installed")
            all_good = False
    
    if not all_good:
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def test_agents():
    """Test agent initialization"""
    print("\n🤖 Testing AI agents...")
    try:
        from agents.news_analyst import NewsAnalystAgent
        from agents.statistical_expert import StatisticalExpertAgent
        from agents.financial_expert import FinancialExpertAgent
        from agents.investment_synthesizer import InvestmentSynthesizerAgent
        
        agents = [
            ("News Analyst", NewsAnalystAgent()),
            ("Statistical Expert", StatisticalExpertAgent()),
            ("Financial Expert", FinancialExpertAgent()),
            ("Investment Synthesizer", InvestmentSynthesizerAgent())
        ]
        
        for name, agent in agents:
            print(f"✅ {name} initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Stock Investment Planner - System Test")
    print("="*60)
    
    tests = [
        ("Python Dependencies", test_imports),
        ("Ollama Connection", test_ollama),
        ("Data Fetching", test_data_fetching),
        ("AI Agents", test_agents)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the analysis!")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Run: python generate_report.py")
        print("  3. Open: docs/index.html")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
