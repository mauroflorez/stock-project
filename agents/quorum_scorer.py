"""
Quorum Scorer - Deterministic weighted voting system for stock recommendations
Replaces LLM-based recommendation with a transparent, reproducible scoring system
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class QuorumScorer:
    """
    Weighted voting system that aggregates signals from all agents.
    Each agent produces a signal that maps to a numeric vote.
    The final recommendation is based on the weighted sum.
    """
    
    # Agent weights (must sum to 1.0)
    WEIGHTS = {
        "news":       0.15,   # News sentiment
        "technical":  0.25,   # RSI, MACD, Bollinger (computed)
        "fundamental":0.25,   # PEG, ROE, P/E (computed)
        "momentum":   0.20,   # Relative strength, ROC, OBV
        "sector":     0.10,   # Sector performance
        "forecast":   0.05,   # Time series forecast direction
    }
    
    # Signal to vote mapping
    SIGNAL_MAP = {
        # News
        "Bullish": 1.0, "Neutral": 0.0, "Bearish": -1.0,
        # Technical
        "BULLISH": 1.0, "NEUTRAL": 0.0, "BEARISH": -1.0,
        # Fundamental
        "UNDERVALUED": 1.0, "FAIR": 0.0, "OVERVALUED": -1.0,
    }
    
    def __init__(self):
        self.name = "Quorum Scorer"
    
    def compute(self, 
                news_signal: str,
                technical_signal: str,
                technical_score: float,
                fundamental_signal: str,
                fundamental_score: float,
                momentum_signal: str = "NEUTRAL",
                momentum_score: float = 0.0,
                sector_signal: str = "NEUTRAL",
                sector_score: float = 0.0,
                forecast_direction: str = "flat",
                agent_details: Dict = None) -> Dict[str, Any]:
        """
        Compute the final quorum score and recommendation.
        
        Args:
            news_signal: Bullish/Neutral/Bearish
            technical_signal: BULLISH/NEUTRAL/BEARISH
            technical_score: Raw score from technical agent
            fundamental_signal: UNDERVALUED/FAIR/OVERVALUED
            fundamental_score: Raw score from fundamental agent
            momentum_signal: BULLISH/NEUTRAL/BEARISH
            momentum_score: Raw score from momentum agent
            sector_signal: BULLISH/NEUTRAL/BEARISH
            sector_score: Raw score from sector agent
            forecast_direction: up/down/flat
            agent_details: Optional dict with full agent reasoning
        
        Returns:
            Dictionary with quorum results
        """
        
        # Map signals to votes [-1, +1]
        news_vote = self.SIGNAL_MAP.get(news_signal, 0.0)
        tech_vote = max(-1, min(1, technical_score / 2))  # Normalize to [-1, 1]
        fund_vote = max(-1, min(1, fundamental_score / 2))
        mom_vote = max(-1, min(1, momentum_score / 2))
        sector_vote = max(-1, min(1, sector_score / 2))
        
        # Forecast vote
        forecast_vote = 0.0
        if forecast_direction == "up":
            forecast_vote = 1.0
        elif forecast_direction == "down":
            forecast_vote = -1.0
        
        # Compute weighted score
        votes = {
            "news": {"vote": news_vote, "signal": news_signal, "weight": self.WEIGHTS["news"]},
            "technical": {"vote": tech_vote, "signal": technical_signal, "weight": self.WEIGHTS["technical"]},
            "fundamental": {"vote": fund_vote, "signal": fundamental_signal, "weight": self.WEIGHTS["fundamental"]},
            "momentum": {"vote": mom_vote, "signal": momentum_signal, "weight": self.WEIGHTS["momentum"]},
            "sector": {"vote": sector_vote, "signal": sector_signal, "weight": self.WEIGHTS["sector"]},
            "forecast": {"vote": forecast_vote, "signal": forecast_direction, "weight": self.WEIGHTS["forecast"]},
        }
        
        weighted_sum = sum(v["vote"] * v["weight"] for v in votes.values())
        
        # Normalize to [0, 1] for confidence display (from [-1, +1] range)
        confidence = (weighted_sum + 1) / 2  # Maps -1→0, 0→0.5, +1→1
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine recommendation
        if weighted_sum >= 0.25:
            recommendation = "BUY"
        elif weighted_sum <= -0.25:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        # Determine strength
        abs_score = abs(weighted_sum)
        if abs_score >= 0.5:
            strength = "Strong"
        elif abs_score >= 0.25:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        # Count agreement
        bullish_count = sum(1 for v in votes.values() if v["vote"] > 0.1)
        bearish_count = sum(1 for v in votes.values() if v["vote"] < -0.1)
        neutral_count = 6 - bullish_count - bearish_count
        
        # Consensus check
        if bullish_count >= 5:
            consensus = "Strong Bullish Consensus"
        elif bearish_count >= 5:
            consensus = "Strong Bearish Consensus"
        elif bullish_count >= 4:
            consensus = "Bullish Majority"
        elif bearish_count >= 4:
            consensus = "Bearish Majority"
        elif bullish_count == bearish_count:
            consensus = "Split Opinion"
        else:
            consensus = "Mixed Signals"
        
        return {
            "recommendation": recommendation,
            "strength": strength,
            "confidence": round(confidence, 3),
            "weighted_score": round(weighted_sum, 3),
            "consensus": consensus,
            "votes": votes,
            "vote_summary": {
                "bullish": bullish_count,
                "neutral": neutral_count,
                "bearish": bearish_count
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def format_scorecard(self, result: Dict) -> str:
        """Format quorum results as a readable scorecard"""
        lines = []
        lines.append(f"╔══════════════════════════════════════════╗")
        lines.append(f"║  QUORUM VERDICT: {result['recommendation']:>4}  ({result['strength']})")
        lines.append(f"║  Confidence: {result['confidence']:.1%}  |  Score: {result['weighted_score']:+.3f}")
        lines.append(f"║  {result['consensus']}")
        lines.append(f"╠══════════════════════════════════════════╣")
        
        for name, v in result['votes'].items():
            vote_bar = "▓" * int(abs(v['vote']) * 5)
            direction = "+" if v['vote'] > 0 else "-" if v['vote'] < 0 else "○"
            lines.append(f"║  {name:<13} {v['signal']:<13} {direction}{vote_bar:<6} ({v['weight']:.0%})")
        
        lines.append(f"╠══════════════════════════════════════════╣")
        vs = result['vote_summary']
        lines.append(f"║  👍 {vs['bullish']} Bullish  |  ○ {vs['neutral']} Neutral  |  👎 {vs['bearish']} Bearish")
        lines.append(f"╚══════════════════════════════════════════╝")
        
        return "\n".join(lines)


if __name__ == "__main__":
    scorer = QuorumScorer()
    
    # Test case 1: Strong buy
    result = scorer.compute(
        news_signal="Bullish",
        technical_signal="BULLISH",
        technical_score=1.5,
        fundamental_signal="UNDERVALUED",
        fundamental_score=2.0,
        momentum_signal="BULLISH",
        momentum_score=1.0,
        sector_signal="BULLISH",
        sector_score=1.0,
        forecast_direction="up"
    )
    print("=== Test 1: Strong Buy ===")
    print(scorer.format_scorecard(result))
    
    # Test case 2: Strong sell
    result2 = scorer.compute(
        news_signal="Bearish",
        technical_signal="BEARISH",
        technical_score=-1.5,
        fundamental_signal="OVERVALUED",
        fundamental_score=-1.5,
        momentum_signal="BEARISH",
        momentum_score=-1.0,
        sector_signal="BEARISH",
        sector_score=-1.0,
        forecast_direction="down"
    )
    print("\n=== Test 2: Strong Sell ===")
    print(scorer.format_scorecard(result2))
    
    # Test case 3: Mixed
    result3 = scorer.compute(
        news_signal="Bullish",
        technical_signal="BEARISH",
        technical_score=-1.0,
        fundamental_signal="UNDERVALUED",
        fundamental_score=1.5,
        momentum_signal="NEUTRAL",
        momentum_score=0.0,
        sector_signal="NEUTRAL",
        sector_score=0.0,
        forecast_direction="flat"
    )
    print("\n=== Test 3: Mixed Signals ===")
    print(scorer.format_scorecard(result3))
