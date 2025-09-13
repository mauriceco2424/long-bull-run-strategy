"""
Optimization Evaluation Script

Evaluates optimization results, performs strategic interpretation,
and generates comprehensive reports for optimization studies.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


class OptimizationEvaluator:
    """
    Evaluates parameter optimization results and generates reports.

    Key Responsibilities:
    - Assess parameter significance and robustness
    - Detect overfitting and data-snooping bias
    - Strategic interpretation of optimal parameters
    - Generate comprehensive evaluation reports
    """

    def __init__(self, study_path: str):
        """Initialize evaluator with optimization study path."""
        self.study_path = Path(study_path)
        self.summary = None
        self.parameter_sweep = None
        self.walkforward_results = None

        # Load optimization results
        self._load_results()

    def _load_results(self):
        """Load optimization study results."""
        # Load summary
        summary_file = self.study_path / "optimization_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                self.summary = json.load(f)

        # Load parameter sweep
        sweep_file = self.study_path / "parameter_sweep.csv"
        if sweep_file.exists():
            self.parameter_sweep = pd.read_csv(sweep_file)

        # Load walk-forward results if available
        wf_file = self.study_path / "walkforward_results.json"
        if wf_file.exists():
            with open(wf_file, 'r') as f:
                self.walkforward_results = json.load(f)

    def evaluate(self) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation of optimization results.

        Returns:
            Evaluation report with strategic insights and recommendations
        """
        print("="*60)
        print("OPTIMIZATION EVALUATION REPORT")
        print("="*60)

        if not self.summary:
            print("ERROR: No optimization results found")
            return {}

        print(f"\nStudy: {self.summary.get('study_name', 'Unknown')}")
        print(f"Timestamp: {self.summary.get('timestamp', 'Unknown')}")
        print(f"Combinations Tested: {self.summary.get('total_combinations', 0)}")

        # Evaluate best parameters
        best_params = self.summary.get('best_parameters', {})
        best_performance = self.summary.get('best_performance', {})

        print("\n" + "="*60)
        print("BEST PARAMETER SET")
        print("="*60)
        for param, value in best_params.items():
            print(f"  {param}: {value}")

        print("\nPerformance Metrics:")
        for metric, value in best_performance.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.4f}")
            else:
                print(f"  {metric}: {value}")

        # Parameter significance evaluation
        significance_report = self._evaluate_parameter_significance()

        # Overfitting assessment
        overfitting_report = self._assess_overfitting()

        # Robustness analysis
        robustness_report = self._analyze_robustness()

        # Strategic interpretation
        strategic_insights = self._generate_strategic_insights()

        # Generate recommendations
        recommendations = self._generate_recommendations(
            significance_report,
            overfitting_report,
            robustness_report
        )

        # Compile evaluation report
        evaluation_report = {
            'study_id': self.study_path.name,
            'evaluation_timestamp': datetime.now().isoformat(),
            'best_parameters': best_params,
            'best_performance': best_performance,
            'parameter_significance': significance_report,
            'overfitting_assessment': overfitting_report,
            'robustness_analysis': robustness_report,
            'strategic_insights': strategic_insights,
            'recommendations': recommendations
        }

        # Save evaluation report
        self._save_evaluation_report(evaluation_report)

        return evaluation_report

    def _evaluate_parameter_significance(self) -> Dict[str, Any]:
        """Evaluate statistical significance of parameters."""
        print("\n" + "="*60)
        print("PARAMETER SIGNIFICANCE ANALYSIS")
        print("="*60)

        if self.parameter_sweep is None or len(self.parameter_sweep) < 10:
            print("  Insufficient data for significance analysis")
            return {'error': 'Insufficient data'}

        significance_results = {}

        # Get parameter columns (exclude metrics)
        param_cols = [col for col in self.parameter_sweep.columns
                     if not col.startswith(('total_', 'sharpe_', 'max_', 'win_'))]

        # Primary metric for evaluation
        primary_metric = 'sharpe_ratio'
        if primary_metric not in self.parameter_sweep.columns:
            primary_metric = 'total_return'

        print(f"\nParameter Correlations with {primary_metric}:")
        for param in param_cols:
            if param in self.parameter_sweep.columns:
                correlation = self.parameter_sweep[param].corr(
                    self.parameter_sweep[primary_metric]
                )

                # Simple significance test
                n = len(self.parameter_sweep)
                from scipy import stats
                t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

                significance_results[param] = {
                    'correlation': correlation,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }

                sig_marker = "*" if p_value < 0.05 else ""
                print(f"  {param}: {correlation:.3f} (p={p_value:.3f}){sig_marker}")

        return significance_results

    def _assess_overfitting(self) -> Dict[str, Any]:
        """Assess overfitting risk in optimization results."""
        print("\n" + "="*60)
        print("OVERFITTING ASSESSMENT")
        print("="*60)

        overfitting_indicators = self.summary.get('overfitting_indicators', {})

        # Check various overfitting indicators
        risk_factors = []
        risk_level = "LOW"

        # 1. Parameter count check
        num_params = overfitting_indicators.get('num_parameters', 0)
        if num_params > 5:
            risk_factors.append("High parameter count")
            risk_level = "HIGH"
        print(f"  Parameter Count: {num_params} ({'HIGH RISK' if num_params > 5 else 'OK'})")

        # 2. Sample size check
        avg_trades = overfitting_indicators.get('avg_trades', 0)
        if avg_trades < 30:
            risk_factors.append("Low trade count")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        print(f"  Avg Trades: {avg_trades:.0f} ({'LOW RISK' if avg_trades < 30 else 'OK'})")

        # 3. Walk-forward degradation
        avg_degradation = overfitting_indicators.get('avg_degradation', 0)
        if avg_degradation > 20:
            risk_factors.append("High validation degradation")
            risk_level = "HIGH"
        elif avg_degradation > 15:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        print(f"  WF Degradation: {avg_degradation:.1f}% ({'HIGH RISK' if avg_degradation > 20 else 'OK'})")

        # 4. Parameter stability
        param_stability = overfitting_indicators.get('parameter_stability', {})
        unstable_params = [p for p, s in param_stability.items() if s > 0.5]
        if len(unstable_params) > 0:
            risk_factors.append(f"Unstable parameters: {', '.join(unstable_params)}")
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        print(f"\n  Overall Overfitting Risk: {risk_level}")
        if risk_factors:
            print("  Risk Factors:")
            for factor in risk_factors:
                print(f"    - {factor}")

        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'indicators': overfitting_indicators
        }

    def _analyze_robustness(self) -> Dict[str, Any]:
        """Analyze parameter robustness and stability."""
        print("\n" + "="*60)
        print("ROBUSTNESS ANALYSIS")
        print("="*60)

        if self.parameter_sweep is None or len(self.parameter_sweep) < 10:
            print("  Insufficient data for robustness analysis")
            return {'error': 'Insufficient data'}

        robustness_metrics = {}

        # Get top 10% of results
        primary_metric = 'sharpe_ratio'
        if primary_metric not in self.parameter_sweep.columns:
            primary_metric = 'total_return'

        top_pct = 0.1
        top_n = max(1, int(len(self.parameter_sweep) * top_pct))
        top_results = self.parameter_sweep.nlargest(top_n, primary_metric)

        # Check parameter clustering in top results
        param_cols = [col for col in self.parameter_sweep.columns
                     if not col.startswith(('total_', 'sharpe_', 'max_', 'win_'))]

        print("\nParameter Distribution in Top 10% Results:")
        for param in param_cols:
            if param in top_results.columns:
                param_std = top_results[param].std()
                param_mean = top_results[param].mean()
                param_cv = param_std / param_mean if param_mean != 0 else float('inf')

                robustness_metrics[param] = {
                    'mean_in_top': param_mean,
                    'std_in_top': param_std,
                    'coefficient_of_variation': param_cv,
                    'robust': param_cv < 0.2
                }

                print(f"  {param}:")
                print(f"    Mean: {param_mean:.2f}")
                print(f"    Std: {param_std:.2f}")
                print(f"    CV: {param_cv:.3f} ({'ROBUST' if param_cv < 0.2 else 'SENSITIVE'})")

        # Performance consistency check
        perf_std = top_results[primary_metric].std()
        perf_mean = top_results[primary_metric].mean()
        perf_consistency = 1 - (perf_std / perf_mean) if perf_mean != 0 else 0

        print(f"\nPerformance Consistency in Top Results: {perf_consistency:.2%}")

        return {
            'parameter_metrics': robustness_metrics,
            'performance_consistency': perf_consistency,
            'robust_parameters': [p for p, m in robustness_metrics.items() if m['robust']]
        }

    def _generate_strategic_insights(self) -> Dict[str, Any]:
        """Generate strategic insights from optimization results."""
        print("\n" + "="*60)
        print("STRATEGIC INSIGHTS")
        print("="*60)

        insights = {
            'parameter_interpretation': {},
            'strategy_characteristics': [],
            'market_conditions': []
        }

        best_params = self.summary.get('best_parameters', {})

        # RSI period interpretation
        if 'rsi_period' in best_params:
            rsi = best_params['rsi_period']
            if rsi <= 10:
                interpretation = "Very short-term momentum focus, high-frequency trading"
                insights['strategy_characteristics'].append("High-frequency")
            elif rsi <= 14:
                interpretation = "Standard momentum period, balanced approach"
                insights['strategy_characteristics'].append("Balanced")
            else:
                interpretation = "Longer-term momentum, fewer but higher quality signals"
                insights['strategy_characteristics'].append("Selective")

            insights['parameter_interpretation']['rsi_period'] = interpretation
            print(f"\nRSI Period ({rsi}): {interpretation}")

        # Threshold interpretation
        if 'oversold_threshold' in best_params:
            oversold = best_params['oversold_threshold']
            if oversold < 30:
                interpretation = "Aggressive entry, more opportunities but higher risk"
                insights['strategy_characteristics'].append("Aggressive entries")
            else:
                interpretation = "Conservative entry, waiting for stronger oversold conditions"
                insights['strategy_characteristics'].append("Conservative entries")

            insights['parameter_interpretation']['oversold_threshold'] = interpretation
            print(f"Oversold Threshold ({oversold}): {interpretation}")

        if 'overbought_threshold' in best_params:
            overbought = best_params['overbought_threshold']
            if overbought > 70:
                interpretation = "Patient exits, holding for stronger trends"
                insights['strategy_characteristics'].append("Trend-following exits")
            else:
                interpretation = "Quick exits, capturing shorter moves"
                insights['strategy_characteristics'].append("Mean-reversion exits")

            insights['parameter_interpretation']['overbought_threshold'] = interpretation
            print(f"Overbought Threshold ({overbought}): {interpretation}")

        # Overall strategy profile
        print("\nStrategy Profile:")
        for characteristic in insights['strategy_characteristics']:
            print(f"  - {characteristic}")

        return insights

    def _generate_recommendations(self, significance: Dict, overfitting: Dict,
                                  robustness: Dict) -> Dict[str, Any]:
        """Generate actionable recommendations based on evaluation."""
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)

        recommendations = {
            'deployment_readiness': 'NOT_READY',
            'action_items': [],
            'parameter_adjustments': [],
            'risk_warnings': []
        }

        # Check deployment readiness
        ready_criteria = []
        not_ready_criteria = []

        # Overfitting check
        if overfitting.get('risk_level') == 'LOW':
            ready_criteria.append("Low overfitting risk")
        elif overfitting.get('risk_level') == 'HIGH':
            not_ready_criteria.append("High overfitting risk detected")
            recommendations['action_items'].append("Reduce parameter complexity")
            recommendations['risk_warnings'].append("Strategy may not perform well out-of-sample")

        # Robustness check
        robust_params = robustness.get('robust_parameters', [])
        if len(robust_params) > 0:
            ready_criteria.append(f"{len(robust_params)} robust parameters")
        else:
            not_ready_criteria.append("No robust parameters found")
            recommendations['action_items'].append("Expand parameter search ranges")

        # Performance check
        best_performance = self.summary.get('best_performance', {})
        sharpe = best_performance.get('sharpe_ratio', 0)
        if sharpe > 1.0:
            ready_criteria.append(f"Strong Sharpe ratio: {sharpe:.2f}")
        elif sharpe < 0.5:
            not_ready_criteria.append(f"Weak Sharpe ratio: {sharpe:.2f}")
            recommendations['action_items'].append("Consider alternative strategy approaches")

        # Determine overall readiness
        if len(not_ready_criteria) == 0 and len(ready_criteria) >= 2:
            recommendations['deployment_readiness'] = 'READY'
            print("\nDeployment Status: READY FOR LIVE TESTING")
        elif len(not_ready_criteria) <= 1:
            recommendations['deployment_readiness'] = 'CONDITIONAL'
            print("\nDeployment Status: CONDITIONAL - ADDRESS CONCERNS")
        else:
            print("\nDeployment Status: NOT READY")

        print("\nPositive Factors:")
        for criteria in ready_criteria:
            print(f"  + {criteria}")

        if not_ready_criteria:
            print("\nConcerns:")
            for criteria in not_ready_criteria:
                print(f"  - {criteria}")

        if recommendations['action_items']:
            print("\nAction Items:")
            for i, item in enumerate(recommendations['action_items'], 1):
                print(f"  {i}. {item}")

        return recommendations

    def _save_evaluation_report(self, report: Dict[str, Any]):
        """Save evaluation report to file."""
        report_file = self.study_path / "evaluation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n" + "="*60)
        print("REPORT SAVED")
        print("="*60)
        print(f"Evaluation report saved to: {report_file}")

    def generate_summary_table(self) -> pd.DataFrame:
        """Generate summary table of optimization results."""
        if self.parameter_sweep is None:
            return pd.DataFrame()

        # Get top 10 results
        primary_metric = 'sharpe_ratio'
        if primary_metric not in self.parameter_sweep.columns:
            primary_metric = 'total_return'

        top_10 = self.parameter_sweep.nlargest(10, primary_metric)

        # Format for display
        param_cols = [col for col in top_10.columns
                     if not col.startswith(('total_', 'sharpe_', 'max_', 'win_'))]

        display_cols = param_cols + [primary_metric, 'total_trades', 'max_drawdown']
        display_cols = [col for col in display_cols if col in top_10.columns]

        summary_table = top_10[display_cols].round(3)

        return summary_table


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate optimization study results')
    parser.add_argument('--study-path', default='data/optimization/test_study',
                       help='Path to optimization study directory')
    parser.add_argument('--show-table', action='store_true',
                       help='Display top results table')

    args = parser.parse_args()

    # Create evaluator
    evaluator = OptimizationEvaluator(args.study_path)

    # Run evaluation
    report = evaluator.evaluate()

    # Show summary table if requested
    if args.show_table:
        print("\n" + "="*60)
        print("TOP 10 PARAMETER COMBINATIONS")
        print("="*60)
        summary_table = evaluator.generate_summary_table()
        if not summary_table.empty:
            print(summary_table.to_string())

    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)

    return report


if __name__ == "__main__":
    main()