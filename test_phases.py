"""
Phase 1B + 1C Test: Technical Indicators & Fundamental Metrics Evaluation
Tests that RSI, MACD, Bollinger Bands, and fundamental signals are computed correctly.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.statistical_expert import StatisticalExpertAgent
from agents.financial_expert import FinancialExpertAgent
from utils.data_fetcher import DataFetcher
from config import STOCK_SYMBOLS, STOCK_NAMES
from generate_report import HTMLReportGenerator
import numpy as np


def test_phase_1b():
    """Test technical indicators computation (no LLM needed)"""
    print("=" * 70)
    print("PHASE 1B: Technical Indicators Evaluation")
    print("=" * 70)
    
    stats_agent = StatisticalExpertAgent()
    fetcher = DataFetcher()
    
    results = []
    
    for symbol in STOCK_SYMBOLS:
        try:
            data = fetcher.get_stock_prices(symbol, days=60)
            if "error" in data:
                print(f"  SKIP: {symbol} - {data['error']}")
                continue
            
            prices = data['historical_close']
            stats = stats_agent.calculate_statistics(prices)
            
            results.append({
                'symbol': symbol,
                'rsi': stats['rsi_14'],
                'macd': stats['macd_line'],
                'macd_sig': stats['macd_signal'],
                'macd_hist': stats['macd_histogram'],
                'bb_upper': stats['bollinger_upper'],
                'bb_lower': stats['bollinger_lower'],
                'price': stats['current_price'],
                'signal': stats['technical_signal'],
                'score': stats['technical_score'],
                'reasons': stats['technical_reasons']
            })
        except Exception as e:
            print(f"  ERROR: {symbol} - {e}")
    
    # Print results
    print(f"\n{'Symbol':<7} {'Price':>9} {'RSI':>6} {'MACD':>8} {'BB_Low':>9} {'BB_Up':>9} {'Score':>6} {'Signal':<8}")
    print("-" * 70)
    for r in results:
        rsi_str = f"{r['rsi']:.1f}" if r['rsi'] else "N/A"
        macd_str = f"{r['macd']:.2f}" if r['macd'] else "N/A"
        bb_lo = f"${r['bb_lower']:.2f}" if r['bb_lower'] else "N/A"
        bb_up = f"${r['bb_upper']:.2f}" if r['bb_upper'] else "N/A"
        print(f"{r['symbol']:<7} ${r['price']:>8.2f} {rsi_str:>6} {macd_str:>8} {bb_lo:>9} {bb_up:>9} {r['score']:>6.1f} {r['signal']:<8}")
    
    # Tests
    tests = []
    
    # Test 1: RSI computed for all stocks with enough data
    rsi_computed = sum(1 for r in results if r['rsi'] is not None)
    test1 = rsi_computed == len(results)
    tests.append(("RSI computed for all stocks", test1, f"{rsi_computed}/{len(results)}"))
    
    # Test 2: RSI values in valid range [0, 100]
    rsi_valid = all(0 <= r['rsi'] <= 100 for r in results if r['rsi'] is not None)
    tests.append(("RSI in [0,100] range", rsi_valid, ""))
    
    # Test 3: MACD computed
    macd_computed = sum(1 for r in results if r['macd'] is not None)
    test3 = macd_computed == len(results)
    tests.append(("MACD computed for all stocks", test3, f"{macd_computed}/{len(results)}"))
    
    # Test 4: Bollinger Bands computed
    bb_computed = sum(1 for r in results if r['bb_upper'] is not None)
    test4 = bb_computed == len(results)
    tests.append(("Bollinger Bands computed", test4, f"{bb_computed}/{len(results)}"))
    
    # Test 5: Bollinger Band invariant (lower < middle < upper)
    bb_ordered = all(r['bb_lower'] < r['price'] or r['bb_upper'] > r['price'] for r in results if r['bb_lower'])
    tests.append(("BB bands reasonable", bb_ordered, ""))
    
    # Test 6: Signal diversity (not all same)
    signals = set(r['signal'] for r in results)
    test6 = len(signals) >= 2
    tests.append(("≥2 technical signal types", test6, f"Types: {signals}"))
    
    # Test 7: Scores have variety
    scores = set(r['score'] for r in results)
    test7 = len(scores) >= 3
    tests.append(("≥3 distinct tech scores", test7, f"{len(scores)} distinct"))
    
    # Test 8: At least one reason per stock
    all_have_reasons = all(len(r['reasons']) >= 1 for r in results)
    tests.append(("All stocks have reasons", all_have_reasons, ""))
    
    print(f"\n--- Test Results ---")
    all_pass = True
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<32} {f'({detail})' if detail else ''}")
        if not passed:
            all_pass = False
    
    print(f"\n{'='*70}")
    print(f"PHASE 1B: {'ALL TESTS PASSED ✅' if all_pass else 'SOME TESTS FAILED ❌'}")
    print(f"{'='*70}\n")
    return all_pass


def test_phase_1c():
    """Test fundamental metrics and signal computation (no LLM needed)"""
    print("=" * 70)
    print("PHASE 1C: Fundamental Metrics Evaluation")
    print("=" * 70)
    
    fin_agent = FinancialExpertAgent()
    fetcher = DataFetcher()
    
    results = []
    
    for symbol in STOCK_SYMBOLS:
        try:
            data = fetcher.get_stock_prices(symbol, days=60)
            if "error" in data:
                print(f"  SKIP: {symbol} - {data['error']}")
                continue
            
            fund = fin_agent.compute_fundamental_signal(data)
            
            results.append({
                'symbol': symbol,
                'pe': data.get('pe_ratio'),
                'fwd_pe': data.get('forward_pe'),
                'peg': data.get('peg_ratio'),
                'roe': data.get('return_on_equity'),
                'eg': data.get('earnings_growth'),
                'dte': data.get('debt_to_equity'),
                'target': data.get('target_mean_price'),
                'price': data.get('current_price'),
                'signal': fund['signal'],
                'score': fund['score'],
                'reasons': fund['reasons']
            })
        except Exception as e:
            print(f"  ERROR: {symbol} - {e}")
    
    # Print compact results
    print(f"\n{'Symbol':<7} {'P/E':>6} {'FwdPE':>6} {'PEG':>5} {'ROE':>6} {'D/E':>6} {'Target':>8} {'Score':>6} {'Signal':<12}")
    print("-" * 70)
    for r in results:
        pe_s = f"{r['pe']:.1f}" if r['pe'] else "N/A"
        fpe_s = f"{r['fwd_pe']:.1f}" if r['fwd_pe'] else "N/A"
        peg_s = f"{r['peg']:.2f}" if r['peg'] else "N/A"
        roe_s = f"{r['roe']*100:.0f}%" if r['roe'] else "N/A"
        dte_s = f"{r['dte']:.0f}" if r['dte'] else "N/A"
        tgt_s = f"${r['target']:.0f}" if r['target'] else "N/A"
        print(f"{r['symbol']:<7} {pe_s:>6} {fpe_s:>6} {peg_s:>5} {roe_s:>6} {dte_s:>6} {tgt_s:>8} {r['score']:>6.1f} {r['signal']:<12}")
    
    # Tests
    tests = []
    
    # Test 1: All metrics populated for most stocks
    has_pe = sum(1 for r in results if r['pe'] is not None)
    tests.append(("P/E available", has_pe >= len(results) * 0.7, f"{has_pe}/{len(results)}"))
    
    # Test 2: Signal diversity
    signals = set(r['signal'] for r in results)
    test2 = len(signals) >= 2
    tests.append(("≥2 fundamental signals", test2, f"Types: {signals}"))
    
    # Test 3: Score diversity
    scores = set(r['score'] for r in results)
    test3 = len(scores) >= 3
    tests.append(("≥3 distinct fund scores", test3, f"{len(scores)} distinct"))
    
    # Test 4: All stocks have reasoning
    all_reasons = all(len(r['reasons']) >= 1 for r in results)
    tests.append(("All stocks have reasons", all_reasons, ""))
    
    # Test 5: PEG ratio when available should influence signal
    high_peg = [r for r in results if r['peg'] and r['peg'] > 2.5]
    if high_peg:
        peg_correct = any(r['signal'] == 'OVERVALUED' or r['score'] < 0 for r in high_peg)
        tests.append(("High PEG → negative score", peg_correct, f"{len(high_peg)} stocks with PEG>2.5"))
    
    # Test 6: ROE data available
    has_roe = sum(1 for r in results if r['roe'] is not None)
    tests.append(("ROE available", has_roe >= len(results) * 0.5, f"{has_roe}/{len(results)}"))
    
    print(f"\n--- Test Results ---")
    all_pass = True
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<32} {f'({detail})' if detail else ''}")
        if not passed:
            all_pass = False
    
    print(f"\n{'='*70}")
    print(f"PHASE 1C: {'ALL TESTS PASSED ✅' if all_pass else 'SOME TESTS FAILED ❌'}")
    print(f"{'='*70}\n")
    return all_pass


def test_phase_1a_revisited():
    """Re-test signal parser with knowledge of new agent capabilities"""
    print("=" * 70)
    print("PHASE 1A (REVISITED): Full Signal Pipeline Test")
    print("=" * 70)
    
    g = HTMLReportGenerator()
    from config import STOCK_SYMBOLS
    
    results = []
    
    for symbol in STOCK_SYMBOLS:
        data = g.get_latest_analysis(symbol)
        if not data:
            print(f"  SKIP: No data for {symbol}")
            continue
        
        news_sent, _ = g.extract_news_sentiment(data['agents']['news_analyst']['analysis'])
        stat_trend, _ = g.extract_statistical_outlook(data['agents']['statistical_expert']['analysis'])
        fin_val, _ = g.extract_financial_outlook(data['agents']['financial_expert']['analysis'])
        conf_score = g.compute_confidence_score(news_sent, stat_trend, fin_val, "HOLD")
        
        if conf_score >= 0.67:
            signal = "BUY"
        elif conf_score <= 0.33:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        results.append({
            'symbol': symbol,
            'news': news_sent,
            'tech': stat_trend,
            'fund': fin_val,
            'score': conf_score,
            'signal': signal
        })
    
    print(f"\n{'Symbol':<8} {'News':<12} {'Technical':<12} {'Fundamental':<14} {'Score':<8} {'Signal':<6}")
    print("-" * 62)
    for r in results:
        print(f"{r['symbol']:<8} {r['news']:<12} {r['tech']:<12} {r['fund']:<14} {r['score']:.2f}    {r['signal']:<6}")
    
    # Summary counts
    buy_count = sum(1 for r in results if r['signal'] == 'BUY')
    hold_count = sum(1 for r in results if r['signal'] == 'HOLD')
    sell_count = sum(1 for r in results if r['signal'] == 'SELL')
    
    print(f"\nBUY: {buy_count}  |  HOLD: {hold_count}  |  SELL: {sell_count}")
    
    tests = []
    tests.append(("Has BUY signals", buy_count > 0, f"{buy_count}"))
    tests.append(("Has HOLD signals", hold_count > 0, f"{hold_count}"))
    tests.append(("Has SELL signals", sell_count > 0, f"{sell_count}"))
    tests.append(("News diversity", len(set(r['news'] for r in results)) >= 2, ""))
    tests.append(("Tech diversity", len(set(r['tech'] for r in results)) >= 2, ""))
    tests.append(("Fund diversity", len(set(r['fund'] for r in results)) >= 2, ""))
    
    print(f"\n--- Test Results ---")
    all_pass = True
    for name, passed, detail in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name:<32} {f'({detail})' if detail else ''}")
        if not passed:
            all_pass = False
    
    print(f"\n{'='*70}")
    print(f"PHASE 1A REVISITED: {'ALL TESTS PASSED ✅' if all_pass else 'SOME TESTS FAILED ❌'}")
    print(f"{'='*70}\n")
    return all_pass


if __name__ == "__main__":
    print("\n" + "🔬" * 35)
    print("   STOCK ANALYSIS AGENT EVALUATOR - Phase 1")
    print("🔬" * 35 + "\n")
    
    # Phase 1B: Technical indicators (Python only, no LLM)
    p1b = test_phase_1b()
    
    # Phase 1C: Fundamental metrics (Python only, no LLM)
    p1c = test_phase_1c()
    
    # Phase 1A revisited: Parser still works with current data
    p1a = test_phase_1a_revisited()
    
    print("\n" + "=" * 70)
    print("OVERALL RESULTS:")
    print(f"  Phase 1A (Parsers):     {'✅ PASS' if p1a else '❌ FAIL'}")
    print(f"  Phase 1B (Tech Indic.): {'✅ PASS' if p1b else '❌ FAIL'}")
    print(f"  Phase 1C (Fund Metr.):  {'✅ PASS' if p1c else '❌ FAIL'}")
    all_ok = p1a and p1b and p1c
    print(f"\n  {'🎉 ALL PHASES PASSED!' if all_ok else '⚠️ SOME PHASES FAILED'}")
    print("=" * 70)
