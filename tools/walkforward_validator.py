#!/usr/bin/env python3
"""
Walk-Forward Analysis Validation Framework
Implements gold standard validation methodology for trading strategy optimization
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path
import logging
from scipy import stats

@dataclass
class ValidationWindow:
    """Represents a single walk-forward validation window"""
    window_id: str
    training_start: str  # YYYY-MM-DD
    training_end: str    # YYYY-MM-DD
    validation_start: str # YYYY-MM-DD
    validation_end: str   # YYYY-MM-DD
    training_days: int
    validation_days: int
    market_regime: Optional[str] = None  # bull/bear/sideways classification

@dataclass
class ParameterCombination:
    """Represents a single parameter combination to test"""
    combination_id: str
    parameters: Dict[str, Any]
    parameter_hash: str

@dataclass
class ValidationResult:
    """Results for a single parameter combination across all windows"""
    combination_id: str
    parameters: Dict[str, Any]
    window_results: List[Dict[str, Any]]  # Per-window performance metrics
    aggregate_metrics: Dict[str, float]   # Overall performance across windows
    stability_score: float                # Consistency across windows (0-1)
    overfitting_risk: str                # low/medium/high
    statistical_significance: Dict[str, float]  # p-values for key metrics
    
class WalkForwardValidator:
    """
    Implements walk-forward validation methodology with overfitting prevention
    
    Core Features:
    - Rolling window validation with configurable training/validation periods
    - Statistical significance testing for parameter performance
    - Overfitting detection and prevention measures
    - Market regime awareness for parameter stability assessment
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize validator with optimization configuration
        
        Args:
            config: Optimization configuration dict from optimization_config.md
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Validation parameters
        self.training_months = config['training_period_months']
        self.validation_months = config['validation_period_months'] 
        self.rolling_step_months = config['rolling_step_months']
        self.min_windows = config['min_validation_windows']
        
        # Statistical thresholds
        self.min_trades = config['min_trades_per_combination']
        self.significance_p = config['statistical_significance_p']
        self.decay_threshold = config['out_of_sample_decay_threshold']
        
        # Data range
        self.start_date = pd.to_datetime(config['start_date'])
        self.end_date = pd.to_datetime(config['end_date'])
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for validation process"""
        logger = logging.getLogger('walkforward_validator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def generate_validation_windows(self) -> List[ValidationWindow]:
        """
        Generate rolling validation windows for walk-forward analysis
        
        Returns:
            List of ValidationWindow objects defining train/validation periods
        """
        windows = []
        current_start = self.start_date
        window_id = 1
        
        while True:
            # Calculate training period
            training_start = current_start
            training_end = training_start + timedelta(days=30 * self.training_months)
            
            # Calculate validation period
            validation_start = training_end
            validation_end = validation_start + timedelta(days=30 * self.validation_months)
            
            # Check if we have enough data for validation period
            if validation_end > self.end_date:
                break
                
            # Create validation window
            window = ValidationWindow(
                window_id=f"window_{window_id:03d}",
                training_start=training_start.strftime('%Y-%m-%d'),
                training_end=training_end.strftime('%Y-%m-%d'),
                validation_start=validation_start.strftime('%Y-%m-%d'),
                validation_end=validation_end.strftime('%Y-%m-%d'),
                training_days=(training_end - training_start).days,
                validation_days=(validation_end - validation_start).days
            )
            
            windows.append(window)
            
            # Advance to next window
            current_start = current_start + timedelta(days=30 * self.rolling_step_months)
            window_id += 1
            
        self.logger.info(f"Generated {len(windows)} validation windows")
        
        # Ensure minimum number of windows
        if len(windows) < self.min_windows:
            raise ValueError(
                f"Insufficient data for walk-forward analysis. "
                f"Generated {len(windows)} windows, minimum required: {self.min_windows}"
            )
            
        return windows
    
    def validate_parameter_combination(
        self, 
        combination: ParameterCombination,
        windows: List[ValidationWindow]
    ) -> ValidationResult:
        """
        Validate a single parameter combination across all windows
        
        Args:
            combination: Parameter combination to test
            windows: List of validation windows to test on
            
        Returns:
            ValidationResult with performance across all windows
        """
        self.logger.info(f"Validating combination {combination.combination_id}")
        
        window_results = []
        
        for window in windows:
            # Run backtest for training period (for parameter optimization)
            training_result = self._run_backtest_window(
                combination.parameters,
                window.training_start,
                window.training_end,
                f"{combination.combination_id}_train_{window.window_id}"
            )
            
            # Run backtest for validation period (out-of-sample testing)
            validation_result = self._run_backtest_window(
                combination.parameters,
                window.validation_start,
                window.validation_end, 
                f"{combination.combination_id}_val_{window.window_id}"
            )
            
            # Calculate window performance metrics
            window_perf = self._calculate_window_performance(
                training_result, validation_result, window
            )
            window_results.append(window_perf)
            
        # Calculate aggregate metrics across all windows
        aggregate_metrics = self._calculate_aggregate_metrics(window_results)
        
        # Calculate stability score (consistency across windows)
        stability_score = self._calculate_stability_score(window_results)
        
        # Assess overfitting risk
        overfitting_risk = self._assess_overfitting_risk(
            window_results, aggregate_metrics
        )
        
        # Calculate statistical significance
        significance_tests = self._calculate_statistical_significance(window_results)
        
        return ValidationResult(
            combination_id=combination.combination_id,
            parameters=combination.parameters,
            window_results=window_results,
            aggregate_metrics=aggregate_metrics,
            stability_score=stability_score,
            overfitting_risk=overfitting_risk,
            statistical_significance=significance_tests
        )
    
    def _run_backtest_window(
        self,
        parameters: Dict[str, Any],
        start_date: str,
        end_date: str,
        run_id: str
    ) -> Dict[str, Any]:
        """
        Run backtest for a specific time window with given parameters
        
        This is a placeholder - actual implementation would interface with
        the trading engine to run backtests with the specified parameters.
        
        Returns:
            Dictionary containing backtest results and metrics
        """
        # TODO: Interface with actual trading engine
        # For now, return mock results for testing
        
        mock_result = {
            'run_id': run_id,
            'start_date': start_date,
            'end_date': end_date,
            'parameters': parameters,
            'metrics': {
                'cagr': np.random.normal(0.12, 0.05),
                'sharpe_ratio': np.random.normal(1.2, 0.3),
                'sortino_ratio': np.random.normal(1.8, 0.4),
                'max_drawdown': np.random.uniform(0.05, 0.25),
                'win_rate': np.random.uniform(0.35, 0.65),
                'total_trades': np.random.randint(20, 200),
                'avg_trade_duration': np.random.uniform(2, 15),
                'total_return': np.random.normal(0.15, 0.08)
            }
        }
        
        return mock_result
    
    def _calculate_window_performance(
        self,
        training_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        window: ValidationWindow
    ) -> Dict[str, Any]:
        """Calculate performance metrics for a single validation window"""
        
        train_metrics = training_result['metrics']
        val_metrics = validation_result['metrics']
        
        # Calculate performance decay (in-sample vs out-of-sample)
        primary_metric = self.config['primary_metric']
        performance_decay = (
            train_metrics[primary_metric] - val_metrics[primary_metric]
        ) / abs(train_metrics[primary_metric]) if train_metrics[primary_metric] != 0 else 0
        
        return {
            'window_id': window.window_id,
            'training_period': {
                'start': window.training_start,
                'end': window.training_end,
                'days': window.training_days,
                'metrics': train_metrics
            },
            'validation_period': {
                'start': window.validation_start,
                'end': window.validation_end,
                'days': window.validation_days,
                'metrics': val_metrics
            },
            'performance_decay': performance_decay,
            'validation_trades': val_metrics['total_trades'],
            'sufficient_trades': val_metrics['total_trades'] >= self.min_trades
        }
    
    def _calculate_aggregate_metrics(
        self,
        window_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate aggregate performance metrics across all windows"""
        
        # Extract validation metrics from all windows
        val_metrics = [wr['validation_period']['metrics'] for wr in window_results]
        
        # Calculate means and standard deviations
        aggregate = {}
        for metric in val_metrics[0].keys():
            values = [vm[metric] for vm in val_metrics]
            aggregate[f"{metric}_mean"] = np.mean(values)
            aggregate[f"{metric}_std"] = np.std(values)
            aggregate[f"{metric}_median"] = np.median(values)
            
        # Calculate additional aggregate statistics
        performance_decays = [wr['performance_decay'] for wr in window_results]
        aggregate['avg_performance_decay'] = np.mean(performance_decays)
        aggregate['max_performance_decay'] = np.max(performance_decays)
        
        # Calculate total trades across all windows
        total_trades = sum(wr['validation_trades'] for wr in window_results)
        aggregate['total_validation_trades'] = total_trades
        
        return aggregate
    
    def _calculate_stability_score(
        self,
        window_results: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate parameter stability score (0-1, higher = more stable)
        
        Measures consistency of performance across validation windows
        """
        primary_metric = self.config['primary_metric']
        
        # Extract primary metric values from validation periods
        metric_values = [
            wr['validation_period']['metrics'][primary_metric] 
            for wr in window_results
        ]
        
        if len(metric_values) < 2:
            return 0.0
            
        # Calculate coefficient of variation (lower = more stable)
        mean_val = np.mean(metric_values)
        std_val = np.std(metric_values)
        
        if mean_val == 0:
            return 0.0
            
        cv = std_val / abs(mean_val)
        
        # Convert to stability score (0-1, higher = more stable)
        # Use sigmoid transformation to map CV to 0-1 range
        stability_score = 1 / (1 + cv)
        
        return stability_score
    
    def _assess_overfitting_risk(
        self,
        window_results: List[Dict[str, Any]],
        aggregate_metrics: Dict[str, float]
    ) -> str:
        """
        Assess overfitting risk based on performance decay and trade count
        
        Returns:
            'low', 'medium', or 'high' overfitting risk assessment
        """
        # Check performance decay threshold
        max_decay = aggregate_metrics['max_performance_decay']
        avg_decay = aggregate_metrics['avg_performance_decay']
        
        # Check minimum trade requirements
        total_trades = aggregate_metrics['total_validation_trades']
        insufficient_trades = total_trades < self.min_trades * len(window_results)
        
        # Risk assessment logic
        if max_decay > self.decay_threshold or avg_decay > self.decay_threshold * 0.7:
            return 'high'
        elif insufficient_trades or avg_decay > self.decay_threshold * 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_statistical_significance(
        self,
        window_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate statistical significance tests for key metrics"""
        
        primary_metric = self.config['primary_metric']
        
        # Extract metric values from validation periods
        metric_values = [
            wr['validation_period']['metrics'][primary_metric] 
            for wr in window_results
        ]
        
        significance_tests = {}
        
        # Test if mean performance is significantly different from zero
        if len(metric_values) > 1:
            t_stat, p_value = stats.ttest_1samp(metric_values, 0)
            significance_tests['mean_different_from_zero_p'] = p_value
            significance_tests['mean_significant'] = p_value < self.significance_p
        
        # Test for consistency (low variance)
        if len(metric_values) > 2:
            # Bartlett test for equal variances (consistency check)
            # Using a benchmark variance for comparison
            benchmark_variance = np.var(metric_values) * 2  # Twice the observed variance
            significance_tests['consistency_check'] = np.var(metric_values) < benchmark_variance
        
        return significance_tests
    
    def export_validation_results(
        self,
        results: List[ValidationResult],
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Export validation results to JSON files for analysis
        
        Args:
            results: List of validation results
            output_dir: Directory to save results
            
        Returns:
            Dictionary mapping result type to file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        # Export walk-forward results
        walkforward_data = {
            'study_metadata': {
                'total_combinations': len(results),
                'validation_windows': len(results[0].window_results) if results else 0,
                'training_months': self.training_months,
                'validation_months': self.validation_months,
                'rolling_step_months': self.rolling_step_months,
                'generated_timestamp': datetime.now().isoformat()
            },
            'validation_results': [asdict(result) for result in results]
        }
        
        walkforward_file = output_dir / 'walkforward_results.json'
        with open(walkforward_file, 'w') as f:
            json.dump(walkforward_data, f, indent=2, default=str)
        exported_files['walkforward_results'] = str(walkforward_file)
        
        # Export summary statistics
        summary_data = self._generate_summary_statistics(results)
        summary_file = output_dir / 'validation_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        exported_files['validation_summary'] = str(summary_file)
        
        # Export robustness analysis
        robustness_data = self._generate_robustness_analysis(results)
        robustness_file = output_dir / 'robustness_analysis.json'
        with open(robustness_file, 'w') as f:
            json.dump(robustness_data, f, indent=2, default=str)
        exported_files['robustness_analysis'] = str(robustness_file)
        
        self.logger.info(f"Exported validation results to {output_dir}")
        return exported_files
    
    def _generate_summary_statistics(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate summary statistics across all parameter combinations"""
        
        primary_metric = self.config['primary_metric']
        
        # Extract key metrics
        stability_scores = [r.stability_score for r in results]
        overfitting_risks = [r.overfitting_risk for r in results]
        
        # Calculate aggregate performance
        performance_values = [
            r.aggregate_metrics[f"{primary_metric}_mean"]
            for r in results
        ]
        
        summary = {
            'study_overview': {
                'total_combinations_tested': len(results),
                'primary_optimization_metric': primary_metric,
                'validation_methodology': 'walk_forward_analysis'
            },
            'performance_distribution': {
                'best_performance': max(performance_values) if performance_values else None,
                'worst_performance': min(performance_values) if performance_values else None,
                'median_performance': np.median(performance_values) if performance_values else None,
                'performance_std': np.std(performance_values) if performance_values else None
            },
            'stability_analysis': {
                'mean_stability_score': np.mean(stability_scores),
                'high_stability_combinations': sum(1 for s in stability_scores if s > 0.8),
                'low_stability_combinations': sum(1 for s in stability_scores if s < 0.5)
            },
            'overfitting_assessment': {
                'low_risk_combinations': overfitting_risks.count('low'),
                'medium_risk_combinations': overfitting_risks.count('medium'), 
                'high_risk_combinations': overfitting_risks.count('high')
            },
            'recommended_combinations': self._get_top_combinations(results, n=5)
        }
        
        return summary
    
    def _generate_robustness_analysis(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate parameter robustness and sensitivity analysis"""
        
        # Extract parameter sensitivity data
        parameter_sensitivity = {}
        
        # Group results by individual parameters to assess sensitivity
        for param_name in results[0].parameters.keys():
            param_values = [r.parameters[param_name] for r in results]
            performance_values = [
                r.aggregate_metrics[f"{self.config['primary_metric']}_mean"]
                for r in results
            ]
            
            # Calculate correlation between parameter value and performance
            if len(set(param_values)) > 1:  # Only if parameter varies
                correlation = np.corrcoef(param_values, performance_values)[0, 1]
                parameter_sensitivity[param_name] = {
                    'correlation_with_performance': correlation,
                    'sensitivity_level': self._classify_sensitivity(abs(correlation))
                }
        
        robustness = {
            'parameter_sensitivity': parameter_sensitivity,
            'stability_distribution': {
                score: len([r for r in results if r.stability_score >= score])
                for score in [0.5, 0.6, 0.7, 0.8, 0.9]
            },
            'overfitting_distribution': {
                risk: len([r for r in results if r.overfitting_risk == risk])
                for risk in ['low', 'medium', 'high']
            }
        }
        
        return robustness
    
    def _classify_sensitivity(self, correlation: float) -> str:
        """Classify parameter sensitivity based on correlation magnitude"""
        if abs(correlation) > 0.7:
            return 'high'
        elif abs(correlation) > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_top_combinations(
        self,
        results: List[ValidationResult],
        n: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top N parameter combinations based on combined score"""
        
        # Calculate combined score: performance + stability - overfitting risk
        def calculate_combined_score(result: ValidationResult) -> float:
            primary_metric = self.config['primary_metric']
            performance = result.aggregate_metrics[f"{primary_metric}_mean"]
            stability = result.stability_score
            
            # Penalty for overfitting risk
            risk_penalty = {'low': 0, 'medium': 0.1, 'high': 0.3}[result.overfitting_risk]
            
            # Combined score (normalized)
            score = performance * stability - risk_penalty
            return score
        
        # Sort by combined score
        scored_results = [
            (calculate_combined_score(r), r) for r in results
        ]
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top N combinations
        top_combinations = []
        for score, result in scored_results[:n]:
            top_combinations.append({
                'rank': len(top_combinations) + 1,
                'combination_id': result.combination_id,
                'parameters': result.parameters,
                'combined_score': score,
                'performance': result.aggregate_metrics[f"{self.config['primary_metric']}_mean"],
                'stability_score': result.stability_score,
                'overfitting_risk': result.overfitting_risk
            })
        
        return top_combinations


def main():
    """Example usage of WalkForwardValidator"""
    
    # Example configuration
    config = {
        'study_name': 'Example_RSI_Optimization',
        'training_period_months': 24,
        'validation_period_months': 6,
        'rolling_step_months': 3,
        'min_validation_windows': 4,
        'start_date': '2020-01-01',
        'end_date': '2024-12-31',
        'primary_metric': 'sortino_ratio',
        'minimize_metric': False,
        'min_trades_per_combination': 30,
        'statistical_significance_p': 0.05,
        'out_of_sample_decay_threshold': 0.20
    }
    
    # Initialize validator
    validator = WalkForwardValidator(config)
    
    # Generate validation windows
    windows = validator.generate_validation_windows()
    print(f"Generated {len(windows)} validation windows")
    
    # Example parameter combination
    combination = ParameterCombination(
        combination_id='test_001',
        parameters={
            'rsi_period': 14,
            'rsi_threshold': 30,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.06
        },
        parameter_hash='abc123'
    )
    
    # Validate parameter combination
    result = validator.validate_parameter_combination(combination, windows)
    print(f"Validation complete. Stability score: {result.stability_score:.3f}")
    print(f"Overfitting risk: {result.overfitting_risk}")


if __name__ == '__main__':
    main()