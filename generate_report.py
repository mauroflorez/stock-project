"""
HTML Report Generator
Converts JSON analysis results into beautiful HTML reports for GitHub Pages
"""

import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import re
from datetime import datetime
from glob import glob
from typing import Dict, Any, List, Tuple


class HTMLReportGenerator:
    """Generates HTML reports from analysis results"""
    
    def __init__(self):
        self.output_dir = "reports"  # Where JSON analysis files are saved
        self.web_dir = "docs"  # GitHub Pages serves from /docs

    def markdown_to_html(self, text: str) -> str:
        """Convert markdown formatting to HTML"""
        if not text:
            return ""

        # Convert markdown headers (#### Header) before other processing
        text = re.sub(r'^#{1,6}\s+(.+)$', r'**\1**', text, flags=re.MULTILINE)

        # Convert **bold** to <strong>
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

        # Convert *italic* to <em> (but not bullet points)
        text = re.sub(r'(?<!\n)\*([^*\n]+)\*', r'<em>\1</em>', text)

        # Convert numbered lists (1. item)
        lines = text.split('\n')
        result_lines = []
        in_ol = False
        in_ul = False

        for line in lines:
            stripped = line.strip()

            # Check for numbered list item
            ol_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
            # Check for bullet list item
            ul_match = re.match(r'^[-*]\s+(.+)$', stripped)

            if ol_match:
                if not in_ol:
                    if in_ul:
                        result_lines.append('</ul>')
                        in_ul = False
                    result_lines.append('<ol>')
                    in_ol = True
                result_lines.append(f'<li>{ol_match.group(2)}</li>')
            elif ul_match:
                if not in_ul:
                    if in_ol:
                        result_lines.append('</ol>')
                        in_ol = False
                    result_lines.append('<ul>')
                    in_ul = True
                result_lines.append(f'<li>{ul_match.group(1)}</li>')
            else:
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                # Convert section headers (ALL CAPS followed by colon)
                if re.match(r'^[A-Z][A-Z\s&]+:$', stripped):
                    result_lines.append(f'<h4>{stripped}</h4>')
                elif stripped:
                    result_lines.append(f'<p>{stripped}</p>')
                else:
                    result_lines.append('')

        # Close any open lists
        if in_ol:
            result_lines.append('</ol>')
        if in_ul:
            result_lines.append('</ul>')

        return '\n'.join(result_lines)

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting from text"""
        # Remove ** bold markers
        text = re.sub(r'\*\*', '', text)
        # Remove list markers at start of text
        text = re.sub(r'^\s*[\*\-]\s+', '', text)
        text = re.sub(r'^\s*\d+\.\s+', '', text)
        # Remove remaining isolated asterisks
        text = re.sub(r'\s\*\s', ' ', text)
        # Remove disclaimer mentions
        text = re.sub(r'DISCLAIMER:.*$', '', text, flags=re.IGNORECASE)
        return text.strip()

    def extract_news_sentiment(self, analysis: str) -> Tuple[str, str]:
        """Extract sentiment and brief summary from news analysis"""
        sentiment = "Neutral"
        summary = ""

        lines = analysis.split('\n')
        for i, line in enumerate(lines):
            if 'SENTIMENT:' in line.upper():
                sentiment = self._clean_text(line.split(':')[-1])
            elif 'SUMMARY:' in line.upper():
                # Get the next non-empty lines as summary
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and not any(x in lines[j].upper() for x in ['SENTIMENT:', 'KEY ', 'MAJOR ', 'IMPACT ']):
                        summary_lines.append(lines[j].strip())
                summary = self._clean_text(' '.join(summary_lines))[:200]
                break

        if not summary:
            # Try to get first meaningful paragraph
            for line in lines:
                if len(line.strip()) > 50 and not any(x in line.upper() for x in ['SENTIMENT:', 'KEY ', '**']):
                    summary = self._clean_text(line.strip())[:200]
                    break

        return sentiment, summary

    def extract_statistical_outlook(self, analysis: str) -> Tuple[str, str]:
        """Extract trend direction and brief summary from statistical analysis"""
        trend = "Neutral"
        summary = ""

        lines = analysis.split('\n')
        for i, line in enumerate(lines):
            upper_line = line.upper()
            if 'TREND' in upper_line and ':' in line:
                content = line.split(':')[-1].strip().lower()
                if 'upward' in content or 'bullish' in content or 'positive' in content:
                    trend = "Bullish"
                elif 'downward' in content or 'bearish' in content or 'negative' in content:
                    trend = "Bearish"
                else:
                    trend = "Neutral"
            elif 'STATISTICAL INSIGHTS:' in upper_line or 'SUMMARY:' in upper_line:
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                summary = self._clean_text(' '.join(summary_lines))[:200]
                break

        return trend, summary

    def extract_financial_outlook(self, analysis: str) -> Tuple[str, str]:
        """Extract valuation assessment and brief summary from financial analysis"""
        valuation = "Fair"
        summary = ""

        lines = analysis.split('\n')
        for i, line in enumerate(lines):
            upper_line = line.upper()
            if 'VALUATION' in upper_line and ':' in line:
                content = line.split(':')[-1].strip().lower()
                if 'undervalued' in content or 'attractive' in content:
                    valuation = "Undervalued"
                elif 'overvalued' in content or 'expensive' in content:
                    valuation = "Overvalued"
                else:
                    valuation = "Fair"
            elif 'INVESTMENT THESIS:' in upper_line or 'SUMMARY:' in upper_line:
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                summary = self._clean_text(' '.join(summary_lines))[:200]
                break

        return valuation, summary

    def generate_sparkline_svg(self, prices: List[float], width: int = 80, height: int = 30) -> str:
        """Generate an inline SVG sparkline chart"""
        if not prices or len(prices) < 2:
            return ""

        # Use last 14 days of data
        prices = prices[-14:]

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1

        # Normalize prices to SVG coordinates
        points = []
        for i, price in enumerate(prices):
            x = (i / (len(prices) - 1)) * width
            y = height - ((price - min_price) / price_range) * height
            points.append(f"{x:.1f},{y:.1f}")

        # Determine color based on trend
        color = "#10b981" if prices[-1] >= prices[0] else "#ef4444"

        path_data = "M" + " L".join(points)

        return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="vertical-align: middle;">
            <path d="{path_data}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

    def generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate a concise executive summary section"""
        news_analysis = data['agents']['news_analyst']['analysis']
        stats_analysis = data['agents']['statistical_expert']['analysis']
        financial_analysis = data['agents']['financial_expert']['analysis']
        synthesis = data['agents']['investment_synthesizer']['synthesis']

        news_sentiment, news_summary = self.extract_news_sentiment(news_analysis)
        stat_trend, stat_summary = self.extract_statistical_outlook(stats_analysis)
        fin_outlook, fin_summary = self.extract_financial_outlook(financial_analysis)
        recommendation, confidence = self.extract_recommendation(synthesis)

        # Extract key points from synthesis
        synthesis_summary = ""
        lines = synthesis.split('\n')
        for i, line in enumerate(lines):
            if 'SUMMARY:' in line.upper():
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                synthesis_summary = ' '.join(summary_lines)
                break

        if not synthesis_summary:
            synthesis_summary = f"Based on comprehensive analysis, the recommendation is {recommendation} with {confidence} confidence."
        else:
            # Clean any remaining markdown from synthesis summary
            synthesis_summary = self._clean_text(synthesis_summary)

        return f'''
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-item news">
                    <div class="summary-header">
                        <span class="summary-icon">📰</span>
                        <span class="summary-title">News Sentiment</span>
                        <span class="summary-badge" style="background: {self._get_sentiment_color(news_sentiment)};">{news_sentiment}</span>
                    </div>
                    <p class="summary-text">{news_summary if news_summary else "Recent news coverage has been analyzed for market impact."}</p>
                </div>
                <div class="summary-item stats">
                    <div class="summary-header">
                        <span class="summary-icon">📊</span>
                        <span class="summary-title">Technical Analysis</span>
                        <span class="summary-badge" style="background: {self._get_sentiment_color(stat_trend)};">{stat_trend}</span>
                    </div>
                    <p class="summary-text">{stat_summary if stat_summary else "Statistical indicators have been evaluated for trend signals."}</p>
                </div>
                <div class="summary-item financial">
                    <div class="summary-header">
                        <span class="summary-icon">💰</span>
                        <span class="summary-title">Fundamental Analysis</span>
                        <span class="summary-badge" style="background: {self._get_valuation_color(fin_outlook)};">{fin_outlook}</span>
                    </div>
                    <p class="summary-text">{fin_summary if fin_summary else "Financial metrics and valuation have been assessed."}</p>
                </div>
            </div>
            <div class="summary-conclusion">
                <strong>Conclusion:</strong> {synthesis_summary}
            </div>
        </div>
        '''

    def _get_sentiment_color(self, sentiment: str) -> str:
        """Get color for sentiment badge"""
        s = sentiment.lower()
        if 'bullish' in s or 'positive' in s:
            return "#10b981"
        elif 'bearish' in s or 'negative' in s:
            return "#ef4444"
        return "#f59e0b"

    def _get_valuation_color(self, valuation: str) -> str:
        """Get color for valuation badge"""
        v = valuation.lower()
        if 'undervalued' in v:
            return "#10b981"
        elif 'overvalued' in v:
            return "#ef4444"
        return "#f59e0b"

    def _get_badge_class(self, sentiment: str) -> str:
        """Get CSS class for sentiment badge"""
        s = sentiment.lower()
        if 'bullish' in s or 'positive' in s:
            return "badge-bullish"
        elif 'bearish' in s or 'negative' in s:
            return "badge-bearish"
        return "badge-neutral"

    def _get_valuation_badge_class(self, valuation: str) -> str:
        """Get CSS class for valuation badge"""
        v = valuation.lower()
        if 'undervalued' in v:
            return "badge-undervalued"
        elif 'overvalued' in v:
            return "badge-overvalued"
        return "badge-fair"
    
    def get_latest_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get the most recent analysis file for a symbol"""
        pattern = f"{self.output_dir}/{symbol}_analysis_*.json"
        files = glob(pattern)
        
        if not files:
            return None
        
        # Get most recent file
        latest_file = max(files, key=os.path.getctime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def extract_recommendation(self, synthesis: str) -> tuple:
        """Extract recommendation and confidence from synthesis"""
        lines = synthesis.split('\n')
        recommendation = "HOLD"
        confidence = "Medium"
        
        for line in lines:
            if line.startswith("RECOMMENDATION:"):
                recommendation = line.split(":")[-1].strip()
            elif line.startswith("CONFIDENCE LEVEL:"):
                confidence = line.split(":")[-1].strip()
        
        return recommendation, confidence
    
    def get_recommendation_color(self, recommendation: str) -> str:
        """Get color for recommendation badge"""
        rec = recommendation.upper()
        if "BUY" in rec:
            return "#10b981"  # Green
        elif "SELL" in rec:
            return "#ef4444"  # Red
        else:
            return "#f59e0b"  # Orange
    
    def generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report from analysis data"""
        
        symbol = data['symbol']
        company_name = data['company_name']
        analysis_date = datetime.fromisoformat(data['analysis_date']).strftime("%B %d, %Y at %I:%M %p")
        
        # Extract analyses
        news_analysis = data['agents']['news_analyst']['analysis']
        stats_analysis = data['agents']['statistical_expert']['analysis']
        financial_analysis = data['agents']['financial_expert']['analysis']
        synthesis = data['agents']['investment_synthesizer']['synthesis']

        # Extract forecast data if available
        forecast_data = data['agents'].get('forecaster', {})
        forecast_summary = forecast_data.get('summary', {})
        forecast_charts = forecast_data.get('charts', {})
        
        # Get recommendation
        recommendation, confidence = self.extract_recommendation(synthesis)
        rec_color = self.get_recommendation_color(recommendation)
        
        # Get stock metrics
        stock_data = data['stock_data']
        current_price = stock_data.get('current_price', 0)
        day_change = stock_data.get('day_change', 0)
        day_change_pct = stock_data.get('day_change_percent', 0)
        market_cap = stock_data.get('market_cap', 0)
        
        # Format market cap
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            else:
                market_cap_str = f"${market_cap/1e6:.2f}M"
        else:
            market_cap_str = "N/A"
        
        change_color = "#10b981" if day_change >= 0 else "#ef4444"
        change_symbol = "▲" if day_change >= 0 else "▼"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} Stock Analysis - {company_name}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1f2937;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .stock-title {{
            font-size: 2.5em;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 10px;
        }}
        
        .stock-symbol {{
            font-size: 1.2em;
            color: #6b7280;
            margin-bottom: 20px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .metric {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #6b7280;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: 700;
            color: #1f2937;
        }}
        
        .recommendation {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .rec-badge {{
            display: inline-block;
            background: {rec_color};
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 2em;
            font-weight: 700;
            margin: 20px 0;
        }}
        
        .confidence {{
            font-size: 1.2em;
            color: #6b7280;
            margin-top: 10px;
        }}
        
        .agent-section {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .agent-title {{
            font-size: 1.8em;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .agent-icon {{
            font-size: 1.2em;
        }}
        
        .agent-content {{
            white-space: pre-wrap;
            line-height: 1.8;
            color: #374151;
            font-size: 1.05em;
        }}
        
        .timestamp {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .disclaimer {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            border-radius: 12px;
            margin-top: 30px;
            color: #92400e;
        }}

        .executive-summary {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .executive-summary h2 {{
            font-size: 1.8em;
            color: #1f2937;
            margin-bottom: 25px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}

        .summary-item {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}

        .summary-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}

        .summary-icon {{
            font-size: 1.3em;
        }}

        .summary-title {{
            font-weight: 600;
            color: #1f2937;
            flex-grow: 1;
        }}

        .summary-badge {{
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .summary-text {{
            color: #4b5563;
            line-height: 1.6;
            font-size: 0.95em;
        }}

        .summary-conclusion {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            line-height: 1.7;
        }}

        .summary-conclusion strong {{
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}

        .agent-content h4 {{
            color: #667eea;
            margin: 20px 0 10px 0;
            font-size: 1.1em;
        }}

        .agent-content p {{
            margin: 8px 0;
            line-height: 1.7;
        }}

        .agent-content ol, .agent-content ul {{
            margin: 10px 0 10px 25px;
            line-height: 1.8;
        }}

        .agent-content li {{
            margin: 5px 0;
        }}

        .forecast-chart {{
            width: 100%;
            min-height: 400px;
            margin-top: 20px;
        }}

        .forecast-chart .plotly-graph-div {{
            width: 100% !important;
        }}
        
        @media (max-width: 768px) {{
            .stock-title {{
                font-size: 2em;
            }}
            .metrics {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="stock-title">{company_name}</div>
            <div class="stock-symbol">{symbol}</div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">${current_price:.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Day Change</div>
                    <div class="metric-value" style="color: {change_color};">
                        {change_symbol} ${abs(day_change):.2f} ({abs(day_change_pct):.2f}%)
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">{market_cap_str}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Analysis Date</div>
                    <div class="metric-value" style="font-size: 1.2em;">{analysis_date}</div>
                </div>
            </div>
        </div>
        
        <!-- Recommendation -->
        <div class="recommendation">
            <h2>Investment Recommendation</h2>
            <div class="rec-badge">{recommendation}</div>
            <div class="confidence">Confidence: {confidence}</div>
        </div>

        <!-- Executive Summary -->
        {self.generate_executive_summary(data)}

        <!-- Price Forecast -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">🔮</span>
                Price Forecast (10-Day)
            </div>
            <div class="forecast-metrics" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="metric" style="border-left-color: #10b981;">
                    <div class="metric-label">Next Day Prediction</div>
                    <div class="metric-value" style="color: #10b981;">${forecast_summary.get('next_day_prediction', current_price):.2f}</div>
                    <div style="font-size: 0.9em; color: #6b7280;">{forecast_summary.get('next_day_expected_return', 'N/A')}</div>
                </div>
                <div class="metric" style="border-left-color: #667eea;">
                    <div class="metric-label">10-Day Prediction</div>
                    <div class="metric-value" style="color: #667eea;">${forecast_summary.get('day_10_prediction', current_price):.2f}</div>
                    <div style="font-size: 0.9em; color: #6b7280;">{forecast_summary.get('day_10_expected_return', 'N/A')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Forecast Confidence</div>
                    <div class="metric-value" style="font-size: 1.4em;">{forecast_summary.get('confidence', 'N/A')}</div>
                    <div style="font-size: 0.9em; color: #6b7280;">Models: {', '.join(forecast_summary.get('models_used', ['N/A']))}</div>
                </div>
            </div>
            <div class="forecast-chart">
                {forecast_charts.get('1y', '<p>Chart not available</p>')}
            </div>
        </div>

        <!-- Investment Synthesis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">🎯</span>
                Investment Synthesis
            </div>
            <div class="agent-content">{self.markdown_to_html(synthesis)}</div>
        </div>

        <!-- News Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">🗞️</span>
                News Analysis
            </div>
            <div class="agent-content">{self.markdown_to_html(news_analysis)}</div>
        </div>

        <!-- Statistical Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">📈</span>
                Statistical Analysis
            </div>
            <div class="agent-content">{self.markdown_to_html(stats_analysis)}</div>
        </div>

        <!-- Financial Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">💼</span>
                Financial Analysis
            </div>
            <div class="agent-content">{self.markdown_to_html(financial_analysis)}</div>
        </div>
        
        <!-- Disclaimer -->
        <div class="disclaimer">
            <strong>⚠️ Important Disclaimer:</strong><br>
            This analysis is generated by AI agents for educational purposes only. It should NOT be considered 
            financial advice. Stock markets are inherently risky and unpredictable. Always conduct your own 
            thorough research and consult with a qualified financial advisor before making any investment decisions. 
            Past performance does not guarantee future results.
        </div>
        
        <div class="timestamp">
            Generated by Stock Investment Planner on {analysis_date}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_index(self, symbols: list):
        """Generate index.html with links to all stock reports"""

        reports = []
        for symbol in symbols:
            data = self.get_latest_analysis(symbol)
            if data:
                stock_data = data.get('stock_data', {})
                current_price = stock_data.get('current_price', 0)

                # Get historical prices for sparkline
                hist_prices = stock_data.get('historical_prices', {})
                prices = list(hist_prices.values()) if hist_prices else []
                sparkline = self.generate_sparkline_svg(prices)

                # Get forecast prediction
                forecast_data = data['agents'].get('forecaster', {})
                forecast_summary = forecast_data.get('summary', {})
                prediction = forecast_summary.get('day_10_prediction', current_price)

                # Get per-agent recommendations
                news_analysis = data['agents']['news_analyst']['analysis']
                stats_analysis = data['agents']['statistical_expert']['analysis']
                financial_analysis = data['agents']['financial_expert']['analysis']
                synthesis = data['agents']['investment_synthesizer']['synthesis']

                news_sentiment, _ = self.extract_news_sentiment(news_analysis)
                stat_trend, _ = self.extract_statistical_outlook(stats_analysis)
                fin_outlook, _ = self.extract_financial_outlook(financial_analysis)
                recommendation, confidence = self.extract_recommendation(synthesis)

                reports.append({
                    'symbol': symbol,
                    'company': data['company_name'],
                    'date': datetime.fromisoformat(data['analysis_date']).strftime("%Y-%m-%d"),
                    'file': f"{symbol.lower()}.html",
                    'price': current_price,
                    'sparkline': sparkline,
                    'prediction': prediction,
                    'news_sentiment': news_sentiment,
                    'stat_trend': stat_trend,
                    'fin_outlook': fin_outlook,
                    'recommendation': recommendation,
                    'rec_color': self.get_recommendation_color(recommendation)
                })
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Investment Planner - AI-Powered Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .hero {
            background: white;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 40px;
        }

        h1 {
            font-size: 2.5em;
            color: #1f2937;
            margin-bottom: 15px;
        }

        .subtitle {
            font-size: 1.2em;
            color: #6b7280;
        }

        .stock-table-container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow-x: auto;
        }

        .stock-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }

        .stock-table th {
            background: #f9fafb;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }

        .stock-table td {
            padding: 18px 12px;
            border-bottom: 1px solid #f3f4f6;
            vertical-align: middle;
        }

        .stock-table tr:hover {
            background: #f9fafb;
        }

        .symbol-cell {
            font-weight: 700;
            font-size: 1.1em;
            color: #1f2937;
        }

        .company-name {
            font-size: 0.85em;
            color: #6b7280;
            margin-top: 3px;
        }

        .price-cell {
            font-weight: 600;
            color: #1f2937;
        }

        .prediction-cell {
            color: #667eea;
            font-weight: 500;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            color: white;
        }

        .badge-bullish { background: #10b981; }
        .badge-bearish { background: #ef4444; }
        .badge-neutral { background: #f59e0b; }
        .badge-undervalued { background: #10b981; }
        .badge-overvalued { background: #ef4444; }
        .badge-fair { background: #f59e0b; }

        .rec-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            color: white;
            font-size: 0.9em;
        }

        .view-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }

        .view-link:hover {
            color: #5568d3;
            text-decoration: underline;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.9;
        }

        .legend {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.85em;
            color: #6b7280;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        @media (max-width: 1024px) {
            .stock-table {
                font-size: 0.85em;
            }
            .stock-table th, .stock-table td {
                padding: 12px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>Stock Investment Planner</h1>
            <p class="subtitle">AI-Powered Multi-Agent Stock Analysis</p>
        </div>

        <div class="stock-table-container">
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Trend</th>
                        <th>10-Day Prediction</th>
                        <th>News</th>
                        <th>Technical</th>
                        <th>Fundamental</th>
                        <th>Recommendation</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""

        for report in reports:
            news_badge_class = self._get_badge_class(report['news_sentiment'])
            stat_badge_class = self._get_badge_class(report['stat_trend'])
            fin_badge_class = self._get_valuation_badge_class(report['fin_outlook'])

            html += f"""
                    <tr>
                        <td>
                            <div class="symbol-cell">{report['symbol']}</div>
                            <div class="company-name">{report['company']}</div>
                        </td>
                        <td class="price-cell">${report['price']:.2f}</td>
                        <td>{report['sparkline']}</td>
                        <td class="prediction-cell">${report['prediction']:.2f}</td>
                        <td><span class="badge {news_badge_class}">{report['news_sentiment']}</span></td>
                        <td><span class="badge {stat_badge_class}">{report['stat_trend']}</span></td>
                        <td><span class="badge {fin_badge_class}">{report['fin_outlook']}</span></td>
                        <td><span class="rec-badge" style="background: {report['rec_color']};">{report['recommendation']}</span></td>
                        <td><a href="{report['file']}" class="view-link">View →</a></td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
            <div class="legend">
                <div class="legend-item"><div class="legend-dot" style="background: #10b981;"></div> Bullish / Buy</div>
                <div class="legend-item"><div class="legend-dot" style="background: #f59e0b;"></div> Neutral / Hold</div>
                <div class="legend-item"><div class="legend-dot" style="background: #ef4444;"></div> Bearish / Sell</div>
            </div>
        </div>

        <div class="footer">
            <p>Powered by Ollama AI Agents | For Educational Purposes Only</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Not Financial Advice</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_all_reports(self, symbols: list):
        """Generate HTML reports for all stocks"""
        os.makedirs(self.web_dir, exist_ok=True)
        
        print("\n📝 Generating HTML reports...\n")
        
        for symbol in symbols:
            data = self.get_latest_analysis(symbol)
            if data:
                html = self.generate_html(data)
                filename = f"{self.web_dir}/{symbol.lower()}.html"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print(f"✅ Generated: {filename}")
        
        # Generate index
        index_html = self.generate_index(symbols)
        index_file = f"{self.web_dir}/index.html"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"✅ Generated: {index_file}")
        print(f"\n🎉 All reports generated in '{self.web_dir}' directory!")
        print(f"\n💡 Next steps:")
        print(f"1. Push the '{self.web_dir}' directory to GitHub")
        print(f"2. Enable GitHub Pages in your repo settings (use /docs folder)")
        print(f"3. Your site will be live at: https://YOUR_USERNAME.github.io/YOUR_REPO/")


if __name__ == "__main__":
    from config import STOCK_SYMBOLS
    
    generator = HTMLReportGenerator()
    generator.generate_all_reports(STOCK_SYMBOLS)
