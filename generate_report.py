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
from datetime import datetime
from glob import glob
from typing import Dict, Any


class HTMLReportGenerator:
    """Generates HTML reports from analysis results"""
    
    def __init__(self):
        self.output_dir = "reports"  # Where JSON analysis files are saved
        self.web_dir = "docs"  # GitHub Pages serves from /docs
    
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
            <div class="agent-content">{synthesis}</div>
        </div>
        
        <!-- News Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">🗞️</span>
                News Analysis
            </div>
            <div class="agent-content">{news_analysis}</div>
        </div>
        
        <!-- Statistical Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">📈</span>
                Statistical Analysis
            </div>
            <div class="agent-content">{stats_analysis}</div>
        </div>
        
        <!-- Financial Analysis -->
        <div class="agent-section">
            <div class="agent-title">
                <span class="agent-icon">💼</span>
                Financial Analysis
            </div>
            <div class="agent-content">{financial_analysis}</div>
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
                reports.append({
                    'symbol': symbol,
                    'company': data['company_name'],
                    'date': datetime.fromisoformat(data['analysis_date']).strftime("%Y-%m-%d"),
                    'file': f"{symbol.lower()}.html"
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
            max-width: 800px;
            margin: 0 auto;
        }
        
        .hero {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 3em;
            color: #1f2937;
            margin-bottom: 20px;
        }
        
        .subtitle {
            font-size: 1.3em;
            color: #6b7280;
            margin-bottom: 30px;
        }
        
        .stock-list {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .stock-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px;
            border-bottom: 2px solid #f3f4f6;
            transition: all 0.3s;
        }
        
        .stock-item:last-child {
            border-bottom: none;
        }
        
        .stock-item:hover {
            background: #f9fafb;
            transform: translateX(10px);
        }
        
        .stock-info {
            flex: 1;
        }
        
        .stock-symbol {
            font-size: 1.5em;
            font-weight: 700;
            color: #1f2937;
        }
        
        .stock-name {
            color: #6b7280;
            margin-top: 5px;
        }
        
        .stock-date {
            color: #9ca3af;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .view-btn {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .view-btn:hover {
            background: #5568d3;
            transform: scale(1.05);
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>📊 Stock Investment Planner</h1>
            <p class="subtitle">AI-Powered Multi-Agent Stock Analysis</p>
            <p style="color: #6b7280;">Combining News Analysis, Statistical Modeling, and Financial Expertise</p>
        </div>
        
        <div class="stock-list">
"""
        
        for report in reports:
            html += f"""
            <div class="stock-item">
                <div class="stock-info">
                    <div class="stock-symbol">{report['symbol']}</div>
                    <div class="stock-name">{report['company']}</div>
                    <div class="stock-date">Latest Analysis: {report['date']}</div>
                </div>
                <a href="{report['file']}" class="view-btn">View Analysis →</a>
            </div>
"""
        
        html += """
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
