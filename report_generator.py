"""
HTML Report Generator
Creates beautiful static HTML reports for GitHub Pages
"""

from jinja2 import Template
from datetime import datetime
import json
import os
from typing import Dict, List


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Investment Analysis - {{ ticker }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.2em;
        }
        
        .price-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
        }
        
        .price-box .price {
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .price-box .label {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .card h3 {
            color: #555;
            margin: 20px 0 10px 0;
            font-size: 1.3em;
        }
        
        .card p {
            color: #666;
            line-height: 1.8;
            margin-bottom: 15px;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin: 30px 0;
            font-size: 1.1em;
            line-height: 1.8;
        }
        
        .recommendation h2 {
            color: white;
            border-bottom: 3px solid white;
            margin-bottom: 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .stat-box .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .stat-box .stat-value {
            color: #333;
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .news-item {
            border-left: 3px solid #667eea;
            padding-left: 15px;
            margin: 15px 0;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .news-item h4 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .news-item .news-meta {
            color: #999;
            font-size: 0.9em;
        }
        
        .disclaimer {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
            color: #856404;
        }
        
        .disclaimer strong {
            display: block;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
        
        .agent-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .price-box .price {
                font-size: 2em;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {{ company_name }}</h1>
            <div class="subtitle">Stock Ticker: {{ ticker }}</div>
            <div class="subtitle">Analysis Date: {{ analysis_date }}</div>
            
            <div class="price-box">
                <div class="label">Current Stock Price</div>
                <div class="price">${{ current_price }}</div>
            </div>
        </div>
        
        <div class="disclaimer">
            <strong>⚠️ Important Disclaimer</strong>
            This analysis is generated by AI agents for educational and informational purposes only. 
            This is NOT professional financial advice. Always consult with a qualified financial advisor 
            before making investment decisions. Past performance does not guarantee future results.
        </div>
        
        <div class="card">
            <h2>📈 Key Statistics & Predictions</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Prediction Method</div>
                    <div class="stat-value">{{ predictions.method }}</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">30-Day Forecast</div>
                    <div class="stat-value">{{ predictions.forecast_summary }}</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">Trend Direction</div>
                    <div class="stat-value">{{ predictions.trend }}</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">Confidence Level</div>
                    <div class="stat-value">{{ predictions.confidence }}</div>
                </div>
            </div>
            
            {% if company_info %}
            <h3>Company Information</h3>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Sector</div>
                    <div class="stat-value" style="font-size: 1.2em;">{{ company_info.sector }}</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">Market Cap</div>
                    <div class="stat-value" style="font-size: 1.2em;">${{ (company_info.market_cap / 1000000000) | round(2) }}B</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">P/E Ratio</div>
                    <div class="stat-value" style="font-size: 1.2em;">{{ company_info.pe_ratio | round(2) }}</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-label">52-Week Range</div>
                    <div class="stat-value" style="font-size: 1em;">${{ company_info['52_week_low'] | round(2) }} - ${{ company_info['52_week_high'] | round(2) }}</div>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="card">
            <h2>📰 Recent News Headlines</h2>
            {% for article in latest_news %}
            <div class="news-item">
                <h4>{{ article.title }}</h4>
                <div class="news-meta">{{ article.source }} • {{ article.published }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="card">
            <span class="agent-badge">🤖 Agent 1: News Analyst</span>
            <h2>News Sentiment Analysis</h2>
            <p>{{ agent_analyses.news_analysis | safe }}</p>
        </div>
        
        <div class="card">
            <span class="agent-badge">🤖 Agent 2: Statistical Analyst</span>
            <h2>Statistical & Technical Analysis</h2>
            <p>{{ agent_analyses.statistical_analysis | safe }}</p>
        </div>
        
        <div class="card">
            <span class="agent-badge">🤖 Agent 3: Financial Expert</span>
            <h2>Fundamental Analysis</h2>
            <p>{{ agent_analyses.fundamental_analysis | safe }}</p>
        </div>
        
        <div class="recommendation">
            <span class="agent-badge" style="background: white; color: #667eea;">🤖 Agent 4: Investment Synthesizer</span>
            <h2>Final Investment Recommendation</h2>
            <div style="white-space: pre-wrap;">{{ agent_analyses.final_recommendation }}</div>
        </div>
        
        <div class="footer">
            <p>Generated by AI-Powered Stock Investment Planner</p>
            <p>Powered by Ollama Local AI | Data from Yahoo Finance & Google News</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Last updated: {{ analysis_date }}</p>
        </div>
    </div>
</body>
</html>
"""


class HTMLReportGenerator:
    """Generate beautiful HTML reports from analysis results"""
    
    def __init__(self):
        self.template = Template(HTML_TEMPLATE)
    
    def generate_report(self, analysis_results: Dict, output_path: str):
        """
        Generate HTML report from analysis results
        """
        try:
            # Format the data for the template
            data = {
                "ticker": analysis_results.get("ticker", "N/A"),
                "company_name": analysis_results.get("company_name", "Unknown Company"),
                "current_price": f"{analysis_results.get('current_price', 0):.2f}",
                "analysis_date": datetime.fromisoformat(
                    analysis_results.get("timestamp", datetime.now().isoformat())
                ).strftime("%B %d, %Y at %I:%M %p"),
                "predictions": analysis_results.get("data", {}).get("predictions", {}),
                "company_info": analysis_results.get("data", {}).get("company_info", {}),
                "latest_news": analysis_results.get("data", {}).get("latest_news", []),
                "agent_analyses": analysis_results.get("agent_analyses", {})
            }
            
            # Format text with line breaks
            for key in data["agent_analyses"]:
                if data["agent_analyses"][key]:
                    data["agent_analyses"][key] = data["agent_analyses"][key].replace('\n', '<br>')
            
            # Render HTML
            html_content = self.template.render(**data)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ Generated HTML report: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Error generating HTML report: {str(e)}")
            raise
    
    def generate_index_page(self, all_analyses: List[Dict], output_path: str):
        """
        Generate an index page listing all stock analyses
        """
        index_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Investment Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .stock-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .stock-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .stock-card h2 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .stock-card .ticker {
            color: #667eea;
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .stock-card .price {
            font-size: 1.8em;
            color: #333;
            margin: 10px 0;
        }
        
        .stock-card .date {
            color: #999;
            font-size: 0.9em;
        }
        
        .stock-card a {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: opacity 0.3s;
        }
        
        .stock-card a:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Stock Investment Dashboard</h1>
            <p style="color: #666; font-size: 1.2em;">AI-Powered Multi-Agent Analysis</p>
            <p style="color: #999; margin-top: 10px;">Last Updated: {{ update_date }}</p>
        </div>
        
        <div class="stock-grid">
            {% for stock in stocks %}
            <div class="stock-card">
                <div class="ticker">{{ stock.ticker }}</div>
                <h2>{{ stock.company_name }}</h2>
                <div class="price">${{ stock.current_price }}</div>
                <div class="date">Analyzed: {{ stock.analysis_date }}</div>
                <a href="{{ stock.report_file }}">View Full Analysis →</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
        
        # Prepare stock data
        stocks = []
        for analysis in all_analyses:
            if "error" not in analysis:
                stocks.append({
                    "ticker": analysis.get("ticker", "N/A"),
                    "company_name": analysis.get("company_name", "Unknown"),
                    "current_price": f"{analysis.get('current_price', 0):.2f}",
                    "analysis_date": datetime.fromisoformat(
                        analysis.get("timestamp", datetime.now().isoformat())
                    ).strftime("%b %d, %Y"),
                    "report_file": f"{analysis.get('ticker', 'stock')}_report.html"
                })
        
        template = Template(index_template)
        html_content = template.render(
            stocks=stocks,
            update_date=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Generated index page: {output_path}")


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "ticker": "GOOGL",
        "company_name": "Alphabet Inc. (Google)",
        "timestamp": datetime.now().isoformat(),
        "current_price": 142.50,
        "data": {
            "predictions": {
                "method": "Prophet",
                "forecast_summary": "$145.20 in 30 days (+1.9%)",
                "trend": "UPWARD",
                "confidence": "Medium-High"
            },
            "company_info": {
                "sector": "Technology",
                "market_cap": 1800000000000,
                "pe_ratio": 28.5,
                "52_week_high": 150.0,
                "52_week_low": 120.0
            },
            "latest_news": [
                {"title": "Google announces new AI", "source": "TechCrunch", "published": "2024-01-15"}
            ]
        },
        "agent_analyses": {
            "news_analysis": "Positive sentiment overall...",
            "statistical_analysis": "Upward trend detected...",
            "fundamental_analysis": "Strong fundamentals...",
            "final_recommendation": "BUY - Strong opportunity..."
        }
    }
    
    generator = HTMLReportGenerator()
    generator.generate_report(sample_data, "test_report.html")
    print("✓ Test report generated!")
