"""
Prediction Tracker - Records predictions and evaluates accuracy over time
Phase 3: Historical accuracy tracking and weight calibration
"""

import json
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import yfinance as yf


PREDICTIONS_FILE = "reports/prediction_history.json"


class PredictionTracker:
    """
    Stores predictions with timestamps and later verifies against actual outcomes.
    Used for agent weight calibration and accuracy monitoring.
    """
    
    def __init__(self, filepath: str = PREDICTIONS_FILE):
        self.filepath = filepath
        self.predictions = self._load()
    
    def _load(self) -> List[Dict]:
        """Load existing predictions from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def _save(self):
        """Save predictions to file"""
        os.makedirs(os.path.dirname(self.filepath) or '.', exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.predictions, f, indent=2, default=str)
    
    def record_prediction(self, symbol: str, quorum_result: Dict, 
                          current_price: float, agents: Dict = None):
        """
        Record a new prediction for future evaluation.
        
        Args:
            symbol: Stock ticker
            quorum_result: Output from QuorumScorer
            current_price: Price at time of prediction
            agents: Dict with individual agent signals for per-agent tracking
        """
        prediction = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price_at_prediction": current_price,
            "recommendation": quorum_result.get('recommendation', 'HOLD'),
            "confidence": quorum_result.get('confidence', 0.5),
            "weighted_score": quorum_result.get('weighted_score', 0.0),
            "consensus": quorum_result.get('consensus', ''),
            "agent_signals": {},
            "evaluation": None  # Filled in later
        }
        
        # Store individual agent signals for per-agent accuracy tracking
        if agents:
            votes = quorum_result.get('votes', {})
            for agent_name, vote_data in votes.items():
                prediction["agent_signals"][agent_name] = {
                    "signal": vote_data.get('signal', 'N/A'),
                    "vote": vote_data.get('vote', 0.0)
                }
        
        self.predictions.append(prediction)
        self._save()
        return prediction
    
    def evaluate_predictions(self, days_after: int = 10) -> Dict:
        """
        Evaluate past predictions against actual price movements.
        
        Args:
            days_after: Number of days to check after prediction
            
        Returns:
            Dictionary with accuracy metrics
        """
        evaluated = 0
        correct = 0
        agent_accuracy = {}
        results = []
        
        cutoff = datetime.now() - timedelta(days=days_after)
        
        for pred in self.predictions:
            if pred.get('evaluation') is not None:
                # Already evaluated
                results.append(pred)
                continue
            
            pred_time = datetime.fromisoformat(pred['timestamp'])
            if pred_time > cutoff:
                continue  # Too recent
            
            # Fetch actual price
            try:
                actual_price = self._get_price_days_after(
                    pred['symbol'], pred_time, days_after
                )
                if actual_price is None:
                    continue
                
                price_change_pct = ((actual_price - pred['price_at_prediction']) / 
                                   pred['price_at_prediction']) * 100
                
                # Determine if prediction was correct
                rec = pred['recommendation']
                if rec == 'BUY':
                    is_correct = price_change_pct > 0
                elif rec == 'SELL':
                    is_correct = price_change_pct < 0
                else:  # HOLD
                    is_correct = abs(price_change_pct) < 5  # Small move = correct HOLD
                
                pred['evaluation'] = {
                    "actual_price": actual_price,
                    "price_change_pct": round(price_change_pct, 2),
                    "is_correct": is_correct,
                    "evaluated_at": datetime.now().isoformat(),
                    "days_evaluated": days_after
                }
                
                evaluated += 1
                if is_correct:
                    correct += 1
                
                # Track per-agent accuracy
                for agent_name, agent_data in pred.get('agent_signals', {}).items():
                    if agent_name not in agent_accuracy:
                        agent_accuracy[agent_name] = {"correct": 0, "total": 0}
                    
                    agent_vote = agent_data.get('vote', 0.0)
                    # Agent was "correct" if it voted in the direction price moved
                    if (agent_vote > 0.1 and price_change_pct > 0) or \
                       (agent_vote < -0.1 and price_change_pct < 0) or \
                       (abs(agent_vote) <= 0.1 and abs(price_change_pct) < 5):
                        agent_accuracy[agent_name]["correct"] += 1
                    agent_accuracy[agent_name]["total"] += 1
                
                results.append(pred)
                
            except Exception as e:
                print(f"  Error evaluating {pred['symbol']}: {e}")
                continue
        
        self._save()
        
        # Compute summary
        overall_accuracy = (correct / evaluated * 100) if evaluated > 0 else None
        
        agent_rates = {}
        for agent, data in agent_accuracy.items():
            if data["total"] > 0:
                agent_rates[agent] = round(data["correct"] / data["total"] * 100, 1)
        
        return {
            "total_predictions": len(self.predictions),
            "evaluated": evaluated,
            "correct": correct,
            "overall_accuracy": overall_accuracy,
            "agent_accuracy": agent_rates,
            "details": results
        }
    
    def _get_price_days_after(self, symbol: str, pred_time: datetime, 
                              days: int) -> Optional[float]:
        """Get the stock price N days after prediction"""
        try:
            target_date = pred_time + timedelta(days=days)
            stock = yf.Ticker(symbol)
            # Fetch a small window around the target date
            start = target_date - timedelta(days=2)
            end = target_date + timedelta(days=2)
            hist = stock.history(start=start, end=end)
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except Exception:
            pass
        return None
    
    def get_suggested_weights(self) -> Optional[Dict]:
        """
        Suggest weight adjustments based on historical agent accuracy.
        Only returns suggestions if we have enough evaluation data.
        """
        eval_result = self.evaluate_predictions()
        
        if eval_result['evaluated'] < 10:
            return None  # Not enough data
        
        agent_rates = eval_result.get('agent_accuracy', {})
        if not agent_rates:
            return None
        
        # Normalize accuracy rates to weights
        total_accuracy = sum(agent_rates.values())
        if total_accuracy == 0:
            return None
        
        suggested = {}
        for agent, accuracy in agent_rates.items():
            suggested[agent] = round(accuracy / total_accuracy, 3)
        
        return {
            "current_weights": {
                "news": 0.15, "technical": 0.25, "fundamental": 0.25,
                "momentum": 0.20, "sector": 0.10, "forecast": 0.05
            },
            "suggested_weights": suggested,
            "based_on": eval_result['evaluated'],
            "overall_accuracy": eval_result['overall_accuracy']
        }
    
    def print_report(self):
        """Print a human-readable accuracy report"""
        result = self.evaluate_predictions()
        
        print("=" * 60)
        print("PREDICTION ACCURACY REPORT")
        print("=" * 60)
        print(f"Total predictions recorded: {result['total_predictions']}")
        print(f"Evaluated (≥10 days old):   {result['evaluated']}")
        
        if result['evaluated'] > 0:
            print(f"Correct predictions:        {result['correct']}/{result['evaluated']}")
            print(f"Overall accuracy:           {result['overall_accuracy']:.1f}%")
            
            if result['agent_accuracy']:
                print(f"\nPer-Agent Accuracy:")
                for agent, rate in sorted(result['agent_accuracy'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    print(f"  {agent:<15} {rate:.1f}%")
        else:
            print("No predictions old enough to evaluate yet.")
            print("Predictions need to be at least 10 days old.")
        
        print("=" * 60)


if __name__ == "__main__":
    tracker = PredictionTracker()
    tracker.print_report()
