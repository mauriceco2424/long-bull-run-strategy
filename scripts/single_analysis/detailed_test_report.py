#!/usr/bin/env python3
"""
Detailed Test Report Generator for Enhanced Single-Run Analysis

This script generates a comprehensive report showing all validation results,
cross-validation matrices, and quality checks from the enhanced analyzer.
"""

import sys
import os
import json
from datetime import datetime
import pandas as pd

# Add the engine directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'engine'))

try:
    from analyze_test_run import EnhancedSingleRunAnalyzer
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    from analyze_test_run import EnhancedSingleRunAnalyzer

def generate_detailed_report():
    """Generate and display a detailed test report."""
    
    print("="*80)
    print("ENHANCED SINGLE-RUN ANALYZER - DETAILED TEST REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the analysis
    analyzer = EnhancedSingleRunAnalyzer()
    results = analyzer.run_test_analysis("test_config.json")
    
    print("\n" + "="*80)
    print("1. ANALYSIS METADATA")
    print("="*80)
    
    metadata = results.get('analysis_metadata', {})
    print(f"Run ID: {metadata.get('run_id', 'N/A')}")
    print(f"Analysis Version: {metadata.get('analysis_version', 'N/A')}")
    print(f"Processing Time: {metadata.get('processing_time_seconds', 0):.2f} seconds")
    print(f"Analysis Timestamp: {metadata.get('analysis_timestamp', 'N/A')}")
    
    print("\n" + "="*80)
    print("2. ENHANCED DATA VALIDATION RESULTS")
    print("="*80)
    
    validation = results.get('validation_results', {})
    
    # Data Quality
    print("\n2.1 DATA QUALITY METRICS:")
    data_quality = validation.get('data_quality', {})
    for metric, value in data_quality.items():
        print(f"  {metric.replace('_', ' ').title()}: {value}")
    
    # Timestamp Validation
    print("\n2.2 TIMESTAMP VALIDATION:")
    timestamp_val = validation.get('timestamp_validation', {})
    for check, result in timestamp_val.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {check.replace('_', ' ').title()}: {result}")
    
    # Accounting Checks
    print("\n2.3 ACCOUNTING IDENTITY CHECKS:")
    accounting = validation.get('accounting_checks', {})
    print(f"  Initial Capital: ${accounting.get('initial_capital', 0):,.2f}")
    print(f"  Final Equity: ${accounting.get('final_equity', 0):,.2f}")
    print(f"  Cash: ${accounting.get('cash', 0):,.2f}")
    print(f"  Positions Value: ${accounting.get('positions_value', 0):,.2f}")
    print(f"  Realized P&L: ${accounting.get('realized_pnl', 0):,.2f}")
    print(f"  Unrealized P&L: ${accounting.get('unrealized_pnl', 0):,.2f}")
    
    # Validation Issues
    warnings = validation.get('warnings', [])
    critical_issues = validation.get('critical_issues', [])
    
    if warnings:
        print("\n2.4 VALIDATION WARNINGS:")
        for warning in warnings:
            print(f"  [WARN] {warning}")
    
    if critical_issues:
        print("\n2.5 CRITICAL VALIDATION ISSUES:")
        for issue in critical_issues:
            print(f"  [CRITICAL] {issue}")
    
    print("\n" + "="*80)
    print("3. EQUITY RECONCILIATION & CROSS-VALIDATION MATRIX")
    print("="*80)
    
    reconciliation = results.get('reconciliation_results', {})
    
    # Actual Return Calculation
    print("\n3.1 ACTUAL RETURN CALCULATION:")
    actual_calc = reconciliation.get('actual_return_calculation', {})
    print(f"  Initial Capital: ${actual_calc.get('initial_capital', 0):,.2f}")
    print(f"  Final Equity (Reported): ${actual_calc.get('final_equity_reported', 0):,.2f}")
    print(f"  Unrealized P&L: ${actual_calc.get('unrealized_pnl', 0):,.2f}")
    print(f"  Adjusted Final Equity: ${actual_calc.get('adjusted_final_equity', 0):,.2f}")
    print(f"  Actual Return: {actual_calc.get('actual_return', 0):.6f}")
    print(f"  Actual Return %: {actual_calc.get('actual_return_pct', 0):.2f}%")
    
    # Cross-Validation Matrix
    print("\n3.2 CROSS-VALIDATION MATRIX:")
    cross_val = reconciliation.get('cross_validation_matrix', {})
    print(f"  Series CSV Final Equity: ${cross_val.get('series_csv_final_equity', 0):,.2f}")
    print(f"  Portfolio State Final Equity: ${cross_val.get('portfolio_state_final_equity', 0):,.2f}")
    print(f"  Visual Equity Trend: {cross_val.get('visual_equity_trend', 'N/A')}")
    
    trend_match = cross_val.get('return_direction_match', False)
    print(f"  Return Direction Match: {'[PASS]' if trend_match else '[FAIL]'} {trend_match}")
    
    # Discrepancies
    discrepancies = reconciliation.get('discrepancies', [])
    if discrepancies:
        print("\n3.3 RECONCILIATION DISCREPANCIES:")
        for disc in discrepancies:
            print(f"  [DISCREPANCY] {disc}")
    else:
        print("\n3.3 RECONCILIATION STATUS: [PASS] No discrepancies detected")
    
    print("\n" + "="*80)
    print("4. OPEN POSITION ANALYSIS & MARK-TO-MARKET")
    print("="*80)
    
    positions = results.get('position_results', {})
    print(f"  Open Positions Count: {positions.get('open_positions_count', 0)}")
    print(f"  Total Unrealized P&L: ${positions.get('unrealized_pnl_total', 0):,.2f}")
    
    # Mark-to-Market Details
    mtm = positions.get('mark_to_market', {})
    if mtm:
        print(f"  Positions Value at Close: ${mtm.get('positions_value_at_close', 0):,.2f}")
        print(f"  Mark-to-Market Applied: {mtm.get('mark_to_market_applied', False)}")
    
    # Position Warnings
    pos_warnings = positions.get('warnings', [])
    if pos_warnings:
        print("\n4.1 POSITION WARNINGS:")
        for warning in pos_warnings:
            print(f"  [WARN] {warning}")
    else:
        print("\n4.1 POSITION STATUS: [PASS] No open positions detected")
    
    print("\n" + "="*80)
    print("5. COMPREHENSIVE PERFORMANCE METRICS")
    print("="*80)
    
    artifacts = results.get('artifacts', {})
    metrics = artifacts.get('metrics', {})
    
    print("\n5.1 RISK-ADJUSTED RETURNS:")
    print(f"  CAGR: {metrics.get('cagr', 0):.2%}")
    print(f"  Sharpe Ratio: {metrics.get('sharpe', 0):.4f}")
    print(f"  Sortino Ratio: {metrics.get('sortino', 0):.4f}")
    
    print("\n5.2 RISK METRICS:")
    print(f"  Maximum Drawdown: {metrics.get('max_dd', 0):.2%}")
    print(f"  Exposure: {metrics.get('exposure', 0):.2%}")
    
    print("\n5.3 TRADING METRICS:")
    print(f"  Total Trades: {metrics.get('n_trades', 0)}")
    print(f"  Win Rate: {metrics.get('win_rate', 0):.1%}")
    print(f"  Average Gain: {metrics.get('avg_gain', 0):.2%}")
    print(f"  Average Loss: {metrics.get('avg_loss', 0):.2%}")
    print(f"  Average Trade Duration: {metrics.get('avg_trade_dur_days', 0):.1f} days")
    print(f"  Average Monitor Duration: {metrics.get('avg_monitor_dur_days', 0):.1f} days")
    
    print("\n5.4 POSITION METRICS:")
    print(f"  Open Positions: {metrics.get('open_positions', 0)}")
    print(f"  Unrealized P&L: ${metrics.get('unrealized_pnl', 0):,.2f}")
    
    print("\n" + "="*80)
    print("6. PROFESSIONAL VISUALIZATION RESULTS")
    print("="*80)
    
    viz_results = results.get('visualization_results', {})
    print(f"  Visualization Quality: {viz_results.get('visualization_quality', 'N/A')}")
    print(f"  Figures Created: {len(viz_results.get('figures_created', []))}")
    
    figures = viz_results.get('figures_created', [])
    if figures:
        for fig in figures:
            print(f"    - {fig}")
    
    formats = viz_results.get('formats_generated', [])
    print(f"  Output Formats: {', '.join(formats) if formats else 'None'}")
    
    viz_errors = viz_results.get('errors', [])
    if viz_errors:
        print("\n6.1 VISUALIZATION ERRORS:")
        for error in viz_errors:
            print(f"  [ERROR] {error}")
    
    print("\n" + "="*80)
    print("7. FINAL QUALITY GATE ASSESSMENT")
    print("="*80)
    
    quality_gate = results.get('overall_status', {})
    status = quality_gate.get('status', 'unknown')
    
    print(f"  Overall Status: {status.upper()}")
    
    gate_warnings = quality_gate.get('warnings', [])
    if gate_warnings:
        print(f"\n7.1 QUALITY GATE WARNINGS ({len(gate_warnings)}):")
        for i, warning in enumerate(gate_warnings, 1):
            print(f"    {i}. {warning}")
    
    gate_issues = quality_gate.get('critical_issues', [])
    if gate_issues:
        print(f"\n7.2 CRITICAL QUALITY ISSUES ({len(gate_issues)}):")
        for i, issue in enumerate(gate_issues, 1):
            print(f"    {i}. [CRITICAL] {issue}")
    
    print("\n" + "="*80)
    print("8. TEST CONCLUSION & RECOMMENDATIONS")
    print("="*80)
    
    print("\n8.1 ENHANCED VALIDATION SYSTEM TEST RESULTS:")
    
    if status == 'passed':
        print("  [PASS] All mandatory quality checks completed successfully")
        print("  [PASS] Equity reconciliation validated")
        print("  [PASS] Cross-validation matrix checks passed")
        print("  [PASS] Professional visualizations generated")
    elif status == 'passed_with_warnings':
        print("  [WARN] Analysis passed with non-critical warnings")
        print("  [PASS] Core validation systems functioning correctly")
        print("  [INFO] Warnings are within acceptable thresholds")
    else:
        print("  [FAIL] Critical issues detected in validation")
        print("  [ACTION] Manual review required before registry update")
    
    print("\n8.2 PROCESSING EFFICIENCY:")
    processing_time = metadata.get('processing_time_seconds', 0)
    data_records = len(results.get('backtest_results', {}).get('daily_series', []))
    
    if processing_time > 0:
        records_per_second = data_records / processing_time
        print(f"  Processing Speed: {records_per_second:.1f} records/second")
        print(f"  Efficiency Rating: {'Excellent' if records_per_second > 100 else 'Good' if records_per_second > 50 else 'Acceptable'}")
    
    print("\n8.3 SYSTEM RECOMMENDATIONS:")
    
    if not gate_issues and not critical_issues:
        print("  [RECOMMENDATION] Enhanced validation system is functioning correctly")
        print("  [RECOMMENDATION] Ready for production deployment")
    
    if gate_warnings or warnings:
        print("  [RECOMMENDATION] Review warning conditions for future improvements")
        print("  [RECOMMENDATION] Consider threshold adjustments if warnings are frequent")
    
    if viz_errors:
        print("  [RECOMMENDATION] Address visualization errors for complete reporting")
    
    print("\n" + "="*80)
    print("END OF DETAILED TEST REPORT")
    print("="*80)
    
    return results

if __name__ == "__main__":
    generate_detailed_report()