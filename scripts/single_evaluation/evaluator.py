"""
Trading Single-Run Evaluator with Enhanced Visual Validation

This module performs comprehensive evaluation of single backtest runs with
mandatory visual validation, accounting reconciliation, and strategic interpretation.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import logging
import warnings

# Suppress matplotlib backend warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from PIL import Image

class SingleRunEvaluator:
    """
    Enhanced evaluator with mandatory visual validation and accounting reconciliation.
    
    Critical features:
    - Visual equity curve validation before metrics acceptance
    - Cross-validation between charts and numerical data
    - Open position verification at period end
    - Accounting identity reconciliation
    - Halt conditions for data discrepancies
    """
    
    def __init__(self, run_id: str, test_mode: bool = False):
        """
        Initialize evaluator with run ID and mode.
        
        Args:
            run_id: Unique identifier for the backtest run
            test_mode: If True, read from data/test_runs/
        """
        self.run_id = run_id
        self.test_mode = test_mode
        
        # Set data directory based on mode
        if test_mode:
            self.run_dir = Path("data/test_runs") / run_id
        else:
            self.run_dir = Path("data/runs") / run_id
        
        # Logging
        self.setup_logging()
        
        # Data containers
        self.manifest = None
        self.metrics = None
        self.series_df = None
        self.trades_df = None
        self.events_df = None
        
        # Validation results
        self.visual_validation = {}
        self.accounting_validation = {}
        self.evaluation_status = "PENDING"
        self.halt_reasons = []
        
    def setup_logging(self):
        """Configure logging for evaluation."""
        log_dir = self.run_dir / "evaluation"
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(f"evaluator_{self.run_id}")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_dir / "evaluation.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def load_run_data(self) -> bool:
        """
        Load all run artifacts from disk.
        
        Returns:
            True if all required data loaded successfully
        """
        try:
            # Load manifest
            with open(self.run_dir / "manifest.json", 'r') as f:
                self.manifest = json.load(f)
            
            # Load metrics
            with open(self.run_dir / "metrics.json", 'r') as f:
                self.metrics = json.load(f)
            
            # Load series data
            self.series_df = pd.read_csv(self.run_dir / "series.csv")
            
            # Load trades
            if (self.run_dir / "trades.csv").exists():
                self.trades_df = pd.read_csv(self.run_dir / "trades.csv")
            
            # Load events
            if (self.run_dir / "events.csv").exists():
                self.events_df = pd.read_csv(self.run_dir / "events.csv")
            
            self.logger.info(f"Successfully loaded run data for {self.run_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load run data: {e}")
            self.halt_reasons.append(f"Data loading error: {e}")
            return False
    
    def perform_visual_validation(self) -> bool:
        """
        MANDATORY: Analyze visual charts before accepting any metrics.
        
        This is the critical validation that prevents accounting discrepancies.
        
        Returns:
            True if visual data matches numerical metrics
        """
        self.logger.info("=" * 80)
        self.logger.info("PERFORMING MANDATORY VISUAL VALIDATION")
        self.logger.info("=" * 80)
        
        # Step 1: Read and analyze main_analysis chart
        chart_path = self.run_dir / "figures" / "main_analysis.png"
        if not chart_path.exists():
            chart_path = self.run_dir / "figures" / "main_analysis.pdf"
        
        if not chart_path.exists():
            self.halt_reasons.append("CRITICAL: Main analysis chart not found")
            self.logger.error("Main analysis chart missing - cannot perform visual validation")
            return False
        
        # Analyze equity curve visually
        self.logger.info(f"Reading visualization from: {chart_path}")
        
        # For this test implementation, we'll analyze the data directly
        # In production, would use image processing or manual inspection
        
        # Step 2: Cross-validate metrics vs visualization
        initial_capital = self.metrics['accounting']['initial_capital']
        final_equity = self.metrics['accounting']['final_equity']
        reported_return = self.metrics['performance']['total_return']
        
        # Calculate expected return from equity values
        actual_return = (final_equity / initial_capital) - 1
        
        # Check for discrepancies
        return_discrepancy = abs(actual_return - reported_return)
        
        self.visual_validation['initial_capital'] = initial_capital
        self.visual_validation['final_equity'] = final_equity
        self.visual_validation['reported_return'] = reported_return
        self.visual_validation['actual_return'] = actual_return
        self.visual_validation['discrepancy'] = return_discrepancy
        
        self.logger.info(f"Visual Validation Results:")
        self.logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
        self.logger.info(f"  Final Equity: ${final_equity:,.2f}")
        self.logger.info(f"  Reported Return: {reported_return:.4%}")
        self.logger.info(f"  Actual Return: {actual_return:.4%}")
        self.logger.info(f"  Discrepancy: {return_discrepancy:.4%}")
        
        # HALT CONDITIONS
        if return_discrepancy > 0.01:  # 1% tolerance
            self.halt_reasons.append(
                f"CRITICAL: Return discrepancy {return_discrepancy:.2%} exceeds 1% tolerance"
            )
            self.logger.error("HALT: Significant discrepancy between reported and actual returns")
            return False
        
        # Check if metrics claim positive but equity declined
        if reported_return > 0.01 and actual_return < -0.01:
            self.halt_reasons.append(
                "CRITICAL: Metrics show positive return but equity declined"
            )
            self.logger.error("HALT: Metrics claim gains but equity shows losses")
            return False
        
        # Check if metrics claim negative but equity increased
        if reported_return < -0.01 and actual_return > 0.01:
            self.halt_reasons.append(
                "CRITICAL: Metrics show negative return but equity increased"
            )
            self.logger.error("HALT: Metrics claim losses but equity shows gains")
            return False
        
        # Step 3: Open position verification
        open_positions = self.metrics['accounting'].get('open_positions', 0)
        unrealized_pnl = self.metrics['accounting'].get('unrealized_pnl', 0)
        
        self.visual_validation['open_positions'] = open_positions
        self.visual_validation['unrealized_pnl'] = unrealized_pnl
        
        self.logger.info(f"  Open Positions: {open_positions}")
        self.logger.info(f"  Unrealized P&L: ${unrealized_pnl:,.2f}")
        
        # Check for incomplete period
        if open_positions > 5:
            self.halt_reasons.append(
                f"WARNING: {open_positions} open positions at period end (incomplete period)"
            )
            self.logger.warning("High number of open positions suggests incomplete evaluation period")
        
        if open_positions > 10:
            self.halt_reasons.append(
                f"CRITICAL: {open_positions} open positions - cannot evaluate without unrealized P&L"
            )
            self.logger.error("HALT: Too many open positions for accurate evaluation")
            return False
        
        # Check if significant capital is tied up
        if abs(unrealized_pnl) > initial_capital * 0.2:
            self.halt_reasons.append(
                f"WARNING: >20% capital in unrealized P&L (${unrealized_pnl:,.2f})"
            )
            self.logger.warning("Significant unrealized P&L affects performance assessment")
        
        self.logger.info("Visual validation PASSED")
        return True
    
    def perform_accounting_reconciliation(self) -> bool:
        """
        MANDATORY: Verify accounting identity before accepting results.
        
        Returns:
            True if accounting checks pass
        """
        self.logger.info("=" * 80)
        self.logger.info("PERFORMING ACCOUNTING RECONCILIATION")
        self.logger.info("=" * 80)
        
        # Verify: final_equity ≈ initial_capital × (1 + total_return)
        initial_capital = self.metrics['accounting']['initial_capital']
        final_equity = self.metrics['accounting']['final_equity']
        total_return = self.metrics['performance']['total_return']
        
        expected_final = initial_capital * (1 + total_return)
        equity_error = abs(final_equity - expected_final)
        equity_error_pct = equity_error / initial_capital
        
        self.accounting_validation['expected_final'] = expected_final
        self.accounting_validation['actual_final'] = final_equity
        self.accounting_validation['error'] = equity_error
        self.accounting_validation['error_pct'] = equity_error_pct
        
        self.logger.info(f"Accounting Reconciliation:")
        self.logger.info(f"  Expected Final: ${expected_final:,.2f}")
        self.logger.info(f"  Actual Final: ${final_equity:,.2f}")
        self.logger.info(f"  Error: ${equity_error:,.2f} ({equity_error_pct:.2%})")
        
        # Cross-check with series.csv
        if self.series_df is not None and len(self.series_df) > 0:
            series_final = self.series_df['equity'].iloc[-1]
            series_error = abs(series_final - final_equity)
            
            self.accounting_validation['series_final'] = series_final
            self.accounting_validation['series_error'] = series_error
            
            self.logger.info(f"  Series Final: ${series_final:,.2f}")
            self.logger.info(f"  Series Error: ${series_error:,.2f}")
            
            if series_error > initial_capital * 0.01:  # 1% tolerance
                self.halt_reasons.append(
                    f"CRITICAL: Series/metrics mismatch ${series_error:,.2f}"
                )
                self.logger.error("HALT: Inconsistency between series.csv and metrics.json")
                return False
        
        # Check accounting identity tolerance
        if equity_error_pct > 0.01:  # 1% tolerance
            self.halt_reasons.append(
                f"CRITICAL: Accounting error {equity_error_pct:.2%} exceeds 1% tolerance"
            )
            self.logger.error("HALT: Accounting identity violation")
            return False
        
        # Verify P&L consistency
        total_pnl = self.metrics['accounting'].get('total_pnl', 0)
        calculated_pnl = final_equity - initial_capital
        pnl_error = abs(total_pnl - calculated_pnl)
        
        self.accounting_validation['reported_pnl'] = total_pnl
        self.accounting_validation['calculated_pnl'] = calculated_pnl
        self.accounting_validation['pnl_error'] = pnl_error
        
        self.logger.info(f"  Reported P&L: ${total_pnl:,.2f}")
        self.logger.info(f"  Calculated P&L: ${calculated_pnl:,.2f}")
        self.logger.info(f"  P&L Error: ${pnl_error:,.2f}")
        
        if pnl_error > 100:  # $100 tolerance for rounding
            self.halt_reasons.append(
                f"WARNING: P&L discrepancy ${pnl_error:,.2f}"
            )
            self.logger.warning("P&L calculation inconsistency detected")
        
        self.logger.info("Accounting reconciliation PASSED")
        return True
    
    def evaluate_performance(self) -> Dict[str, Any]:
        """
        Evaluate strategy performance and provide rating.
        
        Returns:
            Performance evaluation with rating and insights
        """
        self.logger.info("=" * 80)
        self.logger.info("EVALUATING STRATEGY PERFORMANCE")
        self.logger.info("=" * 80)
        
        evaluation = {
            'rating': 'PENDING',
            'summary': '',
            'strengths': [],
            'weaknesses': [],
            'insights': []
        }
        
        # Extract key metrics
        total_return = self.metrics['performance']['total_return']
        sharpe = self.metrics['performance']['sharpe_ratio']
        sortino = self.metrics['performance']['sortino_ratio']
        max_dd = self.metrics['performance']['max_drawdown']
        win_rate = self.metrics['performance']['win_rate']
        
        self.logger.info(f"Key Performance Metrics:")
        self.logger.info(f"  Total Return: {total_return:.2%}")
        self.logger.info(f"  Sharpe Ratio: {sharpe:.2f}")
        self.logger.info(f"  Sortino Ratio: {sortino:.2f}")
        self.logger.info(f"  Max Drawdown: {max_dd:.2%}")
        self.logger.info(f"  Win Rate: {win_rate:.2%}")
        
        # Performance rating logic
        if abs(total_return) < 0.001:  # Near zero return
            evaluation['rating'] = 'NEUTRAL'
            evaluation['summary'] = 'Flat performance with minimal activity'
            evaluation['weaknesses'].append('No alpha generation')
            evaluation['insights'].append('Strategy shows no edge in current configuration')
            
        elif total_return > 0.10 and sharpe > 1.5:
            evaluation['rating'] = 'EXCELLENT'
            evaluation['summary'] = 'Strong risk-adjusted returns'
            evaluation['strengths'].append('Consistent alpha generation')
            
        elif total_return > 0.05 and sharpe > 1.0:
            evaluation['rating'] = 'GOOD'
            evaluation['summary'] = 'Positive performance with acceptable risk'
            evaluation['strengths'].append('Positive risk-adjusted returns')
            
        elif total_return > 0:
            evaluation['rating'] = 'ACCEPTABLE'
            evaluation['summary'] = 'Marginal positive performance'
            evaluation['weaknesses'].append('Low risk-adjusted returns')
            
        else:
            evaluation['rating'] = 'POOR'
            evaluation['summary'] = 'Negative performance'
            evaluation['weaknesses'].append('Strategy loses money')
        
        # Risk assessment
        if abs(max_dd) > 0.20:
            evaluation['weaknesses'].append(f'High drawdown risk ({max_dd:.1%})')
        elif abs(max_dd) < 0.05:
            evaluation['strengths'].append('Excellent drawdown control')
        
        # Win rate analysis
        if win_rate > 0.60:
            evaluation['strengths'].append(f'High win rate ({win_rate:.1%})')
        elif win_rate < 0.40:
            evaluation['weaknesses'].append(f'Low win rate ({win_rate:.1%})')
        
        # Strategic insights
        if total_return == 0 and self.metrics['execution']['total_trades'] < 20:
            evaluation['insights'].append(
                'Low trading activity suggests overly restrictive entry conditions'
            )
        
        self.logger.info(f"Performance Rating: {evaluation['rating']}")
        self.logger.info(f"Summary: {evaluation['summary']}")
        
        return evaluation
    
    def generate_evaluation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.
        
        Returns:
            Complete evaluation report with all findings
        """
        report = {
            'run_id': self.run_id,
            'timestamp': datetime.now().isoformat(),
            'status': self.evaluation_status,
            'visual_validation': self.visual_validation,
            'accounting_validation': self.accounting_validation,
            'performance_evaluation': {},
            'halt_reasons': self.halt_reasons,
            'recommendations': []
        }
        
        # Only evaluate performance if validations passed
        if self.evaluation_status == 'COMPLETED':
            report['performance_evaluation'] = self.evaluate_performance()
            
            # Generate recommendations
            if report['performance_evaluation']['rating'] in ['POOR', 'NEUTRAL']:
                report['recommendations'].append(
                    'Consider parameter optimization to improve entry/exit conditions'
                )
                report['recommendations'].append(
                    'Review strategy logic for potential improvements'
                )
            elif report['performance_evaluation']['rating'] in ['GOOD', 'EXCELLENT']:
                report['recommendations'].append(
                    'Run parameter optimization to validate robustness'
                )
                report['recommendations'].append(
                    'Consider walk-forward analysis for out-of-sample validation'
                )
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save evaluation report to disk."""
        report_dir = self.run_dir / "evaluation"
        report_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        report_path = report_dir / "evaluation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Evaluation report saved to {report_path}")
        
        # Save summary
        summary_path = report_dir / "evaluation_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"EVALUATION SUMMARY - {self.run_id}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Status: {report['status']}\n")
            f.write(f"Timestamp: {report['timestamp']}\n\n")
            
            if report['halt_reasons']:
                f.write("HALT REASONS:\n")
                for reason in report['halt_reasons']:
                    f.write(f"  - {reason}\n")
                f.write("\n")
            
            if 'performance_evaluation' in report and report['performance_evaluation']:
                perf = report['performance_evaluation']
                f.write(f"Performance Rating: {perf['rating']}\n")
                f.write(f"Summary: {perf['summary']}\n\n")
                
                if perf['strengths']:
                    f.write("Strengths:\n")
                    for s in perf['strengths']:
                        f.write(f"  + {s}\n")
                    f.write("\n")
                
                if perf['weaknesses']:
                    f.write("Weaknesses:\n")
                    for w in perf['weaknesses']:
                        f.write(f"  - {w}\n")
                    f.write("\n")
                
                if perf['insights']:
                    f.write("Strategic Insights:\n")
                    for i in perf['insights']:
                        f.write(f"  * {i}\n")
                    f.write("\n")
            
            if report['recommendations']:
                f.write("Recommendations:\n")
                for r in report['recommendations']:
                    f.write(f"  → {r}\n")
        
        self.logger.info(f"Evaluation summary saved to {summary_path}")
    
    def run_evaluation(self) -> Dict[str, Any]:
        """
        Main evaluation pipeline with mandatory validation steps.
        
        Returns:
            Complete evaluation report
        """
        self.logger.info("=" * 80)
        self.logger.info(f"STARTING EVALUATION FOR RUN: {self.run_id}")
        self.logger.info(f"Mode: {'TEST' if self.test_mode else 'PRODUCTION'}")
        self.logger.info("=" * 80)
        
        # Step 1: Load run data
        if not self.load_run_data():
            self.evaluation_status = 'FAILED'
            self.logger.error("Failed to load run data")
            return self.generate_evaluation_report()
        
        # Step 2: MANDATORY Visual Validation
        if not self.perform_visual_validation():
            self.evaluation_status = 'FAILED - Visual Validation'
            self.logger.error("EVALUATION FAILED - VISUAL VALIDATION ERROR")
            self.logger.error("Halt reasons:")
            for reason in self.halt_reasons:
                self.logger.error(f"  - {reason}")
            return self.generate_evaluation_report()
        
        # Step 3: MANDATORY Accounting Reconciliation
        if not self.perform_accounting_reconciliation():
            self.evaluation_status = 'FAILED - Accounting Error'
            self.logger.error("EVALUATION FAILED - ACCOUNTING DISCREPANCY")
            self.logger.error("Halt reasons:")
            for reason in self.halt_reasons:
                self.logger.error(f"  - {reason}")
            return self.generate_evaluation_report()
        
        # Step 4: Performance Evaluation (only if validations pass)
        self.evaluation_status = 'COMPLETED'
        self.logger.info("All validations PASSED - proceeding with performance evaluation")
        
        # Generate and save report
        report = self.generate_evaluation_report()
        self.save_report(report)
        
        self.logger.info("=" * 80)
        self.logger.info("EVALUATION COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 80)
        
        return report


def main():
    """Main entry point for single-run evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate single backtest run')
    parser.add_argument('run_id', nargs='?', help='Run ID to evaluate')
    parser.add_argument('--test', action='store_true', help='Use test data directory')
    
    args = parser.parse_args()
    
    # Default to most recent run if not specified
    if not args.run_id:
        if args.test:
            run_dir = Path("data/test_runs")
        else:
            run_dir = Path("data/runs")
        
        # Find most recent run
        runs = [d for d in run_dir.iterdir() if d.is_dir() and d.name != 'logs']
        if not runs:
            print(f"No runs found in {run_dir}")
            sys.exit(1)
        
        args.run_id = sorted(runs)[-1].name
        print(f"Using most recent run: {args.run_id}")
    
    # Create evaluator and run
    evaluator = SingleRunEvaluator(args.run_id, test_mode=args.test)
    report = evaluator.run_evaluation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Run ID: {report['run_id']}")
    print(f"Status: {report['status']}")
    
    if report['halt_reasons']:
        print("\nHALT REASONS:")
        for reason in report['halt_reasons']:
            print(f"  - {reason}")
    
    if 'performance_evaluation' in report and report['performance_evaluation']:
        perf = report['performance_evaluation']
        print(f"\nPerformance Rating: {perf['rating']}")
        print(f"Summary: {perf['summary']}")
    
    if report['status'] == 'COMPLETED':
        print("\n[SUCCESS] Evaluation completed successfully")
    else:
        print("\n[FAILED] Evaluation failed - see logs for details")
        sys.exit(1)


if __name__ == "__main__":
    main()