"""
Stock Investment Planner - Streamlit Dashboard
Interactive web application for AI-powered stock analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import STOCKS, STOCK_NAMES, OLLAMA_MODEL
from utils.data_fetcher import DataFetcher
from utils.ollama_client import OllamaClient
from agents.forecaster import ForecasterAgent

# Page config
st.set_page_config(
    page_title="Stock Investment Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .forecast-card {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .agent-card {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    .recommendation-buy { background: #dcfce7; border-color: #10b981; }
    .recommendation-hold { background: #fef3c7; border-color: #f59e0b; }
    .recommendation-sell { background: #fee2e2; border-color: #ef4444; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol: str, days: int = 365):
    """Fetch stock data with caching"""
    fetcher = DataFetcher()
    return fetcher.get_stock_prices(symbol, days)


@st.cache_data(ttl=300)
def fetch_news(symbol: str, company_name: str):
    """Fetch news with caching"""
    fetcher = DataFetcher()
    return fetcher.get_news(symbol, company_name)


def check_ollama():
    """Check if Ollama is available"""
    client = OllamaClient()
    return client.is_available()


def create_price_chart(stock_data: dict, forecast_data: dict = None):
    """Create interactive price chart with forecast"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price History & Forecast', 'Trading Volume')
    )

    dates = pd.to_datetime(stock_data['historical_dates'])
    prices = stock_data['historical_close']
    volumes = stock_data.get('historical_volume', [])

    # Price line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Historical Price',
            line=dict(color='#667eea', width=2)
        ),
        row=1, col=1
    )

    # Add forecast if available
    if forecast_data and 'models' in forecast_data:
        ensemble = forecast_data['models'].get('ensemble', {})
        if 'error' not in ensemble:
            future_dates = pd.to_datetime(forecast_data['future_dates'])
            forecast_values = ensemble['forecast_values']
            lower_bound = ensemble['lower_bound']
            upper_bound = ensemble['upper_bound']

            # Forecast line
            fig.add_trace(
                go.Scatter(
                    x=future_dates,
                    y=forecast_values,
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#10b981', width=2, dash='dash'),
                    marker=dict(size=6)
                ),
                row=1, col=1
            )

            # Confidence interval
            fig.add_trace(
                go.Scatter(
                    x=list(future_dates) + list(future_dates)[::-1],
                    y=list(upper_bound) + list(lower_bound)[::-1],
                    fill='toself',
                    fillcolor='rgba(16, 185, 129, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% Confidence Interval',
                    showlegend=True
                ),
                row=1, col=1
            )

    # Volume bars
    if volumes:
        colors = ['#10b981' if prices[i] >= prices[i-1] else '#ef4444'
                  for i in range(1, len(prices))]
        colors.insert(0, '#10b981')

        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=600,
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

    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_forecast_comparison_chart(forecast_data: dict):
    """Create chart comparing different forecast models"""
    if not forecast_data or 'models' not in forecast_data:
        return None

    fig = go.Figure()
    future_dates = pd.to_datetime(forecast_data['future_dates'])

    colors = {
        'arima': '#667eea',
        'exponential_smoothing': '#f59e0b',
        'prophet': '#10b981',
        'ensemble': '#ef4444'
    }

    for model_name, model_data in forecast_data['models'].items():
        if 'error' not in model_data and 'forecast_values' in model_data:
            fig.add_trace(
                go.Scatter(
                    x=future_dates,
                    y=model_data['forecast_values'],
                    mode='lines+markers',
                    name=model_data.get('model', model_name.upper()),
                    line=dict(color=colors.get(model_name, '#6b7280'), width=2)
                )
            )

    fig.update_layout(
        title='Forecast Model Comparison',
        xaxis_title='Date',
        yaxis_title='Predicted Price ($)',
        template='plotly_white',
        height=400
    )

    return fig


def main():
    # Header
    st.markdown('<p class="main-header">📊 Stock Investment Planner</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Multi-Agent Stock Analysis with Time Series Forecasting</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Stock selector
        selected_stock = st.selectbox(
            "Select Stock",
            options=STOCKS,
            format_func=lambda x: f"{x} - {STOCK_NAMES.get(x, x)}"
        )

        # Time range
        time_range = st.selectbox(
            "Historical Data Range",
            options=["1 Month", "3 Months", "6 Months", "1 Year"],
            index=3
        )

        days_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365}
        selected_days = days_map[time_range]

        # Forecast days
        forecast_days = st.slider("Forecast Days", min_value=1, max_value=30, value=10)

        st.divider()

        # Ollama status
        st.subheader("🤖 AI Status")
        ollama_status = check_ollama()
        if ollama_status:
            st.success(f"✅ Ollama Running ({OLLAMA_MODEL})")
        else:
            st.error("❌ Ollama Not Running")
            st.caption("Start with: `ollama serve`")

        st.divider()

        # Run analysis button
        run_analysis = st.button("🚀 Run Full Analysis", type="primary", disabled=not ollama_status)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📈 {selected_stock} - {STOCK_NAMES.get(selected_stock, selected_stock)}")

        # Fetch data
        with st.spinner("Fetching stock data..."):
            stock_data = fetch_stock_data(selected_stock, selected_days)

        if "error" in stock_data:
            st.error(f"Error fetching data: {stock_data['error']}")
            return

        # Run forecast
        with st.spinner("Generating forecasts..."):
            forecaster = ForecasterAgent()
            forecast_result = forecaster.analyze(
                prices=stock_data['historical_close'],
                dates=stock_data['historical_dates'],
                symbol=selected_stock,
                forecast_days=forecast_days
            )

        # Price chart
        fig = create_price_chart(stock_data, forecast_result)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Current metrics
        st.subheader("📊 Current Metrics")

        current_price = stock_data.get('current_price', 0)
        day_change = stock_data.get('day_change', 0)
        day_change_pct = stock_data.get('day_change_percent', 0)

        st.metric(
            label="Current Price",
            value=f"${current_price:.2f}",
            delta=f"{day_change:+.2f} ({day_change_pct:+.2f}%)"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("52W High", f"${stock_data.get('52_week_high', 0):.2f}")
            st.metric("P/E Ratio", f"{stock_data.get('pe_ratio', 'N/A')}")
        with col_b:
            st.metric("52W Low", f"${stock_data.get('52_week_low', 0):.2f}")
            market_cap = stock_data.get('market_cap', 0)
            if market_cap:
                if market_cap >= 1e12:
                    cap_str = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    cap_str = f"${market_cap/1e9:.2f}B"
                else:
                    cap_str = f"${market_cap/1e6:.2f}M"
            else:
                cap_str = "N/A"
            st.metric("Market Cap", cap_str)

    # Forecast section
    st.divider()
    st.subheader("🔮 Price Forecast")

    if forecast_result and 'summary' in forecast_result:
        summary = forecast_result['summary']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Next Day Prediction**")
            next_pred = summary.get('next_day_prediction', current_price)
            next_return = summary.get('next_day_expected_return', '0%')
            color = "green" if '+' in str(next_return) else "red"
            st.markdown(f"### ${next_pred:.2f}")
            st.markdown(f"<span style='color:{color}'>{next_return}</span>", unsafe_allow_html=True)
            st.caption(summary.get('next_day_range', ''))

        with col2:
            st.markdown("**10-Day Prediction**")
            day10_pred = summary.get('day_10_prediction', current_price)
            day10_return = summary.get('day_10_expected_return', '0%')
            color = "green" if '+' in str(day10_return) else "red"
            st.markdown(f"### ${day10_pred:.2f}")
            st.markdown(f"<span style='color:{color}'>{day10_return}</span>", unsafe_allow_html=True)
            st.caption(summary.get('day_10_range', ''))

        with col3:
            st.markdown("**Model Info**")
            st.markdown(f"**Confidence:** {summary.get('confidence', 'N/A')}")
            models = summary.get('models_used', [])
            st.caption(f"Models: {', '.join(models)}")

    # Model comparison chart
    comparison_fig = create_forecast_comparison_chart(forecast_result)
    if comparison_fig:
        st.plotly_chart(comparison_fig, use_container_width=True)

    # Full analysis section (if button clicked)
    if run_analysis:
        st.divider()
        st.subheader("🤖 Full AI Agent Analysis")

        # Import agents
        from agents.news_analyst import NewsAnalystAgent
        from agents.statistical_expert import StatisticalExpertAgent
        from agents.financial_expert import FinancialExpertAgent
        from agents.investment_synthesizer import InvestmentSynthesizerAgent

        fetcher = DataFetcher()

        # News Analysis
        with st.expander("🗞️ News Analysis", expanded=True):
            with st.spinner("Analyzing news..."):
                news_data = fetch_news(selected_stock, STOCK_NAMES.get(selected_stock, selected_stock))
                news_formatted = fetcher.format_news_for_agent(news_data)
                news_agent = NewsAnalystAgent()
                news_result = news_agent.analyze(news_formatted, selected_stock)
            st.markdown(news_result.get('analysis', 'No analysis available'))

        # Statistical Analysis
        with st.expander("📈 Statistical Analysis", expanded=True):
            with st.spinner("Running statistical analysis..."):
                stock_formatted = fetcher.format_price_data_for_agent(stock_data)
                stats_agent = StatisticalExpertAgent()
                stats_result = stats_agent.analyze(
                    stock_formatted,
                    stock_data.get('historical_close', []),
                    selected_stock
                )
            st.markdown(stats_result.get('analysis', 'No analysis available'))

        # Financial Analysis
        with st.expander("💼 Financial Analysis", expanded=True):
            with st.spinner("Running financial analysis..."):
                financial_agent = FinancialExpertAgent()
                financial_result = financial_agent.analyze(stock_formatted, selected_stock)
            st.markdown(financial_result.get('analysis', 'No analysis available'))

        # Investment Synthesis
        with st.expander("🎯 Investment Synthesis", expanded=True):
            with st.spinner("Synthesizing all analyses..."):
                synthesizer = InvestmentSynthesizerAgent()
                forecast_summary = f"""
FORECAST: Next Day ${forecast_result['summary']['next_day_prediction']:.2f} ({forecast_result['summary']['next_day_expected_return']}),
10-Day ${forecast_result['summary']['day_10_prediction']:.2f} ({forecast_result['summary']['day_10_expected_return']})
"""
                synthesis_result = synthesizer.synthesize(
                    news_result.get('analysis', ''),
                    stats_result.get('analysis', '') + forecast_summary,
                    financial_result.get('analysis', ''),
                    selected_stock
                )
            st.markdown(synthesis_result.get('synthesis', 'No synthesis available'))

    # Footer
    st.divider()
    st.caption("⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice. Always consult a qualified financial advisor.")


if __name__ == "__main__":
    main()
