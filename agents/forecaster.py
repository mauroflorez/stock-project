"""
Forecaster Agent - Time series forecasting with ARIMA and statistical models
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


class ForecasterAgent:
    """
    Agent specialized in time series forecasting using statistical models.
    Uses ARIMA, Exponential Smoothing, and optionally Prophet for predictions.
    """

    def __init__(self):
        self.name = "Forecaster"

    def prepare_data(self, prices: List[float], dates: List[str]) -> pd.DataFrame:
        """Prepare data for modeling"""
        df = pd.DataFrame({
            'ds': pd.to_datetime(dates),
            'y': prices
        })
        df = df.sort_values('ds').reset_index(drop=True)
        return df

    def fit_arima(self, prices: List[float], forecast_days: int = 10) -> Dict:
        """
        Fit ARIMA model and generate forecasts with confidence intervals.

        Args:
            prices: Historical closing prices
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with forecasts and confidence intervals
        """
        if not STATSMODELS_AVAILABLE:
            return {"error": "statsmodels not installed"}

        try:
            # Convert to numpy array
            y = np.array(prices)

            # Fit ARIMA(5,1,0) - common for stock prices
            # p=5 (autoregressive terms), d=1 (differencing), q=0 (moving average)
            model = ARIMA(y, order=(5, 1, 0))
            fitted = model.fit()

            # Generate forecasts
            forecast = fitted.get_forecast(steps=forecast_days)
            predicted_mean = forecast.predicted_mean
            conf_int = forecast.conf_int(alpha=0.05)  # 95% confidence interval

            # Calculate prediction for next day and 10 days
            next_day_pred = predicted_mean[0]
            day_10_pred = predicted_mean[-1] if forecast_days >= 10 else predicted_mean[-1]

            return {
                "model": "ARIMA(5,1,0)",
                "forecast_values": predicted_mean.tolist(),
                "lower_bound": conf_int[:, 0].tolist(),
                "upper_bound": conf_int[:, 1].tolist(),
                "next_day": {
                    "prediction": float(next_day_pred),
                    "lower": float(conf_int[0, 0]),
                    "upper": float(conf_int[0, 1])
                },
                "day_10": {
                    "prediction": float(day_10_pred),
                    "lower": float(conf_int[-1, 0]),
                    "upper": float(conf_int[-1, 1])
                },
                "aic": fitted.aic,
                "bic": fitted.bic
            }
        except Exception as e:
            return {"error": f"ARIMA fitting failed: {str(e)}"}

    def fit_exponential_smoothing(self, prices: List[float], forecast_days: int = 10) -> Dict:
        """
        Fit Exponential Smoothing (Holt-Winters) model.
        """
        if not STATSMODELS_AVAILABLE:
            return {"error": "statsmodels not installed"}

        try:
            y = np.array(prices)

            # Fit Holt's linear trend model (no seasonality for daily stock data)
            model = ExponentialSmoothing(
                y,
                trend='add',
                seasonal=None,
                damped_trend=True
            )
            fitted = model.fit()

            # Generate forecasts
            forecast = fitted.forecast(forecast_days)

            # Approximate confidence intervals using fitted residuals
            residuals = fitted.resid
            std_resid = np.std(residuals)

            lower_bound = forecast - 1.96 * std_resid
            upper_bound = forecast + 1.96 * std_resid

            return {
                "model": "Holt-Winters (Additive Trend)",
                "forecast_values": forecast.tolist(),
                "lower_bound": lower_bound.tolist(),
                "upper_bound": upper_bound.tolist(),
                "next_day": {
                    "prediction": float(forecast[0]),
                    "lower": float(lower_bound[0]),
                    "upper": float(upper_bound[0])
                },
                "day_10": {
                    "prediction": float(forecast[-1]),
                    "lower": float(lower_bound[-1]),
                    "upper": float(upper_bound[-1])
                }
            }
        except Exception as e:
            return {"error": f"Exponential Smoothing failed: {str(e)}"}

    def fit_prophet(self, prices: List[float], dates: List[str], forecast_days: int = 10) -> Dict:
        """
        Fit Facebook Prophet model for forecasting.
        """
        if not PROPHET_AVAILABLE:
            return {"error": "prophet not installed"}

        try:
            df = self.prepare_data(prices, dates)

            # Initialize and fit Prophet
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(df)

            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_days)
            forecast = model.predict(future)

            # Get only the forecast period
            forecast_only = forecast.tail(forecast_days)

            return {
                "model": "Prophet",
                "forecast_values": forecast_only['yhat'].tolist(),
                "lower_bound": forecast_only['yhat_lower'].tolist(),
                "upper_bound": forecast_only['yhat_upper'].tolist(),
                "next_day": {
                    "prediction": float(forecast_only['yhat'].iloc[0]),
                    "lower": float(forecast_only['yhat_lower'].iloc[0]),
                    "upper": float(forecast_only['yhat_upper'].iloc[0])
                },
                "day_10": {
                    "prediction": float(forecast_only['yhat'].iloc[-1]),
                    "lower": float(forecast_only['yhat_lower'].iloc[-1]),
                    "upper": float(forecast_only['yhat_upper'].iloc[-1])
                },
                "forecast_dates": forecast_only['ds'].dt.strftime('%Y-%m-%d').tolist()
            }
        except Exception as e:
            return {"error": f"Prophet fitting failed: {str(e)}"}

    def generate_ensemble_forecast(self, arima_result: Dict, ews_result: Dict, prophet_result: Optional[Dict] = None) -> Dict:
        """
        Combine forecasts from multiple models into an ensemble prediction.
        """
        forecasts = []
        weights = []

        if "error" not in arima_result:
            forecasts.append(arima_result)
            weights.append(0.4)  # ARIMA weight

        if "error" not in ews_result:
            forecasts.append(ews_result)
            weights.append(0.3)  # EWS weight

        if prophet_result and "error" not in prophet_result:
            forecasts.append(prophet_result)
            weights.append(0.3)  # Prophet weight

        if not forecasts:
            return {"error": "No models successfully fitted"}

        # Normalize weights
        total_weight = sum(weights[:len(forecasts)])
        weights = [w / total_weight for w in weights[:len(forecasts)]]

        # Calculate weighted ensemble
        ensemble_values = np.zeros(len(forecasts[0]['forecast_values']))
        ensemble_lower = np.zeros(len(forecasts[0]['lower_bound']))
        ensemble_upper = np.zeros(len(forecasts[0]['upper_bound']))

        for i, (forecast, weight) in enumerate(zip(forecasts, weights)):
            ensemble_values += weight * np.array(forecast['forecast_values'])
            ensemble_lower += weight * np.array(forecast['lower_bound'])
            ensemble_upper += weight * np.array(forecast['upper_bound'])

        return {
            "model": "Ensemble (ARIMA + Holt-Winters" + (" + Prophet)" if prophet_result and "error" not in prophet_result else ")"),
            "forecast_values": ensemble_values.tolist(),
            "lower_bound": ensemble_lower.tolist(),
            "upper_bound": ensemble_upper.tolist(),
            "next_day": {
                "prediction": float(ensemble_values[0]),
                "lower": float(ensemble_lower[0]),
                "upper": float(ensemble_upper[0])
            },
            "day_10": {
                "prediction": float(ensemble_values[-1]),
                "lower": float(ensemble_lower[-1]),
                "upper": float(ensemble_upper[-1])
            },
            "models_used": [f['model'] for f in forecasts],
            "weights": weights
        }

    def analyze(self, prices: List[float], dates: List[str], symbol: str, forecast_days: int = 10) -> Dict:
        """
        Perform complete forecasting analysis.

        Args:
            prices: List of historical closing prices
            dates: List of dates corresponding to prices
            symbol: Stock ticker symbol
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with all forecasting results
        """
        print(f"🔮 {self.name} is generating forecasts for {symbol}...")

        current_price = prices[-1]

        # Fit individual models
        arima_result = self.fit_arima(prices, forecast_days)
        ews_result = self.fit_exponential_smoothing(prices, forecast_days)
        prophet_result = self.fit_prophet(prices, dates, forecast_days) if PROPHET_AVAILABLE else {"error": "Prophet not available"}

        # Generate ensemble forecast
        ensemble_result = self.generate_ensemble_forecast(arima_result, ews_result, prophet_result)

        # Generate future dates
        last_date = pd.to_datetime(dates[-1])
        future_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(forecast_days)]

        # Calculate expected returns
        if "error" not in ensemble_result:
            next_day_return = ((ensemble_result['next_day']['prediction'] - current_price) / current_price) * 100
            day_10_return = ((ensemble_result['day_10']['prediction'] - current_price) / current_price) * 100
        else:
            next_day_return = 0
            day_10_return = 0

        # Prepare historical data for visualization (different timeframes)
        hist_1y = {"prices": prices, "dates": dates}
        hist_1m = {"prices": prices[-30:] if len(prices) >= 30 else prices,
                   "dates": dates[-30:] if len(dates) >= 30 else dates}
        hist_10d = {"prices": prices[-10:] if len(prices) >= 10 else prices,
                    "dates": dates[-10:] if len(dates) >= 10 else dates}

        result = {
            "agent": self.name,
            "symbol": symbol,
            "current_price": current_price,
            "forecast_days": forecast_days,
            "future_dates": future_dates,
            "models": {
                "arima": arima_result,
                "exponential_smoothing": ews_result,
                "prophet": prophet_result,
                "ensemble": ensemble_result
            },
            "summary": {
                "next_day_prediction": ensemble_result.get('next_day', {}).get('prediction', current_price),
                "next_day_range": f"${ensemble_result.get('next_day', {}).get('lower', current_price):.2f} - ${ensemble_result.get('next_day', {}).get('upper', current_price):.2f}",
                "next_day_expected_return": f"{next_day_return:+.2f}%",
                "day_10_prediction": ensemble_result.get('day_10', {}).get('prediction', current_price),
                "day_10_range": f"${ensemble_result.get('day_10', {}).get('lower', current_price):.2f} - ${ensemble_result.get('day_10', {}).get('upper', current_price):.2f}",
                "day_10_expected_return": f"{day_10_return:+.2f}%",
                "models_used": ensemble_result.get('models_used', []),
                "confidence": "Medium" if len(ensemble_result.get('models_used', [])) >= 2 else "Low"
            },
            "historical_data": {
                "1y": hist_1y,
                "1m": hist_1m,
                "10d": hist_10d
            }
        }

        print(f"✅ Forecast complete for {symbol}")
        return result


if __name__ == "__main__":
    # Test the forecaster
    from utils.data_fetcher import DataFetcher

    print("Testing Forecaster Agent...\n")

    fetcher = DataFetcher()
    stock_data = fetcher.get_stock_prices("GOOGL", days=365)

    if "error" not in stock_data:
        agent = ForecasterAgent()
        result = agent.analyze(
            prices=stock_data['historical_close'],
            dates=stock_data['historical_dates'],
            symbol="GOOGL",
            forecast_days=10
        )

        print("\n" + "="*80)
        print(f"Current Price: ${result['current_price']:.2f}")
        print(f"\nNext Day Forecast:")
        print(f"  Prediction: ${result['summary']['next_day_prediction']:.2f}")
        print(f"  Range: {result['summary']['next_day_range']}")
        print(f"  Expected Return: {result['summary']['next_day_expected_return']}")
        print(f"\n10-Day Forecast:")
        print(f"  Prediction: ${result['summary']['day_10_prediction']:.2f}")
        print(f"  Range: {result['summary']['day_10_range']}")
        print(f"  Expected Return: {result['summary']['day_10_expected_return']}")
        print(f"\nModels Used: {', '.join(result['summary']['models_used'])}")
        print(f"Confidence: {result['summary']['confidence']}")
    else:
        print(f"Error fetching data: {stock_data['error']}")
