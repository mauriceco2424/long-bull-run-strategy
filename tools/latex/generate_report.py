#!/usr/bin/env python3
"""
LaTeX Report Generation System

This script generates professional PDF reports from trading strategy evaluation results.
It takes analysis artifacts and renders them into a LaTeX document, then compiles to PDF.

Usage:
    python tools/latex/generate_report.py --run-id <run_id> [--output <output.pdf>]
"""

import argparse
import json
import sys
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import tempfile
import re


class LaTeXReportGenerator:
    """Generates professional PDF reports from trading strategy evaluation results."""
    
    def __init__(self, run_id: str, run_data_path: str = "data/runs"):
        self.run_id = run_id
        self.run_path = Path(run_data_path) / run_id
        self.template_path = Path("tools/latex/templates/strategy_report.tex")
        
        # Load run data
        self.manifest = self._load_json("manifest.json")
        self.metrics = self._load_json("metrics.json")
        
        # Check for required files
        self._validate_inputs()
    
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
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate the complete PDF report."""
        
        if output_path is None:
            output_path = f"{self.run_id}_strategy_report.pdf"
        
        print(f"Generating PDF report for run {self.run_id}...")
        
        # Prepare template data
        template_data = self._prepare_template_data()
        
        # Generate LaTeX document
        latex_content = self._render_template(template_data)
        
        # Compile to PDF
        pdf_path = self._compile_latex(latex_content, output_path)
        
        print(f"Report generated successfully: {pdf_path}")
        return pdf_path
    
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
        
        # Chart paths (relative to LaTeX working directory)
        data.update(self._prepare_chart_paths())
        
        # Analysis text (will be filled by evaluator)
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
        """Prepare paths to chart files."""
        
        figs_path = self.run_path / "figs"
        
        # Look for standard chart files
        chart_files = {
            'equity_chart_path': 'equity_curve.png',
            'trade_analysis_chart_path': 'trade_analysis.png',
            'symbol_chart_1_path': 'symbol_1.png',
            'symbol_chart_2_path': 'symbol_2.png',
        }
        
        chart_paths = {}
        for key, filename in chart_files.items():
            chart_path = figs_path / filename
            if chart_path.exists():
                chart_paths[key] = str(chart_path.absolute())
            else:
                # Fallback to first available chart
                available_charts = list(figs_path.glob("*.png"))
                if available_charts:
                    chart_paths[key] = str(available_charts[0].absolute())
                else:
                    chart_paths[key] = "chart_not_found.png"
        
        return chart_paths
    
    def _prepare_analysis_sections(self) -> Dict[str, str]:
        """Prepare analysis text sections (to be filled by evaluator)."""
        
        # These are placeholders that should be filled by the evaluator
        return {
            'performance_rating': 'TO BE FILLED BY EVALUATOR',
            'executive_summary_text': 'Executive summary to be provided by evaluator based on performance analysis.',
            'recommendation_items': '\\item Recommendation 1\\n\\item Recommendation 2',
            'strategy_description': self.manifest.get('strategy_description', 'Strategy description from template'),
            'parameter_table_rows': self._generate_parameter_table(),
            'equity_analysis_text': 'detailed equity curve analysis including trend identification and key performance periods',
            'drawdown_analysis_text': 'Analysis of drawdown periods and recovery characteristics.',
            'max_dd_period': 'period to be identified by evaluator',
            'risk_adjusted_analysis': 'Risk-adjusted performance analysis to be provided by evaluator.',
            'market_behavior_analysis': 'Market behavior analysis to be provided by evaluator.',
            'strategy_effectiveness_analysis': 'Strategy effectiveness analysis to be provided by evaluator.',
            'parameter_sensitivity_analysis': 'Parameter sensitivity analysis to be provided by evaluator.',
            'regime_performance_rows': 'Regime & Performance data to be filled by evaluator',
            'statistical_significance_text': 'Statistical significance analysis to be provided by evaluator.',
            'lookahead_status': 'PASS',
            'liquidity_status': 'PASS',
            'execution_status': 'PASS',
            'accounting_status': 'PASS',
            'cagr_ci_lower': 'TBD',
            'cagr_ci_upper': 'TBD',
            'sortino_ci_lower': 'TBD',
            'sortino_ci_upper': 'TBD',
            'winrate_ci_lower': 'TBD', 
            'winrate_ci_upper': 'TBD',
            'per_symbol_analysis_section': 'Per-symbol analysis to be provided by evaluator.',
            'symbol_1_name': 'Symbol 1',
            'symbol_2_name': 'Symbol 2',
            'overall_assessment': 'Overall assessment to be provided by evaluator.',
            'optimization_recommendations': '\\item Optimization 1\\n\\item Optimization 2',
            'implementation_considerations': 'Implementation considerations to be provided by evaluator.',
            'next_steps_recommendations': 'Next steps to be provided by evaluator.',
            'data_source': self.manifest.get('data_source', 'N/A'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'methodology_notes': 'Methodology notes and assumptions.',
            'var_95': 'TBD',
            'expected_shortfall': 'TBD',
            'max_consecutive_losses': str(self.metrics.get('max_consecutive_losses', 'N/A')),
        }
    
    def _generate_parameter_table(self) -> str:
        """Generate LaTeX table rows for parameters."""
        
        # Extract parameters from manifest or config
        parameters = self.manifest.get('parameters', {})
        
        if not parameters:
            return "No parameters available & & \\\\"
        
        rows = []
        for param_name, param_value in parameters.items():
            param_name_display = param_name.replace('_', '\\_')
            rows.append(f"{param_name_display} & {param_value} & Strategy parameter \\\\")
        
        return '\n'.join(rows)
    
    def _render_template(self, data: Dict[str, str]) -> str:
        """Render the LaTeX template with data."""
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"LaTeX template not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple template substitution using {{key}} format
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        return template_content
    
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
                    ['pdflatex', '-interaction=nonstopmode', 'report.tex'],
                    cwd=temp_dir_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Second pass for references
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 'report.tex'],
                    cwd=temp_dir_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Copy PDF to output location
                pdf_source = temp_dir_path / "report.pdf"
                output_path = Path(output_path).resolve()
                shutil.copy2(pdf_source, output_path)
                
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
    
    def check_latex_availability(self) -> bool:
        """Check if LaTeX is available on the system."""
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False


def main():
    """Main entry point for report generation."""
    
    parser = argparse.ArgumentParser(description='Generate professional PDF report from trading strategy analysis')
    parser.add_argument(
        '--run-id',
        required=True,
        help='Run ID for the strategy analysis'
    )
    parser.add_argument(
        '--output',
        help='Output PDF path (default: <run_id>_strategy_report.pdf)'
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
        generator = LaTeXReportGenerator("dummy", args.run_data_path)
        if generator.check_latex_availability():
            print("LaTeX is available for report generation")
            sys.exit(0)
        else:
            print("LaTeX is not available. Please install LaTeX (e.g., TeX Live, MiKTeX)")
            sys.exit(1)
    
    try:
        # Generate report
        generator = LaTeXReportGenerator(args.run_id, args.run_data_path)
        
        # Check LaTeX availability
        if not generator.check_latex_availability():
            print("Warning: LaTeX not available. Please install LaTeX for PDF generation.")
            print("Recommended: TeX Live (Linux/Mac) or MiKTeX (Windows)")
            sys.exit(1)
        
        pdf_path = generator.generate_report(args.output)
        
        print(f"Report generation completed successfully!")
        print(f"Output: {pdf_path}")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()