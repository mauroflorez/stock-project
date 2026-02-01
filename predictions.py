"""
Time Series Prediction Module
Uses Prophet and ARIMA for stock price forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not available. Install with: pip install prophet")

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available. Install with: pip install statsmodels")

from config import PREDICTION_DAYS


class TimeSeriesPredictor:
    """Predict stock prices using time series models"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.predictions = {}
        
    def predict_with_prophet(self, df: pd.DataFrame, days: int = PREDICTION_DAYS) -> dict:
        """
        Use Facebook Prophet for predictions
        """
        if not PROPHET_AVAILABLE:
            return {"error": "Prophet not installed"}
        
        try:
            # Prepare data for Prophet
            prophet_df = pd.DataFrame({
                'ds': df.index,
                'y': df['Close'].values
            })
            
            # Create and fit model
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            
            model.fit(prophet_df)
            
            # Make predictions
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            
            # Extract predictions
            last_actual = df['Close'].iloc[-1]
            future_predictions = forecast.tail(days)
            predicted_price = future_predictions['yhat'].iloc[-1]
            
            trend = "UPWARD" if predicted_price > last_actual else "DOWNWARD"
            change_pct = ((predicted_price - last_actual) / last_actual) * 100
            
            return {
                "method": "Prophet",
                "current_price": float(last_actual),
                "predicted_price": float(predicted_price),
                "change_percent": float(change_pct),
                "trend": trend,
                "confidence": "Medium-High",
                "forecast_summary": f"${predicted_price:.2f} in {days} days ({change_pct:+.2f}%)",
                "predictions": future_predictions[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')
            }
            
        except Exception as e:
            return {"error": f"Prophet prediction failed: {str(e)}"}
    
    def predict_with_arima(self, df: pd.DataFrame, days: int = PREDICTION_DAYS) -> dict:
        """
        Use ARIMA model for predictions
        """
        if not STATSMODELS_AVAILABLE:
            return {"error": "statsmodels not installed"}
        
        try:
            # Use closing prices
            prices = df['Close'].values
            
            # Fit ARIMA model (auto-select best parameters)
            # Using simple ARIMA(1,1,1) as default
            model = ARIMA(prices, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Make predictions
            forecast = fitted_model.forecast(steps=days)
            
            last_actual = prices[-1]
            predicted_price = forecast[-1]
            
            trend = "UPWARD" if predicted_price > last_actual else "DOWNWARD"
            change_pct = ((predicted_price - last_actual) / last_actual) * 100
            
            return {
                "method": "ARIMA(1,1,1)",
                "current_price": float(last_actual),
                "predicted_price": float(predicted_price),
                "change_percent": float(change_pct),
                "trend": trend,
                "confidence": "Medium",
                "forecast_summary": f"${predicted_price:.2f} in {days} days ({change_pct:+.2f}%)"
            }
            
        except Exception as e:
            return {"error": f"ARIMA prediction failed: {str(e)}"}
    
    def predict_simple_moving_average(self, df: pd.DataFrame, days: int = PREDICTION_DAYS) -> dict:
        """
        Simple moving average prediction (fallback method)
        """
        try:
            prices = df['Close'].values
            
            # Calculate trend using recent prices
            recent_days = min(30, len(prices))
            recent_prices = prices[-recent_days:]
            
            # Linear regression on recent data
            x = np.arange(len(recent_prices))
            coeffs = np.polyfit(x, recent_prices, 1)
            
            # Predict
            future_x = len(recent_prices) + days - 1
            predicted_price = coeffs[0] * future_x + coeffs[1]
            
            last_actual = prices[-1]
            trend = "UPWARD" if predicted_price > last_actual else "DOWNWARD"
            change_pct = ((predicted_price - last_actual) / last_actual) * 100
            
            return {
                "method": "Moving Average Trend",
                "current_price": float(last_actual),
                "predicted_price": float(predicted_price),
                "change_percent": float(change_pct),
                "trend": trend,
                "confidence": "Low-Medium",
                "forecast_summary": f"${predicted_price:.2f} in {days} days ({change_pct:+.2f}%)"
            }
            
        except Exception as e:
            return {"error": f"Simple prediction failed: {str(e)}"}
    
    def get_best_prediction(self, df: pd.DataFrame, days: int = PREDICTION_DAYS) -> dict:
        """
        Try multiple methods and return the best available prediction
        """
        # Try Prophet first (most sophisticated)
        if PROPHET_AVAILABLE:
            print(f"  Using Prophet for {self.ticker}...")
            result = self.predict_with_prophet(df, days)
            if "error" not in result:
                return result
        
        # Try ARIMA second
        if STATSMODELS_AVAILABLE:
            print(f"  Using ARIMA for {self.ticker}...")
            result = self.predict_with_arima(df, days)
            if "error" not in result:
                return result
        
        # Fallback to simple method
        print(f"  Using simple trend analysis for {self.ticker}...")
        return self.predict_simple_moving_average(df, days)
    
    def calculate_volatility(self, df: pd.DataFrame) -> dict:
        """
        Calculate various volatility metrics
        """
        returns = df['Close'].pct_change().dropna()
        
        return {
            "daily_volatility": float(returns.std() * 100),
            "annualized_volatility": float(returns.std() * np.sqrt(252) * 100),
            "30d_volatility": float(returns.tail(30).std() * 100)
        }


def test_predictions():
    """Test the prediction functions"""
    print("Testing Time Series Predictions...")
    
    # Create sample data
    dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
    prices = 100 + np.cumsum(np.random.randn(365) * 2)
    
    df = pd.DataFrame({'Close': prices}, index=dates)
    
    predictor = TimeSeriesPredictor("TEST")
    
    print("\nTesting prediction methods...")
    result = predictor.get_best_prediction(df, days=30)
    
    print(f"\nMethod: {result.get('method', 'N/A')}")
    print(f"Current: ${result.get('current_price', 0):.2f}")
    print(f"Predicted: ${result.get('predicted_price', 0):.2f}")
    print(f"Change: {result.get('change_percent', 0):.2f}%")
    print(f"Trend: {result.get('trend', 'N/A')}")
    
    print("\n✓ Prediction tests complete!")


if __name__ == "__main__":
    test_predictions()
