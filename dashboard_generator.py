"""
Simple Web Dashboard for Enterprise Contextual Compression Engine
Visualize compression results with an interactive HTML dashboard
"""

from api_wrapper import CompressionAPI
import json
from datetime import datetime

class DashboardGenerator:
    """Generate HTML dashboard for compression results"""
    
    def __init__(self):
        self.api = CompressionAPI()
    
    def generate_dashboard(self, document_text, output_file="dashboard.html"):
        """Generate interactive HTML dashboard"""
        
        # Process document
        result = self.api.compress_text(document_text)
        
        # Generate HTML
        html = self._build_html(result)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def _build_html(self, result):
        """Build complete HTML dashboard"""
        
        metadata = result['metadata']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compression Engine Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .content-section {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .item-list {{
            list-style: none;
        }}
        
        .item {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        .item:hover {{
            background: #e9ecef;
            border-left-width: 8px;
        }}
        
        .item-statement {{
            font-size: 1.1em;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .item-meta {{
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #6c757d;
            flex-wrap: wrap;
        }}
        
        .badge {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            display: inline-block;
        }}
        
        .badge-warning {{
            background: #ffc107;
            color: #333;
        }}
        
        .badge-danger {{
            background: #dc3545;
        }}
        
        .badge-success {{
            background: #28a745;
        }}
        
        .contradiction {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .tab {{
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1.1em;
            color: #6c757d;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }}
        
        .tab:hover {{
            color: #667eea;
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .quote {{
            background: #e7f3ff;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #0056b3;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #667eea;
        }}
        
        .timeline-item {{
            position: relative;
            padding-bottom: 30px;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -35px;
            top: 5px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 2px #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Compression Analysis Dashboard</h1>
            <p>Document processed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Chunks</div>
                <div class="stat-value">{metadata['total_chunks']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Items Extracted</div>
                <div class="stat-value">{metadata['total_extracted_items']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Compression Ratio</div>
                <div class="stat-value">{metadata['compression_ratio']:.2f}x</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Strategy</div>
                <div class="stat-value" style="font-size: 1.5em;">{metadata['chunk_strategy']}</div>
            </div>
        </div>
        
        <div class="content-section">
            <div class="tabs">
                <button class="tab active" onclick="showTab('executive')">Executive Summary</button>
                <button class="tab" onclick="showTab('numbers')">Numbers & Limits</button>
                <button class="tab" onclick="showTab('dates')">Dates & Timelines</button>
                <button class="tab" onclick="showTab('exceptions')">Exceptions</button>
                <button class="tab" onclick="showTab('risks')">Risks</button>
                <button class="tab" onclick="showTab('contradictions')">Contradictions</button>
            </div>
            
            <div id="executive" class="tab-content active">
                <h2 class="section-title">⚡ Executive Summary</h2>
                <ul class="item-list">
                    {self._generate_executive_summary_html(result['executive_compressed_summary'])}
                </ul>
            </div>
            
            <div id="numbers" class="tab-content">
                <h2 class="section-title">💰 Numbers and Limits</h2>
                <ul class="item-list">
                    {self._generate_items_html(result['numbers_and_limits'])}
                </ul>
            </div>
            
            <div id="dates" class="tab-content">
                <h2 class="section-title">📅 Dates and Timelines</h2>
                <div class="timeline">
                    {self._generate_timeline_html(result['dates_and_timelines'])}
                </div>
            </div>
            
            <div id="exceptions" class="tab-content">
                <h2 class="section-title">⚠️ Exceptions and Conditions</h2>
                <ul class="item-list">
                    {self._generate_items_html(result['exceptions_and_conditions'])}
                </ul>
            </div>
            
            <div id="risks" class="tab-content">
                <h2 class="section-title">🚨 Risks and Constraints</h2>
                <ul class="item-list">
                    {self._generate_items_html(result['risks_and_constraints'])}
                </ul>
            </div>
            
            <div id="contradictions" class="tab-content">
                <h2 class="section-title">❗ Contradictions Detected</h2>
                {self._generate_contradictions_html(result['contradictions'])}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _generate_executive_summary_html(self, items):
        """Generate HTML for executive summary"""
        if not items:
            return "<li class='item'>No executive summary items found</li>"
        
        html = ""
        for item in items[:10]:  # Top 10 items
            priority_badge = self._get_priority_badge(item.get('priority', ''))
            html += f"""
                <li class="item">
                    <div class="item-statement">{self._escape_html(item['statement'])}</div>
                    <div class="item-meta">
                        <span>{priority_badge}</span>
                        <span>Source: {', '.join(item['source_chunks'])}</span>
                    </div>
                </li>
            """
        return html
    
    def _generate_items_html(self, items):
        """Generate HTML for regular items"""
        if not items:
            return "<li class='item'>No items found in this category</li>"
        
        html = ""
        for item in items:
            quote_html = f"<span class='quote'>{self._escape_html(item.get('quote', ''))}</span>" if item.get('quote') else ""
            html += f"""
                <li class="item">
                    <div class="item-statement">{self._escape_html(item['statement'])}</div>
                    <div class="item-meta">
                        {f"<span>Value: {quote_html}</span>" if quote_html else ""}
                        <span>Source: {', '.join(item['source_chunks'])}</span>
                    </div>
                </li>
            """
        return html
    
    def _generate_timeline_html(self, items):
        """Generate timeline HTML for dates"""
        if not items:
            return "<div class='item'>No timeline items found</div>"
        
        html = ""
        for item in items:
            html += f"""
                <div class="timeline-item">
                    <div class="item">
                        <div class="item-statement">{self._escape_html(item['statement'])}</div>
                        <div class="item-meta">
                            <span class="quote">{self._escape_html(item.get('quote', ''))}</span>
                            <span>Source: {', '.join(item['source_chunks'])}</span>
                        </div>
                    </div>
                </div>
            """
        return html
    
    def _generate_contradictions_html(self, contradictions):
        """Generate HTML for contradictions"""
        if not contradictions:
            return "<div class='item'><strong>✅ No contradictions detected</strong></div>"
        
        html = "<ul class='item-list'>"
        for idx, c in enumerate(contradictions[:10], 1):
            html += f"""
                <li class="item contradiction">
                    <div class="item-statement">
                        <strong>Contradiction #{idx}</strong>
                    </div>
                    <div style="margin-top: 15px;">
                        <div><span class="badge badge-warning">Statement 1 ({c['source_chunk_1']})</span></div>
                        <p style="margin: 10px 0;">{self._escape_html(c['statement_1'])}</p>
                        
                        <div><span class="badge badge-warning">Statement 2 ({c['source_chunk_2']})</span></div>
                        <p style="margin: 10px 0;">{self._escape_html(c['statement_2'])}</p>
                    </div>
                </li>
            """
        html += "</ul>"
        return html
    
    def _get_priority_badge(self, priority):
        """Get HTML badge for priority"""
        badges = {
            'risk_penalty': '<span class="badge badge-danger">🚨 Risk/Penalty</span>',
            'compliance_requirement': '<span class="badge badge-danger">📋 Compliance</span>',
            'number_limit': '<span class="badge">💰 Number/Limit</span>',
            'date_timeline': '<span class="badge">📅 Date/Timeline</span>',
            'exception_condition': '<span class="badge badge-warning">⚠️ Exception</span>',
            'objective_fact': '<span class="badge badge-success">✓ Fact</span>'
        }
        return badges.get(priority, '<span class="badge">Info</span>')
    
    def _escape_html(self, text):
        """Escape HTML special characters"""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


# Example usage
if __name__ == "__main__":
    sample_document = """
    EMPLOYMENT AGREEMENT

    Effective Date: January 15, 2024
    
    Compensation: Base salary of $120,000 per year, plus annual bonus up to 25%.
    
    Benefits: 20 days PTO, health insurance, 401(k) with 5% company match.
    
    Termination: Either party may terminate with 30 days notice. 
    However, termination for cause results in immediate cessation of benefits.
    Severance pay of 3 months salary applies unless terminated for cause.
    
    Non-Compete: 12 month restriction within 100 mile radius, unless waived by company.
    
    Confidentiality: Must be maintained for 5 years post-termination.
    Violation may result in penalties up to $250,000.
    
    Stock Options: 5,000 options at $15 strike price, vesting over 4 years.
    
    Review Dates: Quarterly reviews required. Annual review on December 15, 2024.
    """
    
    # Generate dashboard
    generator = DashboardGenerator()
    output_file = generator.generate_dashboard(sample_document)
    
    print(f"Dashboard generated: {output_file}")
    print("Open the file in your web browser to view the interactive dashboard.")
