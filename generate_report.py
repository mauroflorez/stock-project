"""
HTML Report Generator
Converts JSON analysis results into beautiful HTML reports for GitHub Pages
Modern glassmorphism design with animations and dark mode support
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
    """Generates HTML reports from analysis results with modern styling"""

    # Modern color palette
    COLORS = {
        'primary': '#6366f1',      # Indigo
        'primary_dark': '#4f46e5',
        'success': '#10b981',       # Emerald
        'warning': '#f59e0b',       # Amber
        'danger': '#ef4444',        # Red
        'dark': '#0f172a',          # Slate 900
        'dark_card': '#1e293b',     # Slate 800
        'dark_border': '#334155',   # Slate 700
        'light': '#f8fafc',         # Slate 50
        'light_card': '#ffffff',
        'text_dark': '#1e293b',
        'text_light': '#f1f5f9',
        'text_muted': '#64748b',
    }

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

    def generate_sparkline_svg(self, prices: List[float], width: int = 100, height: int = 40) -> str:
        """Generate an inline SVG sparkline chart with gradient fill"""
        if not prices or len(prices) < 2:
            return ""

        # Use last 20 days of data for smoother chart
        prices = prices[-20:]

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1

        # Add padding to prevent clipping
        padding = 4
        chart_width = width - (padding * 2)
        chart_height = height - (padding * 2)

        # Normalize prices to SVG coordinates
        points = []
        for i, price in enumerate(prices):
            x = padding + (i / (len(prices) - 1)) * chart_width
            y = padding + chart_height - ((price - min_price) / price_range) * chart_height
            points.append(f"{x:.1f},{y:.1f}")

        # Determine color based on trend
        is_positive = prices[-1] >= prices[0]
        color = "#10b981" if is_positive else "#ef4444"
        color_light = "#34d399" if is_positive else "#f87171"

        path_data = "M" + " L".join(points)

        # Create area fill path (closes to bottom)
        first_point = points[0]
        last_point = points[-1]
        area_path = f"M{first_point} L" + " L".join(points[1:]) + f" L{last_point.split(',')[0]},{height - padding} L{padding},{height - padding} Z"

        # Unique ID for gradient
        grad_id = f"grad_{hash(tuple(prices)) % 10000}"

        return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="vertical-align: middle;">
            <defs>
                <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{color};stop-opacity:0.3"/>
                    <stop offset="100%" style="stop-color:{color};stop-opacity:0"/>
                </linearGradient>
            </defs>
            <path d="{area_path}" fill="url(#{grad_id})"/>
            <path d="{path_data}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="{points[-1].split(',')[0]}" cy="{points[-1].split(',')[1]}" r="3" fill="{color}"/>
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
    
    def get_common_css(self, is_detail_page: bool = False) -> str:
        """Generate common CSS styles for all pages"""
        return """
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #818cf8;
            --success: #10b981;
            --success-light: #34d399;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-dark: #0f172a;
            --bg-card-dark: #1e293b;
            --bg-card-dark-hover: #273449;
            --border-dark: #334155;
            --bg-light: #f1f5f9;
            --bg-card-light: #ffffff;
            --text-dark: #1e293b;
            --text-light: #f1f5f9;
            --text-muted: #64748b;
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            --shadow-lg: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            background-attachment: fixed;
            min-height: 100vh;
            color: var(--text-light);
            line-height: 1.6;
        }

        /* Animated background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(59, 130, 246, 0.05) 0%, transparent 70%);
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }

        /* Glass card effect */
        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 24px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: var(--shadow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(99, 102, 241, 0.4);
        }

        /* Navigation */
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            margin-bottom: 24px;
        }

        .nav-brand {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-light), var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
        }

        .nav-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 12px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }

        .nav-link:hover {
            color: var(--text-light);
            background: rgba(99, 102, 241, 0.2);
            border-color: var(--primary);
        }

        /* Typography */
        h1, h2, h3 {
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        h1 { font-size: 2.5rem; margin-bottom: 8px; }
        h2 { font-size: 1.5rem; margin-bottom: 16px; color: var(--text-light); }
        h3 { font-size: 1.125rem; color: var(--text-muted); }

        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .badge-success { background: rgba(16, 185, 129, 0.2); color: var(--success-light); border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-primary { background: rgba(99, 102, 241, 0.2); color: var(--primary-light); border: 1px solid rgba(99, 102, 241, 0.3); }

        .badge-bullish, .badge-undervalued { background: rgba(16, 185, 129, 0.2); color: var(--success-light); border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-bearish, .badge-overvalued { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-neutral, .badge-fair { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

        /* Recommendation badge - large */
        .rec-badge-large {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 16px 48px;
            border-radius: 16px;
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            box-shadow: 0 10px 40px -10px currentColor;
        }

        .rec-buy { background: linear-gradient(135deg, #10b981, #059669); color: white; }
        .rec-sell { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }
        .rec-hold { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }

        /* Metrics grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
        }

        .metric-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-dark);
            border-radius: 16px;
            padding: 20px;
            transition: all 0.2s ease;
        }

        .metric-card:hover {
            background: rgba(15, 23, 42, 0.8);
            border-color: var(--primary);
        }

        .metric-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-light);
        }

        .metric-value.positive { color: var(--success); }
        .metric-value.negative { color: var(--danger); }
        .metric-value.primary { color: var(--primary-light); }

        .metric-sub {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* Collapsible sections */
        .collapsible {
            cursor: pointer;
        }

        .collapsible-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 0;
            border-bottom: 1px solid var(--border-dark);
        }

        .collapsible-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.25rem;
            font-weight: 600;
        }

        .collapsible-icon {
            font-size: 1.5rem;
        }

        .collapsible-toggle {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 8px;
            color: var(--primary-light);
            transition: all 0.2s ease;
        }

        .collapsible:hover .collapsible-toggle {
            background: rgba(99, 102, 241, 0.2);
        }

        .collapsible-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }

        .collapsible.open .collapsible-content {
            max-height: 5000px;
            transition: max-height 0.5s ease-in;
        }

        .collapsible.open .collapsible-toggle {
            transform: rotate(180deg);
        }

        .collapsible-body {
            padding: 24px 0;
            color: var(--text-muted);
            line-height: 1.8;
        }

        .collapsible-body h4 {
            color: var(--primary-light);
            margin: 24px 0 12px 0;
            font-size: 1rem;
            font-weight: 600;
        }

        .collapsible-body p {
            margin: 8px 0;
        }

        .collapsible-body ul, .collapsible-body ol {
            margin: 12px 0 12px 24px;
        }

        .collapsible-body li {
            margin: 6px 0;
        }

        /* Summary cards */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }

        .summary-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-dark);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.2s ease;
        }

        .summary-card:hover {
            border-color: var(--primary);
            background: rgba(15, 23, 42, 0.8);
        }

        .summary-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .summary-icon {
            font-size: 1.5rem;
        }

        .summary-title {
            flex: 1;
            font-weight: 600;
            color: var(--text-light);
        }

        .summary-text {
            color: var(--text-muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }

        /* Conclusion box */
        .conclusion-box {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin-top: 24px;
        }

        .conclusion-box strong {
            color: var(--primary-light);
            font-size: 1rem;
        }

        /* Disclaimer */
        .disclaimer {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 16px;
            padding: 20px 24px;
            color: #fbbf24;
            font-size: 0.9rem;
        }

        .disclaimer strong {
            display: block;
            margin-bottom: 8px;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 32px 0;
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* Chart container */
        .chart-container {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 16px;
            padding: 16px;
            margin-top: 24px;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-in {
            animation: fadeIn 0.5s ease-out forwards;
        }

        .delay-1 { animation-delay: 0.1s; opacity: 0; }
        .delay-2 { animation-delay: 0.2s; opacity: 0; }
        .delay-3 { animation-delay: 0.3s; opacity: 0; }
        .delay-4 { animation-delay: 0.4s; opacity: 0; }

        /* Responsive */
        @media (max-width: 768px) {
            .container { padding: 16px; }
            h1 { font-size: 1.75rem; }
            .card { padding: 24px; border-radius: 20px; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .metric-value { font-size: 1.5rem; }
            .rec-badge-large { padding: 12px 32px; font-size: 1.25rem; }
        }

        /* Plotly chart styling */
        .js-plotly-plot .plotly .modebar {
            background: transparent !important;
        }
        .js-plotly-plot .plotly .modebar-btn path {
            fill: var(--text-muted) !important;
        }
        """

    def generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report from analysis data with modern styling"""

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
        rec_class = "rec-buy" if "BUY" in recommendation.upper() else "rec-sell" if "SELL" in recommendation.upper() else "rec-hold"

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

        change_class = "positive" if day_change >= 0 else "negative"
        change_symbol = "+" if day_change >= 0 else ""

        # Extract summaries for executive summary
        news_sentiment, news_summary = self.extract_news_sentiment(news_analysis)
        stat_trend, stat_summary = self.extract_statistical_outlook(stats_analysis)
        fin_outlook, fin_summary = self.extract_financial_outlook(financial_analysis)

        news_badge_class = self._get_badge_class(news_sentiment)
        stat_badge_class = self._get_badge_class(stat_trend)
        fin_badge_class = self._get_valuation_badge_class(fin_outlook)

        # Get synthesis summary
        synthesis_summary = self._extract_synthesis_summary(synthesis, recommendation, confidence)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - {company_name} | Stock Analysis</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        {self.get_common_css(is_detail_page=True)}
    </style>
</head>
<body>
    <div class="container">
        <!-- Navigation -->
        <nav class="nav animate-in">
            <a href="index.html" class="nav-brand">Stock Planner</a>
            <a href="index.html" class="nav-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back to Dashboard
            </a>
        </nav>

        <!-- Header Card -->
        <div class="card animate-in delay-1">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 24px;">
                <div>
                    <h1>{company_name}</h1>
                    <h3>{symbol}</h3>
                </div>
                <div class="rec-badge-large {rec_class}">{recommendation}</div>
            </div>

            <div class="metrics-grid" style="margin-top: 32px;">
                <div class="metric-card">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">${current_price:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Day Change</div>
                    <div class="metric-value {change_class}">{change_symbol}${abs(day_change):.2f}</div>
                    <div class="metric-sub">{change_symbol}{abs(day_change_pct):.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">{market_cap_str}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Confidence</div>
                    <div class="metric-value primary">{confidence}</div>
                </div>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="card animate-in delay-2">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-header">
                        <span class="summary-icon">📰</span>
                        <span class="summary-title">News Sentiment</span>
                        <span class="badge {news_badge_class}">{news_sentiment}</span>
                    </div>
                    <p class="summary-text">{news_summary if news_summary else "Recent news coverage analyzed for market impact."}</p>
                </div>
                <div class="summary-card">
                    <div class="summary-header">
                        <span class="summary-icon">📊</span>
                        <span class="summary-title">Technical Analysis</span>
                        <span class="badge {stat_badge_class}">{stat_trend}</span>
                    </div>
                    <p class="summary-text">{stat_summary if stat_summary else "Statistical indicators evaluated for trend signals."}</p>
                </div>
                <div class="summary-card">
                    <div class="summary-header">
                        <span class="summary-icon">💰</span>
                        <span class="summary-title">Fundamental Analysis</span>
                        <span class="badge {fin_badge_class}">{fin_outlook}</span>
                    </div>
                    <p class="summary-text">{fin_summary if fin_summary else "Financial metrics and valuation assessed."}</p>
                </div>
            </div>
            <div class="conclusion-box">
                <strong>Conclusion</strong>
                <p style="margin-top: 8px; color: var(--text-muted);">{synthesis_summary}</p>
            </div>
        </div>

        <!-- Price Forecast -->
        <div class="card animate-in delay-3">
            <h2>Price Forecast (10-Day)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Next Day</div>
                    <div class="metric-value primary">${forecast_summary.get('next_day_prediction', current_price):.2f}</div>
                    <div class="metric-sub">{forecast_summary.get('next_day_expected_return', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">10-Day Target</div>
                    <div class="metric-value primary">${forecast_summary.get('day_10_prediction', current_price):.2f}</div>
                    <div class="metric-sub">{forecast_summary.get('day_10_expected_return', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Forecast Confidence</div>
                    <div class="metric-value">{forecast_summary.get('confidence', 'N/A')}</div>
                    <div class="metric-sub">Models: {', '.join(forecast_summary.get('models_used', ['N/A']))}</div>
                </div>
            </div>
            <div class="chart-container">
                {forecast_charts.get('1y', '<p style="text-align: center; color: var(--text-muted); padding: 40px;">Chart not available</p>')}
            </div>
        </div>

        <!-- Detailed Analysis Sections (Collapsible) -->
        <div class="card animate-in delay-4">
            <h2>Detailed Analysis</h2>

            <div class="collapsible" onclick="this.classList.toggle('open')">
                <div class="collapsible-header">
                    <div class="collapsible-title">
                        <span class="collapsible-icon">🎯</span>
                        Investment Synthesis
                    </div>
                    <div class="collapsible-toggle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"/>
                        </svg>
                    </div>
                </div>
                <div class="collapsible-content">
                    <div class="collapsible-body">{self.markdown_to_html(synthesis)}</div>
                </div>
            </div>

            <div class="collapsible" onclick="this.classList.toggle('open')">
                <div class="collapsible-header">
                    <div class="collapsible-title">
                        <span class="collapsible-icon">📰</span>
                        News Analysis
                    </div>
                    <div class="collapsible-toggle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"/>
                        </svg>
                    </div>
                </div>
                <div class="collapsible-content">
                    <div class="collapsible-body">{self.markdown_to_html(news_analysis)}</div>
                </div>
            </div>

            <div class="collapsible" onclick="this.classList.toggle('open')">
                <div class="collapsible-header">
                    <div class="collapsible-title">
                        <span class="collapsible-icon">📈</span>
                        Statistical Analysis
                    </div>
                    <div class="collapsible-toggle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"/>
                        </svg>
                    </div>
                </div>
                <div class="collapsible-content">
                    <div class="collapsible-body">{self.markdown_to_html(stats_analysis)}</div>
                </div>
            </div>

            <div class="collapsible" onclick="this.classList.toggle('open')">
                <div class="collapsible-header">
                    <div class="collapsible-title">
                        <span class="collapsible-icon">💼</span>
                        Financial Analysis
                    </div>
                    <div class="collapsible-toggle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"/>
                        </svg>
                    </div>
                </div>
                <div class="collapsible-content">
                    <div class="collapsible-body">{self.markdown_to_html(financial_analysis)}</div>
                </div>
            </div>
        </div>

        <!-- Disclaimer -->
        <div class="disclaimer animate-in delay-4">
            <strong>Important Disclaimer</strong>
            This analysis is generated by AI agents for educational purposes only. It should NOT be considered
            financial advice. Always conduct your own research and consult with a qualified financial advisor
            before making any investment decisions.
        </div>

        <!-- Footer -->
        <div class="footer">
            Generated on {analysis_date}
        </div>
    </div>
</body>
</html>
"""
        return html

    def _extract_synthesis_summary(self, synthesis: str, recommendation: str, confidence: str) -> str:
        """Extract a brief summary from the synthesis"""
        lines = synthesis.split('\n')
        for i, line in enumerate(lines):
            if 'SUMMARY:' in line.upper():
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                return self._clean_text(' '.join(summary_lines))[:300]

        return f"Based on comprehensive analysis, the recommendation is {recommendation} with {confidence} confidence."
    
    def generate_index(self, symbols: list):
        """Generate index.html with links to all stock reports - modern dashboard"""

        reports = []
        for symbol in symbols:
            data = self.get_latest_analysis(symbol)
            if data:
                stock_data = data.get('stock_data', {})
                current_price = stock_data.get('current_price', 0)
                day_change = stock_data.get('day_change', 0)
                day_change_pct = stock_data.get('day_change_percent', 0)

                # Get historical prices for sparkline
                hist_prices = stock_data.get('historical_prices', {})
                prices = list(hist_prices.values()) if hist_prices else []
                sparkline = self.generate_sparkline_svg(prices, width=100, height=40)

                # Get forecast prediction
                forecast_data = data['agents'].get('forecaster', {})
                forecast_summary = forecast_data.get('summary', {})
                prediction = forecast_summary.get('day_10_prediction', current_price)
                pred_change = ((prediction - current_price) / current_price * 100) if current_price else 0

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
                    'day_change': day_change,
                    'day_change_pct': day_change_pct,
                    'sparkline': sparkline,
                    'prediction': prediction,
                    'pred_change': pred_change,
                    'news_sentiment': news_sentiment,
                    'stat_trend': stat_trend,
                    'fin_outlook': fin_outlook,
                    'recommendation': recommendation,
                    'confidence': confidence
                })

        # Count recommendations for summary
        buy_count = sum(1 for r in reports if 'BUY' in r['recommendation'].upper())
        sell_count = sum(1 for r in reports if 'SELL' in r['recommendation'].upper())
        hold_count = len(reports) - buy_count - sell_count

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Investment Planner - AI-Powered Analysis</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        {self.get_common_css()}

        /* Index-specific styles */
        .hero {{
            text-align: center;
            padding: 48px 32px;
        }}

        .hero h1 {{
            font-size: 3rem;
            background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
        }}

        .hero-subtitle {{
            color: var(--text-muted);
            font-size: 1.125rem;
        }}

        /* Stats row */
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}

        .stat-card {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--border-dark);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
        }}

        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 4px;
        }}

        /* Stock grid */
        .stock-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
        }}

        .stock-card {{
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-dark);
            border-radius: 20px;
            padding: 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }}

        .stock-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary);
            box-shadow: 0 20px 40px -15px rgba(99, 102, 241, 0.3);
        }}

        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }}

        .stock-info h3 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-light);
            margin-bottom: 4px;
        }}

        .stock-info .company {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .stock-price {{
            text-align: right;
        }}

        .stock-price .current {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-light);
        }}

        .stock-price .change {{
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .stock-price .change.positive {{ color: var(--success); }}
        .stock-price .change.negative {{ color: var(--danger); }}

        .stock-chart {{
            background: rgba(15, 23, 42, 0.5);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
        }}

        .stock-metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}

        .stock-metric {{
            background: rgba(15, 23, 42, 0.5);
            border-radius: 10px;
            padding: 12px;
        }}

        .stock-metric .label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stock-metric .value {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-light);
            margin-top: 4px;
        }}

        .stock-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }}

        .stock-recommendation {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid var(--border-dark);
        }}

        .rec-pill {{
            padding: 8px 20px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
        }}

        .rec-pill.buy {{ background: linear-gradient(135deg, #10b981, #059669); color: white; }}
        .rec-pill.sell {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }}
        .rec-pill.hold {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }}

        .view-arrow {{
            color: var(--primary-light);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        /* Legend */
        .legend {{
            display: flex;
            justify-content: center;
            gap: 24px;
            flex-wrap: wrap;
            margin-top: 32px;
            padding: 20px;
            background: rgba(30, 41, 59, 0.4);
            border-radius: 12px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .stock-grid {{ grid-template-columns: 1fr; }}
            .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero -->
        <div class="card hero animate-in">
            <h1>Stock Investment Planner</h1>
            <p class="hero-subtitle">AI-Powered Multi-Agent Stock Analysis</p>
        </div>

        <!-- Stats Summary -->
        <div class="stats-row animate-in delay-1">
            <div class="stat-card">
                <div class="stat-value" style="color: var(--success);">{buy_count}</div>
                <div class="stat-label">Buy Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--warning);">{hold_count}</div>
                <div class="stat-label">Hold Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--danger);">{sell_count}</div>
                <div class="stat-label">Sell Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--primary-light);">{len(reports)}</div>
                <div class="stat-label">Stocks Analyzed</div>
            </div>
        </div>

        <!-- Stock Grid -->
        <div class="stock-grid animate-in delay-2">
"""

        for i, report in enumerate(reports):
            news_badge_class = self._get_badge_class(report['news_sentiment'])
            stat_badge_class = self._get_badge_class(report['stat_trend'])
            fin_badge_class = self._get_valuation_badge_class(report['fin_outlook'])

            rec_upper = report['recommendation'].upper()
            rec_class = "buy" if "BUY" in rec_upper else "sell" if "SELL" in rec_upper else "hold"

            change_class = "positive" if report['day_change'] >= 0 else "negative"
            change_symbol = "+" if report['day_change'] >= 0 else ""

            pred_class = "positive" if report['pred_change'] >= 0 else "negative"
            pred_symbol = "+" if report['pred_change'] >= 0 else ""

            html += f"""
            <a href="{report['file']}" class="stock-card">
                <div class="stock-header">
                    <div class="stock-info">
                        <h3>{report['symbol']}</h3>
                        <div class="company">{report['company']}</div>
                    </div>
                    <div class="stock-price">
                        <div class="current">${report['price']:.2f}</div>
                        <div class="change {change_class}">{change_symbol}{report['day_change_pct']:.2f}%</div>
                    </div>
                </div>

                <div class="stock-chart">
                    {report['sparkline']}
                </div>

                <div class="stock-metrics">
                    <div class="stock-metric">
                        <div class="label">10-Day Target</div>
                        <div class="value">${report['prediction']:.2f}</div>
                    </div>
                    <div class="stock-metric">
                        <div class="label">Expected Change</div>
                        <div class="value" style="color: var({'--success' if report['pred_change'] >= 0 else '--danger'});">{pred_symbol}{report['pred_change']:.1f}%</div>
                    </div>
                </div>

                <div class="stock-badges">
                    <span class="badge {news_badge_class}">{report['news_sentiment']}</span>
                    <span class="badge {stat_badge_class}">{report['stat_trend']}</span>
                    <span class="badge {fin_badge_class}">{report['fin_outlook']}</span>
                </div>

                <div class="stock-recommendation">
                    <span class="rec-pill {rec_class}">{report['recommendation']}</span>
                    <span class="view-arrow">
                        View Details
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                    </span>
                </div>
            </a>
"""

        html += """
        </div>

        <!-- Legend -->
        <div class="legend animate-in delay-3">
            <div class="legend-item">
                <div class="legend-dot" style="background: var(--success);"></div>
                Bullish / Buy
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: var(--warning);"></div>
                Neutral / Hold
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: var(--danger);"></div>
                Bearish / Sell
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Powered by Ollama AI Agents</p>
            <p style="margin-top: 8px; opacity: 0.7;">For Educational Purposes Only - Not Financial Advice</p>
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
