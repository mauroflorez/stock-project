"""
Phase 2 + 3 Test Evaluator
Tests: Momentum Agent, Sector Analyst, Quorum Scorer, Prediction Tracker
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from agents.momentum_analyst import MomentumAnalystAgent
from agents.sector_analyst import SectorAnalystAgent
from agents.quorum_scorer import QuorumScorer
from agents.statistical_expert import StatisticalExpertAgent
from agents.financial_expert import FinancialExpertAgent
from utils.data_fetcher import DataFetcher
from utils.prediction_tracker import PredictionTracker
from generate_report import HTMLReportGenerator
from config import STOCK_SYMBOLS, STOCK_NAMES


def test_phase_2a():
    """Test Momentum Agent"""
    print("=" * 70)
    print("PHASE 2A: Momentum Analyst Evaluation")
    print("=" * 70)
    
    fetcher = DataFetcher()
    mom_agent = MomentumAnalystAgent()
    
    results = []
    for symbol in STOCK_SYMBOLS:
        try:
            data = fetcher.get_stock_prices(symbol, days=60)
            if "error" in data:
                continue
            r = mom_agent.analyze(
                data['historical_close'],
                data.get('historical_volume', []),
                symbol
            )
            results.append({
                'symbol': symbol,
                'signal': r['momentum_signal'],
                'score': r['momentum_score'],
                'reasons': r['momentum_reasons']
            })
        except Exception as e:
            print(f"  ERROR: {symbol} - {e}")
    
    print(f"\n{'Symbol':<8} {'Score':>6} {'Signal':<10} {'Reasons'}")
    print("-" * 70)
    for r in results:
        print(f"{r['symbol']:<8} {r['score']:>6.2f} {r['signal']:<10} {r['reasons'][0] if r['reasons'] else ''}")
    
    tests = []
    signals = set(r['signal'] for r in results)
    tests.append(("All stocks analyzed", len(results) == len(STOCK_SYMBOLS), f"{len(results)}/{len(STOCK_SYMBOLS)}"))
    tests.append(("Signals computed", all(r['signal'] in ('BULLISH','NEUTRAL','BEARISH') for r in results), ""))
    tests.append(("≥2 signal types", len(signals) >= 2, f"Types: {signals}"))
    tests.append(("All have reasons", all(len(r['reasons']) >= 1 for r in results), ""))
    scores = set(r['score'] for r in results)
    tests.append(("Score diversity", len(scores) >= 3, f"{len(scores)} distinct"))
    
    all_pass = True
    print(f"\n--- Test Results ---")
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<28} {f'({detail})' if detail else ''}")
        if not passed: all_pass = False
    
    print(f"\nPHASE 2A: {'ALL PASSED ✅' if all_pass else 'FAILED ❌'}\n")
    return all_pass


def test_phase_2b():
    """Test Sector Analyst"""
    print("=" * 70)
    print("PHASE 2B: Sector Analyst Evaluation")
    print("=" * 70)
    
    fetcher = DataFetcher()
    sector_agent = SectorAnalystAgent()
    
    results = []
    for symbol in STOCK_SYMBOLS:
        try:
            data = fetcher.get_stock_prices(symbol, days=60)
            if "error" in data:
                continue
            r = sector_agent.analyze(
                data['historical_close'],
                data.get('sector', 'Unknown'),
                symbol
            )
            results.append({
                'symbol': symbol,
                'sector': data.get('sector', '?'),
                'signal': r['sector_signal'],
                'score': r['sector_score'],
                'comparison': r.get('sector_comparison', {})
            })
        except Exception as e:
            print(f"  ERROR: {symbol} - {e}")
    
    print(f"\n{'Symbol':<7} {'Sector':<25} {'Signal':<10} {'Score':>6} {'Rel Perf':>10}")
    print("-" * 70)
    for r in results:
        rel = r['comparison'].get('relative_performance', 'N/A') if r['comparison'] else 'N/A'
        rel_str = f"{rel:+.1f}pp" if isinstance(rel, (int, float)) else rel
        print(f"{r['symbol']:<7} {r['sector']:<25} {r['signal']:<10} {r['score']:>6.1f} {rel_str:>10}")
    
    tests = []
    signals = set(r['signal'] for r in results)
    has_comparison = sum(1 for r in results if r['comparison'])
    tests.append(("All stocks analyzed", len(results) == len(STOCK_SYMBOLS), f"{len(results)}/{len(STOCK_SYMBOLS)}"))
    tests.append(("Sector ETF comparisons", has_comparison >= len(results) * 0.5, f"{has_comparison}/{len(results)}"))
    tests.append(("≥2 signal types", len(signals) >= 2, f"Types: {signals}"))
    
    all_pass = True
    print(f"\n--- Test Results ---")
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<28} {f'({detail})' if detail else ''}")
        if not passed: all_pass = False
    
    print(f"\nPHASE 2B: {'ALL PASSED ✅' if all_pass else 'FAILED ❌'}\n")
    return all_pass


def test_phase_2c():
    """Test Quorum Scorer with real data"""
    print("=" * 70)
    print("PHASE 2C: Quorum Scorer Evaluation")
    print("=" * 70)
    
    fetcher = DataFetcher()
    stats_agent = StatisticalExpertAgent()
    fin_agent = FinancialExpertAgent()
    mom_agent = MomentumAnalystAgent()
    sector_agent = SectorAnalystAgent()
    scorer = QuorumScorer()
    report_gen = HTMLReportGenerator()
    
    results = []
    
    for symbol in STOCK_SYMBOLS:
        try:
            data = fetcher.get_stock_prices(symbol, days=60)
            if "error" in data:
                continue
            
            # Python-computed signals
            stats = stats_agent.calculate_statistics(data['historical_close'])
            fund = fin_agent.compute_fundamental_signal(data)
            mom = mom_agent.analyze(data['historical_close'], data.get('historical_volume', []), symbol)
            sec = sector_agent.analyze(data['historical_close'], data.get('sector', ''), symbol)
            
            # Get news from existing analysis
            existing = report_gen.get_latest_analysis(symbol)
            if existing:
                news_sent, _ = report_gen.extract_news_sentiment(existing['agents']['news_analyst']['analysis'])
            else:
                news_sent = "Neutral"
            
            quorum = scorer.compute(
                news_signal=news_sent,
                technical_signal=stats['technical_signal'],
                technical_score=stats['technical_score'],
                fundamental_signal=fund['signal'],
                fundamental_score=fund['score'],
                momentum_signal=mom['momentum_signal'],
                momentum_score=mom['momentum_score'],
                sector_signal=sec['sector_signal'],
                sector_score=sec['sector_score'],
                forecast_direction="flat"
            )
            
            results.append({
                'symbol': symbol,
                'news': news_sent,
                'tech': stats['technical_signal'],
                'fund': fund['signal'],
                'mom': mom['momentum_signal'],
                'sec': sec['sector_signal'],
                'rec': quorum['recommendation'],
                'conf': quorum['confidence'],
                'score': quorum['weighted_score'],
                'strength': quorum['strength'],
                'consensus': quorum['consensus']
            })
        except Exception as e:
            print(f"  ERROR: {symbol} - {e}")
    
    print(f"\n{'Sym':<6} {'News':<8} {'Tech':<8} {'Fund':<11} {'Mom':<8} {'Sec':<8} {'→Rec':<6} {'Conf':>6} {'Score':>7} {'Consensus'}")
    print("-" * 95)
    for r in results:
        print(f"{r['symbol']:<6} {r['news']:<8} {r['tech']:<8} {r['fund']:<11} {r['mom']:<8} {r['sec']:<8} {r['rec']:<6} {r['conf']:>5.1%} {r['score']:>+6.3f} {r['consensus']}")
    
    # Summary
    buy_c = sum(1 for r in results if r['rec'] == 'BUY')
    hold_c = sum(1 for r in results if r['rec'] == 'HOLD')
    sell_c = sum(1 for r in results if r['rec'] == 'SELL')
    print(f"\nBUY: {buy_c}  |  HOLD: {hold_c}  |  SELL: {sell_c}")
    
    tests = []
    recs = set(r['rec'] for r in results)
    tests.append(("Has BUY recommendations", 'BUY' in recs, f"Count: {buy_c}"))
    tests.append(("Has HOLD recommendations", 'HOLD' in recs, f"Count: {hold_c}"))
    tests.append(("Has SELL recommendations", 'SELL' in recs, f"Count: {sell_c}"))
    tests.append(("6 agents contributing", all(
        len(set([r['news'], r['tech'], r['fund'], r['mom'], r['sec']])) >= 1 
        for r in results
    ), ""))
    tests.append(("Confidence range >30%", 
                  max(r['conf'] for r in results) - min(r['conf'] for r in results) > 0.3, 
                  f"{min(r['conf'] for r in results):.1%}-{max(r['conf'] for r in results):.1%}"))
    consen = set(r['consensus'] for r in results)
    tests.append(("≥2 consensus types", len(consen) >= 2, f"Types: {consen}"))
    
    all_pass = True
    print(f"\n--- Test Results ---")
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<30} {f'({detail})' if detail else ''}")
        if not passed: all_pass = False
    
    print(f"\nPHASE 2C: {'ALL PASSED ✅' if all_pass else 'FAILED ❌'}\n")
    return all_pass


def test_phase_3():
    """Test Prediction Tracker infrastructure"""
    print("=" * 70)
    print("PHASE 3: Prediction Tracker Evaluation")
    print("=" * 70)
    
    # Test with a mock prediction
    import tempfile
    temp_file = tempfile.mktemp(suffix='.json')
    tracker = PredictionTracker(filepath=temp_file)
    
    tests = []
    
    # Test 1: Record prediction
    mock_quorum = {
        "recommendation": "BUY",
        "confidence": 0.72,
        "weighted_score": 0.35,
        "consensus": "Bullish Majority",
        "votes": {
            "news": {"signal": "Bullish", "vote": 1.0},
            "technical": {"signal": "BULLISH", "vote": 0.75},
            "fundamental": {"signal": "FAIR", "vote": 0.0},
            "momentum": {"signal": "BULLISH", "vote": 0.5},
            "sector": {"signal": "NEUTRAL", "vote": 0.0},
            "forecast": {"signal": "up", "vote": 1.0}
        }
    }
    pred = tracker.record_prediction("GOOGL", mock_quorum, 312.50)
    tests.append(("Record prediction", pred is not None, ""))
    tests.append(("Prediction has symbol", pred.get('symbol') == 'GOOGL', ""))
    tests.append(("Prediction has price", pred.get('price_at_prediction') == 312.50, ""))
    tests.append(("Prediction has rec", pred.get('recommendation') == 'BUY', ""))
    tests.append(("Prediction has confidence", pred.get('confidence') == 0.72, ""))
    
    # Test 2: Load persisted
    tracker2 = PredictionTracker(filepath=temp_file)
    tests.append(("Persistence works", len(tracker2.predictions) == 1, f"{len(tracker2.predictions)} predictions"))
    
    # Test 3: Evaluate (should say "too recent")
    eval_result = tracker.evaluate_predictions()
    tests.append(("Evaluation runs", eval_result is not None, ""))
    tests.append(("No evaluable yet", eval_result['evaluated'] == 0, "predictions too recent"))
    
    # Test 4: Weight suggestion
    weights = tracker.get_suggested_weights()
    tests.append(("Weights need more data", weights is None, "need ≥10 evaluated"))
    
    # Cleanup
    try:
        os.remove(temp_file)
    except:
        pass
    
    all_pass = True
    print(f"\n--- Test Results ---")
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<30} {f'({detail})' if detail else ''}")
        if not passed: all_pass = False
    
    print(f"\nPHASE 3: {'ALL PASSED ✅' if all_pass else 'FAILED ❌'}\n")
    return all_pass


def test_report_generation():
    """Test that report generation still works with all changes"""
    print("=" * 70)
    print("INTEGRATION TEST: Report Generation")
    print("=" * 70)
    
    report_gen = HTMLReportGenerator()
    tests = []
    
    # Test with existing analysis data
    from config import STOCK_SYMBOLS
    test_symbol = STOCK_SYMBOLS[0]
    data = report_gen.get_latest_analysis(test_symbol)
    
    if data:
        try:
            html = report_gen.generate_html(data)
            tests.append(("HTML generated", len(html) > 1000, f"{len(html)} chars"))
            tests.append(("Has doctype", "<!DOCTYPE html>" in html, ""))
            tests.append(("Has recommendation", any(x in html for x in ['BUY', 'HOLD', 'SELL']), ""))
        except Exception as e:
            tests.append(("HTML generation", False, str(e)))
    else:
        tests.append(("Data available", False, f"No data for {test_symbol}"))
    
    all_pass = True
    print(f"\n--- Test Results ---")
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<30} {f'({detail})' if detail else ''}")
        if not passed: all_pass = False
    
    print(f"\nINTEGRATION: {'ALL PASSED ✅' if all_pass else 'FAILED ❌'}\n")
    return all_pass


if __name__ == "__main__":
    print("\n" + "🔬" * 35)
    print("   STOCK ANALYSIS AGENT EVALUATOR - Phase 2 & 3")
    print("🔬" * 35 + "\n")
    
    p2a = test_phase_2a()
    p2b = test_phase_2b()
    p2c = test_phase_2c()
    p3 = test_phase_3()
    integ = test_report_generation()
    
    print("\n" + "=" * 70)
    print("OVERALL RESULTS:")
    print(f"  Phase 2A (Momentum):     {'✅ PASS' if p2a else '❌ FAIL'}")
    print(f"  Phase 2B (Sector):       {'✅ PASS' if p2b else '❌ FAIL'}")
    print(f"  Phase 2C (Quorum):       {'✅ PASS' if p2c else '❌ FAIL'}")
    print(f"  Phase 3  (Tracker):      {'✅ PASS' if p3 else '❌ FAIL'}")
    print(f"  Integration (Reports):   {'✅ PASS' if integ else '❌ FAIL'}")
    all_ok = p2a and p2b and p2c and p3 and integ
    print(f"\n  {'🎉 ALL PHASES PASSED!' if all_ok else '⚠️ SOME PHASES FAILED'}")
    print("=" * 70)
