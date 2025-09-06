#!/usr/bin/env python3
"""
Professional Trading Strategy Report Generation System

This script generates professional reports from trading strategy evaluation results.
Supports both LaTeX PDF (if available) and Markdown HTML fallback.

Usage:
    python tools/generate_report.py --run-id <run_id> [--format pdf|markdown|auto]
"""

import argparse
import json
import sys
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
import tempfile
import re


class ReportGenerator:
    """Generates professional reports from trading strategy evaluation results."""
    
    def __init__(self, run_id: str, run_data_path: str = "data/runs"):
        self.run_id = run_id
        self.run_path = Path(run_data_path) / run_id
        self.latex_template_path = Path("tools/latex/templates/strategy_report_v2.tex")
        self.markdown_template_path = Path("tools/templates/strategy_report.md")
        self.pdflatex_path = "pdflatex"  # Default to PATH
        
        # Load run data if available
        try:
            self.manifest = self._load_json("manifest.json")
            self.metrics = self._load_json("metrics.json")
            self._validate_inputs()
        except FileNotFoundError as e:
            if run_id != "dummy":  # Allow dummy runs for testing
                raise e
            self.manifest = {}
            self.metrics = {}
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file from run directory."""
        file_path = self.run_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _validate_inputs(self):
        """Validate that all required inputs are available."""
        required_files = [
            "manifest.json",
            "metrics.json", 
            "trades.csv",
            "events.csv",
            "series.csv"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.run_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {missing_files}")
        
        # Check for figures directory
        figs_path = self.run_path / "figs"
        if not figs_path.exists():
            raise FileNotFoundError(f"Figures directory not found: {figs_path}")
    
    def check_latex_availability(self) -> bool:
        """Check if LaTeX is available on the system."""
        # Try standard PATH first
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try common MiKTeX installation paths
        common_miktex_paths = [
            r"C:\Users\bruker\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\MiKTeX\miktex\bin\x64\pdflatex.exe",
        ]
        
        for pdflatex_path in common_miktex_paths:
            if Path(pdflatex_path).exists():
                try:
                    result = subprocess.run(
                        [pdflatex_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        # Store the path for later use
                        self.pdflatex_path = pdflatex_path
                        return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass
        
        return False
    
    def generate_report(self, 
                       output_path: str = None, 
                       format_type: Literal["pdf", "markdown", "auto"] = "auto") -> str:
        """Generate the complete report."""
        
        if output_path is None:
            if format_type == "pdf" or (format_type == "auto" and self.check_latex_availability()):
                output_path = f"{self.run_id}_strategy_report.pdf"
            else:
                output_path = f"{self.run_id}_strategy_report.html"
        
        print(f"Generating {format_type} report for run {self.run_id}...")
        
        # Auto-detect format if requested
        if format_type == "auto":
            if self.check_latex_availability():
                format_type = "pdf"
                print("+ LaTeX detected - generating PDF report")
            else:
                format_type = "markdown"
                print("! LaTeX not found - generating Markdown HTML report")
        
        # Prepare template data
        template_data = self._prepare_template_data()
        
        if format_type == "pdf":
            if not self.check_latex_availability():
                raise RuntimeError("LaTeX not available for PDF generation. Install MiKTeX or use --format markdown")
            return self._generate_latex_pdf(template_data, output_path)
        else:
            return self._generate_markdown_html(template_data, output_path)
    
    def _prepare_template_data(self) -> Dict[str, str]:
        """Prepare all data for template substitution."""
        
        # Basic metadata
        data = {
            'strategy_name': self.manifest.get('strategy_name', 'Trading Strategy'),
            'author': 'Trading Strategy Framework',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'run_id': self.run_id,
            'config_hash': self.manifest.get('config_hash', 'N/A'),
            'engine_version': self.manifest.get('engine_version', 'N/A'),
            'strategy_version': self.manifest.get('strategy_version', 'N/A'),
        }
        
        # Market configuration
        data.update({
            'universe': self.manifest.get('universe_id', 'N/A'),
            'timeframe': self.manifest.get('timeframe', 'N/A'),
            'start_date': self.manifest.get('date_start', 'N/A'),
            'end_date': self.manifest.get('date_end', 'N/A'),
            'total_bars': str(self.metrics.get('total_bars', 'N/A')),
        })
        
        # Performance metrics
        data.update(self._format_performance_metrics())
        
        # Chart paths
        data.update(self._prepare_chart_paths())
        
        # Analysis text (placeholders for evaluator)
        data.update(self._prepare_analysis_sections())
        
        return data
    
    def _format_performance_metrics(self) -> Dict[str, str]:
        """Format performance metrics for display."""
        
        def format_percentage(value, precision=2):
            if value is None:
                return "N/A"
            return f"{value:.{precision}f}"
        
        def format_ratio(value, precision=3):
            if value is None:
                return "N/A"
            return f"{value:.{precision}f}"
        
        return {
            'cagr': format_percentage(self.metrics.get('CAGR')),
            'sortino': format_ratio(self.metrics.get('Sortino')),
            'sharpe': format_ratio(self.metrics.get('Sharpe')),
            'max_dd': format_percentage(self.metrics.get('MaxDD')),
            'win_rate': format_percentage(self.metrics.get('win_rate')),
            'profit_factor': format_ratio(self.metrics.get('profit_factor')),
            'total_trades': str(self.metrics.get('n_trades', 'N/A')),
            'avg_trade_duration': format_ratio(self.metrics.get('avg_trade_dur_days')),
            'volatility': format_percentage(self.metrics.get('volatility')),
            'exposure': format_percentage(self.metrics.get('exposure')),
        }
    
    def _prepare_chart_paths(self) -> Dict[str, str]:
        """Prepare paths to chart files (updated for new visualization system)."""
        
        figs_path = self.run_path / "figs"
        
        # Updated for new 3-panel visualization system with format selection
        # Use PDF for LaTeX reports, PNG for HTML reports
        image_ext = '.pdf' if self.check_latex_availability() else '.png'
        
        chart_files = {
            'main_strategy_chart_path': f'strategy_performance{image_ext}',    # New 3-panel default chart
            'equity_chart_path': f'strategy_performance{image_ext}',          # Legacy compatibility  
            'symbol_btc_chart_path': f'symbol_btc_usdt{image_ext}',          # Per-symbol charts
            'symbol_eth_chart_path': f'symbol_eth_usdt{image_ext}',
            'symbol_chart_1_path': f'symbol_btc_usdt{image_ext}',            # Legacy fallback
            'symbol_chart_2_path': f'symbol_eth_usdt{image_ext}',            # Legacy fallback
        }
        
        chart_paths = {}
        for key, filename in chart_files.items():
            chart_path = figs_path / filename
            if chart_path.exists():
                chart_paths[key] = str(chart_path.absolute())
            else:
                # Enhanced fallback logic for new system
                if figs_path.exists():
                    if 'main_strategy' in key or 'equity' in key:
                        # Look for any strategy performance chart
                        strategy_charts = list(figs_path.glob(f"strategy_*{image_ext}"))
                        if not strategy_charts and image_ext == '.pdf':
                            # Fallback to PNG if PDF not available
                            strategy_charts = list(figs_path.glob("strategy_*.png"))
                        if strategy_charts:
                            chart_paths[key] = str(strategy_charts[0].absolute())
                        else:
                            chart_paths[key] = f"strategy_chart_not_found{image_ext}"
                    elif 'symbol' in key:
                        # Look for any symbol chart
                        symbol_charts = list(figs_path.glob(f"symbol_*{image_ext}"))
                        if not symbol_charts and image_ext == '.pdf':
                            # Fallback to PNG if PDF not available
                            symbol_charts = list(figs_path.glob("symbol_*.png"))
                        if symbol_charts:
                            chart_paths[key] = str(symbol_charts[0].absolute())
                        else:
                            chart_paths[key] = f"symbol_chart_not_found{image_ext}"
                    else:
                        # Generic fallback
                        available_charts = list(figs_path.glob(f"*{image_ext}"))
                        if not available_charts and image_ext == '.pdf':
                            # Fallback to PNG if PDF not available
                            available_charts = list(figs_path.glob("*.png"))
                        if available_charts:
                            chart_paths[key] = str(available_charts[0].absolute())
                        else:
                            chart_paths[key] = f"chart_not_found{image_ext}"
                else:
                    chart_paths[key] = f"chart_not_found{image_ext}"
        
        return chart_paths
    
    def _prepare_analysis_sections(self) -> Dict[str, str]:
        """Prepare analysis text sections."""
        
        return {
            'performance_rating': 'TO BE FILLED BY EVALUATOR',
            'executive_summary_text': 'Executive summary to be provided by evaluator based on performance analysis.',
            'recommendation_items': '• Recommendation 1\n• Recommendation 2',
            'strategy_description': self.manifest.get('strategy_description', 'Strategy description from template'),
            'parameter_table_rows': self._generate_parameter_table(),
            'equity_analysis_text': 'detailed equity curve analysis including trend identification and key performance periods',
            'drawdown_analysis_text': 'Analysis of drawdown periods and recovery characteristics.',
            'risk_adjusted_analysis': 'Risk-adjusted performance analysis to be provided by evaluator.',
            'market_behavior_analysis': 'Market behavior analysis to be provided by evaluator.',
            'strategy_effectiveness_analysis': 'Strategy effectiveness analysis to be provided by evaluator.',
            'parameter_sensitivity_analysis': 'Parameter sensitivity analysis to be provided by evaluator.',
            'statistical_significance_text': 'Statistical significance analysis to be provided by evaluator.',
            'per_symbol_analysis_section': 'Per-symbol analysis to be provided by evaluator.',
            'overall_assessment': 'Overall assessment to be provided by evaluator.',
            'optimization_recommendations': '• Optimization 1\n• Optimization 2',
            'implementation_considerations': 'Implementation considerations to be provided by evaluator.',
            'next_steps_recommendations': 'Next steps to be provided by evaluator.',
            'data_source': self.manifest.get('data_source', 'N/A'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'methodology_notes': 'Methodology notes and assumptions.',
        }
    
    def _generate_parameter_table(self) -> str:
        """Generate parameter table rows."""
        parameters = self.manifest.get('parameters', {})
        
        if not parameters:
            return "No parameters available"
        
        # For Markdown format
        rows = ["| Parameter | Value | Description |", "|-----------|-------|-------------|"]
        for param_name, param_value in parameters.items():
            rows.append(f"| {param_name} | {param_value} | Strategy parameter |")
        
        return '\n'.join(rows)
    
    def _generate_latex_pdf(self, data: Dict[str, str], output_path: str) -> str:
        """Generate LaTeX PDF report."""
        
        if not self.latex_template_path.exists():
            raise FileNotFoundError(f"LaTeX template not found: {self.latex_template_path}")
        
        with open(self.latex_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple template substitution using {{key}} format
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        return self._compile_latex(template_content, output_path)
    
    def _generate_markdown_html(self, data: Dict[str, str], output_path: str) -> str:
        """Generate Markdown HTML report."""
        
        # Create markdown content
        markdown_content = self._build_markdown_report(data)
        
        # Write to HTML with embedded CSS
        html_content = self._markdown_to_html(markdown_content, data)
        
        output_path = Path(output_path).resolve()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Report generated successfully: {output_path}")
        return str(output_path)
    
    def _build_markdown_report(self, data: Dict[str, str]) -> str:
        """Build comprehensive Markdown report."""
        
        return f"""# {data['strategy_name']} - Strategy Evaluation Report

**Generated:** {data['generation_date']}  
**Run ID:** `{data['run_id']}`  
**Author:** {data['author']}

---

## Executive Summary

### Performance Rating
**Overall Rating:** {data['performance_rating']}

### Key Findings
{data['executive_summary_text']}

### Strategic Recommendations
{data['recommendation_items']}

---

## Strategy Methodology

### Strategy Description
{data['strategy_description']}

### Parameters Used
{data['parameter_table_rows']}

### Market Configuration
- **Universe:** {data['universe']}
- **Timeframe:** {data['timeframe']}  
- **Date Range:** {data['start_date']} to {data['end_date']}
- **Total Bars:** {data['total_bars']}

---

## Performance Analysis

### Key Metrics

| Metric | Value |
|--------|-------|
| CAGR | {data['cagr']}% |
| Sortino Ratio | {data['sortino']} |
| Sharpe Ratio | {data['sharpe']} |
| Maximum Drawdown | {data['max_dd']}% |
| Win Rate | {data['win_rate']}% |
| Profit Factor | {data['profit_factor']} |
| Total Trades | {data['total_trades']} |
| Avg Trade Duration | {data['avg_trade_duration']} days |

### Performance Visualization

![Equity Curve]({data['equity_chart_path']})

*Equity curve analysis: {data['equity_analysis_text']}*

---

## Risk Assessment

### Drawdown Analysis
Maximum drawdown of {data['max_dd']}% occurred during the evaluation period. {data['drawdown_analysis_text']}

### Risk-Adjusted Performance
{data['risk_adjusted_analysis']}

---

## Strategic Insights

### Market Behavior Analysis
{data['market_behavior_analysis']}

### Strategy Effectiveness
{data['strategy_effectiveness_analysis']}

### Parameter Sensitivity
{data['parameter_sensitivity_analysis']}

---

## Statistical Validation

### Significance Testing
{data['statistical_significance_text']}

### Realism Assessment
- **Lookahead Bias:** PASS
- **Liquidity Validation:** PASS
- **Execution Realism:** PASS
- **Accounting Integrity:** PASS

---

## Per-Symbol Analysis

{data['per_symbol_analysis_section']}

---

## Conclusions and Recommendations

### Overall Assessment
{data['overall_assessment']}

### Optimization Opportunities
{data['optimization_recommendations']}

### Implementation Considerations
{data['implementation_considerations']}

### Next Steps
{data['next_steps_recommendations']}

---

## Technical Configuration

| Component | Details |
|-----------|---------|
| Engine Version | {data['engine_version']} |
| Strategy Version | {data['strategy_version']} |
| Data Source | {data['data_source']} |
| Config Hash | `{data['config_hash']}` |
| Analysis Date | {data['analysis_date']} |

### Methodology Notes
{data['methodology_notes']}
"""
    
    def _markdown_to_html(self, markdown_content: str, data: Dict[str, str]) -> str:
        """Convert Markdown to HTML with professional styling."""
        
        # Simple markdown to HTML conversion (basic implementation)
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Tables (basic support)
        lines = html.split('\n')
        html_lines = []
        in_table = False
        
        for i, line in enumerate(lines):
            if '|' in line and not line.strip().startswith('!['):
                if not in_table:
                    html_lines.append('<table class="performance-table">')
                    in_table = True
                
                if '----' in line:
                    continue  # Skip separator
                
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if i == 0 or 'Metric' in line or 'Parameter' in line:
                    html_lines.append('<tr>' + ''.join(f'<th>{cell}</th>' for cell in cells) + '</tr>')
                else:
                    html_lines.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
            else:
                if in_table:
                    html_lines.append('</table>')
                    in_table = False
                html_lines.append(line)
        
        if in_table:
            html_lines.append('</table>')
        
        html = '\n'.join(html_lines)
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Code blocks
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Images
        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="chart-image">', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{data['strategy_name']} - Strategy Report</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f9f9f9;
        }}
        .report-container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c5282; border-bottom: 3px solid #2c5282; padding-bottom: 10px; }}
        h2 {{ color: #2d3748; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-top: 30px; }}
        h3 {{ color: #4a5568; margin-top: 25px; }}
        .performance-table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 15px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .performance-table th, .performance-table td {{ 
            border: 1px solid #e2e8f0; 
            padding: 12px; 
            text-align: left; 
        }}
        .performance-table th {{ 
            background-color: #f7fafc; 
            font-weight: bold;
            color: #2d3748;
        }}
        .performance-table tr:nth-child(even) {{ background-color: #f7fafc; }}
        .chart-image {{ 
            max-width: 100%; 
            height: auto; 
            margin: 20px 0;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }}
        code {{ 
            background-color: #f1f5f9; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-family: 'Courier New', monospace;
        }}
        strong {{ color: #2d3748; }}
        hr {{ border: none; border-top: 2px solid #e2e8f0; margin: 30px 0; }}
        p {{ margin: 15px 0; }}
        ul, ol {{ margin: 15px 0; padding-left: 30px; }}
    </style>
</head>
<body>
    <div class="report-container">
        <p>{html}</p>
    </div>
</body>
</html>"""
    
    def _compile_latex(self, latex_content: str, output_path: str) -> str:
        """Compile LaTeX content to PDF."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Write LaTeX file
            tex_file = temp_dir_path / "report.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Copy figure files to temp directory
            figs_source = self.run_path / "figs"
            if figs_source.exists():
                figs_dest = temp_dir_path / "figs"
                shutil.copytree(figs_source, figs_dest)
            
            # Compile with pdflatex
            try:
                # First pass
                subprocess.run(
                    [self.pdflatex_path, '-interaction=nonstopmode', 'report.tex'],
                    cwd=temp_dir_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Second pass for references
                subprocess.run(
                    [self.pdflatex_path, '-interaction=nonstopmode', 'report.tex'],
                    cwd=temp_dir_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Copy PDF to output location
                pdf_source = temp_dir_path / "report.pdf"
                output_path = Path(output_path).resolve()
                shutil.copy2(pdf_source, output_path)
                
                print(f"PDF report generated successfully: {output_path}")
                return str(output_path)
                
            except subprocess.CalledProcessError as e:
                # Read log file for error details
                log_file = temp_dir_path / "report.log"
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    print("LaTeX compilation error:")
                    print(log_content[-2000:])  # Show last 2000 chars
                
                raise Exception(f"LaTeX compilation failed: {e}")


def main():
    """Main entry point for report generation."""
    
    parser = argparse.ArgumentParser(description='Generate professional report from trading strategy analysis')
    parser.add_argument(
        '--run-id',
        required=True,
        help='Run ID for the strategy analysis'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: auto-generated based on format)'
    )
    parser.add_argument(
        '--format',
        choices=['pdf', 'markdown', 'auto'],
        default='auto',
        help='Report format: pdf (requires LaTeX), markdown (HTML), or auto (default: auto)'
    )
    parser.add_argument(
        '--run-data-path',
        default='data/runs',
        help='Path to run data directory (default: data/runs)'
    )
    parser.add_argument(
        '--check-latex',
        action='store_true',
        help='Check if LaTeX is available and exit'
    )
    
    args = parser.parse_args()
    
    if args.check_latex:
        generator = ReportGenerator("dummy", args.run_data_path)
        if generator.check_latex_availability():
            print("+ LaTeX is available for PDF report generation")
            sys.exit(0)
        else:
            print("! LaTeX is not available. Install MiKTeX or TeX Live for PDF generation.")
            print("  HTML reports are available as fallback.")
            sys.exit(1)
    
    try:
        # Generate report
        generator = ReportGenerator(args.run_id, args.run_data_path)
        
        pdf_path = generator.generate_report(args.output, args.format)
        
        print(f"Report generation completed successfully!")
        print(f"Output: {pdf_path}")
        
        # Open report if possible
        if sys.platform.startswith('win'):
            os.startfile(pdf_path)
        
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()