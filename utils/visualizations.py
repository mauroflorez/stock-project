"""
Visualization utilities for stock analysis and forecasting
Generates interactive plots for time series data and forecasts
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class StockVisualizer:
    """
    Creates visualizations for stock data and forecasts.
    Supports both Plotly (interactive) and Matplotlib (static) outputs.
    """

    def __init__(self, output_dir: str = "docs/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_forecast_plot_plotly(
        self,
        symbol: str,
        historical_prices: List[float],
        historical_dates: List[str],
        forecast_values: List[float],
        forecast_dates: List[str],
        lower_bound: List[float],
        upper_bound: List[float],
        timeframe: str = "1y"
    ) -> str:
        """
        Create an interactive Plotly forecast chart.

        Returns:
            HTML string containing the interactive chart
        """
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly not available for interactive charts</p>"

        fig = go.Figure()

        # Convert dates
        hist_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in historical_dates]
        fc_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in forecast_dates]

        # Historical prices
        fig.add_trace(go.Scatter(
            x=hist_dates,
            y=historical_prices,
            mode='lines',
            name='Historical',
            line=dict(color='#667eea', width=2)
        ))

        # Forecast
        fig.add_trace(go.Scatter(
            x=fc_dates,
            y=forecast_values,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#10b981', width=2, dash='dash'),
            marker=dict(size=6)
        ))

        # Confidence interval
        fig.add_trace(go.Scatter(
            x=fc_dates + fc_dates[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval',
            showlegend=True
        ))

        # Add vertical line at forecast start (without annotation to avoid datetime issue)
        if hist_dates:
            fig.add_shape(
                type="line",
                x0=hist_dates[-1],
                x1=hist_dates[-1],
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="gray", width=1, dash="dash")
            )

        fig.update_layout(
            title=f'{symbol} Price Forecast ({timeframe} history)',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=60, r=30, t=60, b=60)
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def create_forecast_plot_matplotlib(
        self,
        symbol: str,
        historical_prices: List[float],
        historical_dates: List[str],
        forecast_values: List[float],
        forecast_dates: List[str],
        lower_bound: List[float],
        upper_bound: List[float],
        timeframe: str = "1y",
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a static Matplotlib forecast chart.

        Returns:
            Path to saved image or None
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        # Convert dates
        hist_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in historical_dates]
        fc_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in forecast_dates]

        # Plot historical
        ax.plot(hist_dates, historical_prices, color='#667eea', linewidth=2, label='Historical')

        # Plot forecast
        ax.plot(fc_dates, forecast_values, color='#10b981', linewidth=2, linestyle='--', marker='o', markersize=4, label='Forecast')

        # Confidence interval
        ax.fill_between(fc_dates, lower_bound, upper_bound, color='#10b981', alpha=0.2, label='95% CI')

        # Vertical line at forecast start
        if hist_dates:
            ax.axvline(x=hist_dates[-1], color='gray', linestyle='--', alpha=0.7)

        ax.set_title(f'{symbol} Price Forecast ({timeframe} history)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # Save to default location
            filename = f"{self.output_dir}/{symbol.lower()}_forecast_{timeframe}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            return filename

    def create_multi_timeframe_chart(
        self,
        symbol: str,
        forecast_data: Dict
    ) -> Dict[str, str]:
        """
        Create charts for multiple timeframes (1y, 1m, 10d).

        Returns:
            Dictionary mapping timeframe to chart HTML/path
        """
        charts = {}

        # Get ensemble forecast data
        ensemble = forecast_data.get('models', {}).get('ensemble', {})
        if 'error' in ensemble:
            return {"error": "No valid forecast data"}

        forecast_values = ensemble.get('forecast_values', [])
        lower_bound = ensemble.get('lower_bound', [])
        upper_bound = ensemble.get('upper_bound', [])
        forecast_dates = forecast_data.get('future_dates', [])

        historical_data = forecast_data.get('historical_data', {})

        for timeframe, label in [('1y', '1 Year'), ('1m', '1 Month'), ('10d', '10 Days')]:
            hist = historical_data.get(timeframe, {})
            prices = hist.get('prices', [])
            dates = hist.get('dates', [])

            if prices and dates:
                if PLOTLY_AVAILABLE:
                    charts[timeframe] = self.create_forecast_plot_plotly(
                        symbol=symbol,
                        historical_prices=prices,
                        historical_dates=dates,
                        forecast_values=forecast_values,
                        forecast_dates=forecast_dates,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        timeframe=label
                    )
                elif MATPLOTLIB_AVAILABLE:
                    charts[timeframe] = self.create_forecast_plot_matplotlib(
                        symbol=symbol,
                        historical_prices=prices,
                        historical_dates=dates,
                        forecast_values=forecast_values,
                        forecast_dates=forecast_dates,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        timeframe=label
                    )

        return charts

    def generate_forecast_summary_html(self, forecast_data: Dict) -> str:
        """
        Generate HTML summary of forecast results.
        """
        summary = forecast_data.get('summary', {})
        symbol = forecast_data.get('symbol', 'Unknown')
        current_price = forecast_data.get('current_price', 0)

        html = f"""
        <div class="forecast-summary">
            <h3>📈 Price Forecast for {symbol}</h3>
            <div class="forecast-metrics">
                <div class="metric-box">
                    <span class="metric-label">Current Price</span>
                    <span class="metric-value">${current_price:.2f}</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Next Day Prediction</span>
                    <span class="metric-value">${summary.get('next_day_prediction', 0):.2f}</span>
                    <span class="metric-range">{summary.get('next_day_range', 'N/A')}</span>
                    <span class="metric-return">{summary.get('next_day_expected_return', 'N/A')}</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">10-Day Prediction</span>
                    <span class="metric-value">${summary.get('day_10_prediction', 0):.2f}</span>
                    <span class="metric-range">{summary.get('day_10_range', 'N/A')}</span>
                    <span class="metric-return">{summary.get('day_10_expected_return', 'N/A')}</span>
                </div>
            </div>
            <div class="models-info">
                <strong>Models:</strong> {', '.join(summary.get('models_used', ['N/A']))} |
                <strong>Confidence:</strong> {summary.get('confidence', 'N/A')}
            </div>
        </div>
        """
        return html


if __name__ == "__main__":
    # Test visualizations
    print("Testing Stock Visualizer...")

    # Create sample data
    import random
    base_price = 100
    prices = [base_price + random.uniform(-5, 5) + i * 0.1 for i in range(365)]
    dates = [(datetime.now() - timedelta(days=365-i)).strftime('%Y-%m-%d') for i in range(365)]

    forecast_values = [prices[-1] + i * 0.5 for i in range(10)]
    forecast_dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(10)]
    lower_bound = [v - 5 for v in forecast_values]
    upper_bound = [v + 5 for v in forecast_values]

    visualizer = StockVisualizer()

    if PLOTLY_AVAILABLE:
        html = visualizer.create_forecast_plot_plotly(
            symbol="TEST",
            historical_prices=prices,
            historical_dates=dates,
            forecast_values=forecast_values,
            forecast_dates=forecast_dates,
            lower_bound=lower_bound,
            upper_bound=upper_bound
        )
        print(f"Plotly chart generated: {len(html)} characters")

    if MATPLOTLIB_AVAILABLE:
        path = visualizer.create_forecast_plot_matplotlib(
            symbol="TEST",
            historical_prices=prices[-30:],
            historical_dates=dates[-30:],
            forecast_values=forecast_values,
            forecast_dates=forecast_dates,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            timeframe="1m"
        )
        print(f"Matplotlib chart saved to: {path}")
