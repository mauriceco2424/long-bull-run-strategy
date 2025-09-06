#!/usr/bin/env python3
"""
Overfitting Detection and Prevention Framework
Implements statistical safeguards against curve-fitting in trading strategy optimization
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from scipy import stats
from pathlib import Path
import logging
import warnings
from collections import defaultdict

@dataclass
class OverfittingAssessment:
    """Results of overfitting analysis for a parameter combination"""
    combination_id: str
    risk_level: str  # 'low', 'medium', 'high'
    risk_score: float  # 0-1, higher = more risky
    warning_flags: List[str]
    statistical_tests: Dict[str, Any]
    recommendations: List[str]
    
@dataclass
class ValidationMetrics:
    """Key metrics for overfitting detection"""
    in_sample_performance: float
    out_sample_performance: float
    performance_decay: float
    total_trades: int
    validation_periods: int
    parameter_count: int
    data_snooping_score: float

class OverfittingDetector:
    """
    Comprehensive overfitting detection and prevention system
    
    Implements multiple statistical tests and heuristics to identify
    parameter combinations that are likely overfit to historical data.
    
    Detection Methods:
    1. Performance decay analysis (in-sample vs out-of-sample)
    2. Statistical significance testing
    3. Parameter complexity penalties 
    4. Data-snooping bias detection
    5. Stability analysis across time periods
    6. Trade count sufficiency tests
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize overfitting detector
        
        Args:
            config: Configuration dictionary with detection thresholds
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Overfitting thresholds
        self.max_parameters = config.get('max_parameters_optimized', 5)
        self.min_trades = config.get('min_trades_per_combination', 30)
        self.decay_threshold = config.get('out_of_sample_decay_threshold', 0.20)
        self.significance_p = config.get('statistical_significance_p', 0.05)
        
        # Data snooping detection
        self.combinations_tested = 0
        self.best_performance_history = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for overfitting detection"""
        logger = logging.getLogger('overfitting_detector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def assess_overfitting_risk(
        self,
        combination_id: str,
        parameters: Dict[str, Any],
        validation_results: List[Dict[str, Any]],
        aggregate_metrics: Dict[str, float]
    ) -> OverfittingAssessment:
        """
        Comprehensive overfitting risk assessment
        
        Args:
            combination_id: Unique identifier for parameter combination
            parameters: Parameter values being tested
            validation_results: Results from walk-forward validation
            aggregate_metrics: Summary metrics across all validation windows
            
        Returns:
            OverfittingAssessment with risk level and detailed analysis
        """
        self.logger.info(f"Assessing overfitting risk for {combination_id}")
        
        # Extract validation metrics
        metrics = self._extract_validation_metrics(
            parameters, validation_results, aggregate_metrics
        )
        
        # Run overfitting detection tests
        warning_flags = []
        statistical_tests = {}
        risk_scores = []
        
        # Test 1: Performance decay analysis
        decay_risk, decay_flags = self._test_performance_decay(metrics)
        risk_scores.append(decay_risk)
        warning_flags.extend(decay_flags)
        statistical_tests['performance_decay'] = {
            'decay_percentage': metrics.performance_decay,
            'threshold': self.decay_threshold,
            'risk_score': decay_risk
        }
        
        # Test 2: Statistical significance testing
        sig_risk, sig_flags, sig_tests = self._test_statistical_significance(
            validation_results, metrics
        )
        risk_scores.append(sig_risk)
        warning_flags.extend(sig_flags)
        statistical_tests['significance_tests'] = sig_tests
        
        # Test 3: Parameter complexity analysis
        complexity_risk, complexity_flags = self._test_parameter_complexity(metrics)
        risk_scores.append(complexity_risk)
        warning_flags.extend(complexity_flags)
        statistical_tests['parameter_complexity'] = {
            'parameter_count': metrics.parameter_count,
            'max_allowed': self.max_parameters,
            'risk_score': complexity_risk
        }
        
        # Test 4: Trade count sufficiency
        trade_risk, trade_flags = self._test_trade_sufficiency(metrics)
        risk_scores.append(trade_risk)
        warning_flags.extend(trade_flags)
        statistical_tests['trade_sufficiency'] = {
            'total_trades': metrics.total_trades,
            'min_required': self.min_trades,
            'risk_score': trade_risk
        }
        
        # Test 5: Data snooping bias detection
        snooping_risk, snooping_flags = self._test_data_snooping(metrics)
        risk_scores.append(snooping_risk)
        warning_flags.extend(snooping_flags)
        statistical_tests['data_snooping'] = {
            'snooping_score': metrics.data_snooping_score,
            'combinations_tested': self.combinations_tested,
            'risk_score': snooping_risk
        }
        
        # Calculate overall risk score and level
        overall_risk_score = np.mean(risk_scores)
        risk_level = self._classify_risk_level(overall_risk_score, warning_flags)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, warning_flags, metrics
        )
        
        # Update global tracking
        self.combinations_tested += 1
        self.best_performance_history.append(metrics.out_sample_performance)
        
        return OverfittingAssessment(
            combination_id=combination_id,
            risk_level=risk_level,
            risk_score=overall_risk_score,
            warning_flags=warning_flags,
            statistical_tests=statistical_tests,
            recommendations=recommendations
        )
    
    def _extract_validation_metrics(
        self,
        parameters: Dict[str, Any],
        validation_results: List[Dict[str, Any]],
        aggregate_metrics: Dict[str, float]
    ) -> ValidationMetrics:
        """Extract key metrics from validation results for overfitting analysis"""
        
        # Calculate average in-sample and out-of-sample performance
        in_sample_perfs = []
        out_sample_perfs = []
        total_trades = 0
        
        primary_metric = self.config['primary_metric']
        
        for result in validation_results:
            in_sample_perfs.append(
                result['training_period']['metrics'][primary_metric]
            )
            out_sample_perfs.append(
                result['validation_period']['metrics'][primary_metric]
            )
            total_trades += result['validation_trades']
        
        in_sample_avg = np.mean(in_sample_perfs)
        out_sample_avg = np.mean(out_sample_perfs)
        
        # Calculate performance decay
        performance_decay = (
            (in_sample_avg - out_sample_avg) / abs(in_sample_avg)
            if in_sample_avg != 0 else 0
        )
        
        # Calculate data snooping score (simplified)
        data_snooping_score = self._calculate_data_snooping_score(out_sample_avg)
        
        return ValidationMetrics(
            in_sample_performance=in_sample_avg,
            out_sample_performance=out_sample_avg,
            performance_decay=performance_decay,
            total_trades=total_trades,
            validation_periods=len(validation_results),
            parameter_count=len(parameters),
            data_snooping_score=data_snooping_score
        )
    
    def _test_performance_decay(
        self, 
        metrics: ValidationMetrics
    ) -> Tuple[float, List[str]]:
        """
        Test for excessive performance decay from in-sample to out-of-sample
        
        Returns:
            (risk_score, warning_flags)
        """
        decay = metrics.performance_decay
        warning_flags = []
        
        # Calculate risk score based on decay severity
        if decay > self.decay_threshold:
            risk_score = min(1.0, decay / self.decay_threshold)
            if decay > self.decay_threshold * 1.5:
                warning_flags.append("SEVERE_PERFORMANCE_DECAY")
            else:
                warning_flags.append("HIGH_PERFORMANCE_DECAY")
        elif decay > self.decay_threshold * 0.7:
            risk_score = 0.6
            warning_flags.append("MODERATE_PERFORMANCE_DECAY")
        else:
            risk_score = max(0.0, decay / (self.decay_threshold * 0.7)) * 0.4
        
        # Additional checks for unusual patterns
        if decay < -0.1:  # Out-of-sample significantly better than in-sample
            warning_flags.append("SUSPICIOUS_IMPROVEMENT")
            risk_score = max(risk_score, 0.5)
        
        return risk_score, warning_flags
    
    def _test_statistical_significance(
        self,
        validation_results: List[Dict[str, Any]],
        metrics: ValidationMetrics
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Test statistical significance of performance metrics
        
        Returns:
            (risk_score, warning_flags, statistical_test_results)
        """
        primary_metric = self.config['primary_metric']
        warning_flags = []
        tests = {}
        risk_score = 0.0
        
        # Extract out-of-sample performance values
        out_sample_values = [
            result['validation_period']['metrics'][primary_metric]
            for result in validation_results
        ]
        
        if len(out_sample_values) < 3:
            warning_flags.append("INSUFFICIENT_VALIDATION_PERIODS")
            return 0.8, warning_flags, tests
        
        # Test 1: One-sample t-test against zero
        try:
            t_stat, p_value = stats.ttest_1samp(out_sample_values, 0)
            tests['t_test_vs_zero'] = {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < self.significance_p
            }
            
            if p_value >= self.significance_p:
                warning_flags.append("NOT_STATISTICALLY_SIGNIFICANT")
                risk_score = max(risk_score, 0.7)
                
        except Exception as e:
            self.logger.warning(f"T-test failed: {e}")
            tests['t_test_vs_zero'] = {'error': str(e)}
        
        # Test 2: Normality test (Shapiro-Wilk)
        try:
            if len(out_sample_values) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(out_sample_values)
                tests['normality_test'] = {
                    'statistic': shapiro_stat,
                    'p_value': shapiro_p,
                    'normal_distribution': shapiro_p > 0.05
                }
                
                if shapiro_p <= 0.05:
                    warning_flags.append("NON_NORMAL_RETURNS")
                    
        except Exception as e:
            self.logger.warning(f"Shapiro test failed: {e}")
            tests['normality_test'] = {'error': str(e)}
        
        # Test 3: Consistency test (coefficient of variation)
        cv = np.std(out_sample_values) / np.mean(out_sample_values) if np.mean(out_sample_values) != 0 else np.inf
        tests['consistency_test'] = {
            'coefficient_of_variation': cv,
            'high_variability': cv > 1.0
        }
        
        if cv > 1.5:
            warning_flags.append("HIGH_PERFORMANCE_VARIABILITY")
            risk_score = max(risk_score, 0.6)
        
        return risk_score, warning_flags, tests
    
    def _test_parameter_complexity(
        self, 
        metrics: ValidationMetrics
    ) -> Tuple[float, List[str]]:
        """
        Test for excessive parameter complexity (overfitting through complexity)
        
        Returns:
            (risk_score, warning_flags)
        """
        warning_flags = []
        param_count = metrics.parameter_count
        
        # Risk increases with parameter count
        if param_count > self.max_parameters:
            risk_score = 1.0
            warning_flags.append("EXCESSIVE_PARAMETERS")
        elif param_count >= self.max_parameters * 0.8:
            risk_score = 0.7
            warning_flags.append("HIGH_PARAMETER_COUNT")
        else:
            # Linear scaling from 0 to 0.5 based on parameter count
            risk_score = (param_count / self.max_parameters) * 0.5
        
        # Additional penalty for insufficient data relative to parameter count
        data_per_param = metrics.total_trades / param_count if param_count > 0 else 0
        min_data_per_param = 10  # Minimum trades per parameter
        
        if data_per_param < min_data_per_param:
            warning_flags.append("INSUFFICIENT_DATA_PER_PARAMETER")
            risk_score = max(risk_score, 0.8)
        
        return risk_score, warning_flags
    
    def _test_trade_sufficiency(
        self, 
        metrics: ValidationMetrics
    ) -> Tuple[float, List[str]]:
        """
        Test for sufficient trade count for statistical validity
        
        Returns:
            (risk_score, warning_flags)
        """
        warning_flags = []
        total_trades = metrics.total_trades
        required_trades = self.min_trades * metrics.validation_periods
        
        if total_trades < required_trades * 0.5:
            risk_score = 1.0
            warning_flags.append("SEVERELY_INSUFFICIENT_TRADES")
        elif total_trades < required_trades * 0.8:
            risk_score = 0.8
            warning_flags.append("INSUFFICIENT_TRADES")
        elif total_trades < required_trades:
            risk_score = 0.5
            warning_flags.append("MARGINAL_TRADE_COUNT")
        else:
            # Linear scaling from 0 to 0.2 based on excess trades
            excess_ratio = min(2.0, total_trades / required_trades)
            risk_score = 0.2 * (2.0 - excess_ratio)
        
        return risk_score, warning_flags
    
    def _test_data_snooping(
        self, 
        metrics: ValidationMetrics
    ) -> Tuple[float, List[str]]:
        """
        Test for data snooping bias (multiple testing problem)
        
        Returns:
            (risk_score, warning_flags)
        """
        warning_flags = []
        snooping_score = metrics.data_snooping_score
        
        # Risk increases with number of combinations tested and performance rank
        if snooping_score > 0.95:
            risk_score = 0.9
            warning_flags.append("HIGH_DATA_SNOOPING_RISK")
        elif snooping_score > 0.90:
            risk_score = 0.7
            warning_flags.append("MODERATE_DATA_SNOOPING_RISK")
        else:
            risk_score = snooping_score * 0.6
        
        # Additional penalty for excessive testing
        if self.combinations_tested > 1000:
            warning_flags.append("EXCESSIVE_PARAMETER_TESTING")
            risk_score = max(risk_score, 0.6)
        
        return risk_score, warning_flags
    
    def _calculate_data_snooping_score(self, performance: float) -> float:
        """
        Calculate data snooping score based on performance relative to history
        
        Simple implementation: percentile rank of current performance
        """
        if len(self.best_performance_history) == 0:
            return 0.5  # Neutral score for first combination
        
        # Calculate percentile rank
        better_count = sum(1 for p in self.best_performance_history if performance > p)
        percentile = better_count / len(self.best_performance_history)
        
        return percentile
    
    def _classify_risk_level(
        self, 
        overall_risk_score: float, 
        warning_flags: List[str]
    ) -> str:
        """
        Classify overall overfitting risk level
        
        Args:
            overall_risk_score: Average risk score across all tests
            warning_flags: List of warning flags raised
            
        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        # Check for critical warning flags
        critical_flags = {
            'SEVERE_PERFORMANCE_DECAY',
            'EXCESSIVE_PARAMETERS', 
            'SEVERELY_INSUFFICIENT_TRADES'
        }
        
        if any(flag in critical_flags for flag in warning_flags):
            return 'high'
        
        # Classify based on risk score
        if overall_risk_score >= 0.7:
            return 'high'
        elif overall_risk_score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(
        self,
        risk_level: str,
        warning_flags: List[str],
        metrics: ValidationMetrics
    ) -> List[str]:
        """Generate specific recommendations based on identified issues"""
        
        recommendations = []
        
        # General recommendations by risk level
        if risk_level == 'high':
            recommendations.append(
                "HIGH RISK: This parameter combination shows strong signs of overfitting. "
                "Consider avoiding this configuration for live trading."
            )
        elif risk_level == 'medium':
            recommendations.append(
                "MEDIUM RISK: Use caution with this parameter combination. "
                "Consider additional validation or position size reduction."
            )
        else:
            recommendations.append(
                "LOW RISK: This parameter combination appears robust, "
                "but continue monitoring performance in live trading."
            )
        
        # Specific recommendations based on warning flags
        flag_recommendations = {
            'SEVERE_PERFORMANCE_DECAY': [
                "Reduce parameter complexity or increase validation data",
                "Consider ensemble methods to improve robustness"
            ],
            'HIGH_PERFORMANCE_DECAY': [
                "Monitor closely in live trading",
                "Consider walk-forward re-optimization schedule"
            ],
            'EXCESSIVE_PARAMETERS': [
                f"Reduce parameter count to maximum {self.max_parameters}",
                "Focus on most impactful parameters only"
            ],
            'SEVERELY_INSUFFICIENT_TRADES': [
                f"Increase data range to generate minimum {self.min_trades} trades",
                "Consider less restrictive entry conditions"
            ],
            'NOT_STATISTICALLY_SIGNIFICANT': [
                "Results may be due to random chance",
                "Increase validation periods or data range"
            ],
            'HIGH_DATA_SNOOPING_RISK': [
                "Apply Bonferroni correction for multiple testing",
                "Use out-of-time validation for final confirmation"
            ]
        }
        
        for flag in warning_flags:
            if flag in flag_recommendations:
                recommendations.extend(flag_recommendations[flag])
        
        return list(set(recommendations))  # Remove duplicates
    
    def export_overfitting_analysis(
        self,
        assessments: List[OverfittingAssessment],
        output_dir: Path
    ) -> str:
        """
        Export comprehensive overfitting analysis report
        
        Args:
            assessments: List of overfitting assessments
            output_dir: Directory to save analysis
            
        Returns:
            Path to exported analysis file
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Compile analysis data
        analysis_data = {
            'study_overview': {
                'total_combinations_assessed': len(assessments),
                'assessment_timestamp': datetime.now().isoformat(),
                'detection_methodology': 'multi_factor_overfitting_analysis',
                'thresholds': {
                    'max_parameters': self.max_parameters,
                    'min_trades': self.min_trades,
                    'decay_threshold': self.decay_threshold,
                    'significance_p': self.significance_p
                }
            },
            'risk_distribution': {
                'low_risk': len([a for a in assessments if a.risk_level == 'low']),
                'medium_risk': len([a for a in assessments if a.risk_level == 'medium']),
                'high_risk': len([a for a in assessments if a.risk_level == 'high'])
            },
            'common_warning_flags': self._analyze_common_warnings(assessments),
            'risk_score_statistics': {
                'mean_risk_score': np.mean([a.risk_score for a in assessments]),
                'median_risk_score': np.median([a.risk_score for a in assessments]),
                'max_risk_score': max([a.risk_score for a in assessments]),
                'min_risk_score': min([a.risk_score for a in assessments])
            },
            'detailed_assessments': [asdict(assessment) for assessment in assessments],
            'recommendations': {
                'general_guidelines': self._generate_general_guidelines(assessments),
                'optimization_improvements': self._suggest_optimization_improvements(assessments)
            }
        }
        
        # Export to JSON
        analysis_file = output_dir / 'overfitting_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        # Export summary report
        summary_file = output_dir / 'overfitting_summary.txt'
        self._export_text_summary(assessments, summary_file)
        
        self.logger.info(f"Exported overfitting analysis to {output_dir}")
        return str(analysis_file)
    
    def _analyze_common_warnings(
        self, 
        assessments: List[OverfittingAssessment]
    ) -> Dict[str, int]:
        """Analyze frequency of warning flags across all assessments"""
        
        flag_counts = defaultdict(int)
        for assessment in assessments:
            for flag in assessment.warning_flags:
                flag_counts[flag] += 1
        
        return dict(flag_counts)
    
    def _generate_general_guidelines(
        self, 
        assessments: List[OverfittingAssessment]
    ) -> List[str]:
        """Generate general guidelines based on assessment patterns"""
        
        guidelines = []
        
        # Analyze overall risk distribution
        high_risk_pct = len([a for a in assessments if a.risk_level == 'high']) / len(assessments)
        
        if high_risk_pct > 0.5:
            guidelines.append(
                "CRITICAL: Over 50% of parameter combinations show high overfitting risk. "
                "Consider reducing parameter complexity or increasing validation data."
            )
        elif high_risk_pct > 0.25:
            guidelines.append(
                "WARNING: Over 25% of combinations show high overfitting risk. "
                "Review optimization methodology and validation approach."
            )
        
        # Analyze common warning patterns
        common_flags = self._analyze_common_warnings(assessments)
        most_common = max(common_flags.items(), key=lambda x: x[1]) if common_flags else None
        
        if most_common and most_common[1] > len(assessments) * 0.3:
            guidelines.append(
                f"Most common issue: {most_common[0]} affecting {most_common[1]} combinations. "
                f"Address this systematically across the optimization study."
            )
        
        return guidelines
    
    def _suggest_optimization_improvements(
        self, 
        assessments: List[OverfittingAssessment]
    ) -> List[str]:
        """Suggest improvements to optimization methodology"""
        
        improvements = []
        
        # Check for systematic issues
        severe_decay_count = sum(
            1 for a in assessments 
            if 'SEVERE_PERFORMANCE_DECAY' in a.warning_flags
        )
        
        if severe_decay_count > len(assessments) * 0.2:
            improvements.append(
                "Consider implementing regularization techniques or ensemble methods "
                "to reduce performance decay across parameter combinations."
            )
        
        # Check for parameter complexity issues
        excess_param_count = sum(
            1 for a in assessments 
            if 'EXCESSIVE_PARAMETERS' in a.warning_flags
        )
        
        if excess_param_count > 0:
            improvements.append(
                "Reduce parameter search space or use feature selection methods "
                "to identify most impactful parameters for optimization."
            )
        
        # Data sufficiency recommendations
        insufficient_trade_count = sum(
            1 for a in assessments 
            if any(flag.endswith('_INSUFFICIENT_TRADES') for flag in a.warning_flags)
        )
        
        if insufficient_trade_count > len(assessments) * 0.3:
            improvements.append(
                "Expand data range or adjust strategy parameters to generate "
                "sufficient trades for statistical validation."
            )
        
        return improvements
    
    def _export_text_summary(
        self, 
        assessments: List[OverfittingAssessment], 
        output_file: Path
    ) -> None:
        """Export human-readable summary report"""
        
        with open(output_file, 'w') as f:
            f.write("OVERFITTING ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            # Overview
            f.write(f"Total Parameter Combinations Analyzed: {len(assessments)}\n")
            f.write(f"Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Risk Distribution
            risk_counts = {
                'low': len([a for a in assessments if a.risk_level == 'low']),
                'medium': len([a for a in assessments if a.risk_level == 'medium']),
                'high': len([a for a in assessments if a.risk_level == 'high'])
            }
            
            f.write("RISK DISTRIBUTION:\n")
            for level, count in risk_counts.items():
                pct = (count / len(assessments)) * 100
                f.write(f"  {level.upper()} Risk: {count} combinations ({pct:.1f}%)\n")
            f.write("\n")
            
            # Top Risk Combinations
            high_risk = [a for a in assessments if a.risk_level == 'high']
            if high_risk:
                f.write("HIGH RISK COMBINATIONS:\n")
                for assessment in sorted(high_risk, key=lambda x: x.risk_score, reverse=True)[:10]:
                    f.write(f"  {assessment.combination_id}: Risk Score {assessment.risk_score:.3f}\n")
                    f.write(f"    Warnings: {', '.join(assessment.warning_flags)}\n")
                f.write("\n")
            
            # Common Issues
            common_flags = self._analyze_common_warnings(assessments)
            if common_flags:
                f.write("MOST COMMON ISSUES:\n")
                for flag, count in sorted(common_flags.items(), key=lambda x: x[1], reverse=True)[:5]:
                    pct = (count / len(assessments)) * 100
                    f.write(f"  {flag}: {count} combinations ({pct:.1f}%)\n")
                f.write("\n")
            
            # Recommendations
            guidelines = self._generate_general_guidelines(assessments)
            if guidelines:
                f.write("RECOMMENDATIONS:\n")
                for i, guideline in enumerate(guidelines, 1):
                    f.write(f"  {i}. {guideline}\n")


def main():
    """Example usage of OverfittingDetector"""
    
    config = {
        'max_parameters_optimized': 5,
        'min_trades_per_combination': 30,
        'out_of_sample_decay_threshold': 0.20,
        'statistical_significance_p': 0.05,
        'primary_metric': 'sortino_ratio'
    }
    
    detector = OverfittingDetector(config)
    
    # Example assessment (normally would come from validation results)
    example_validation = [
        {
            'training_period': {'metrics': {'sortino_ratio': 2.1}},
            'validation_period': {'metrics': {'sortino_ratio': 1.8}},
            'validation_trades': 45
        },
        {
            'training_period': {'metrics': {'sortino_ratio': 2.0}},
            'validation_period': {'metrics': {'sortino_ratio': 1.7}},
            'validation_trades': 38
        }
    ]
    
    example_aggregate = {'total_validation_trades': 83}
    example_params = {'rsi_period': 14, 'rsi_threshold': 30}
    
    assessment = detector.assess_overfitting_risk(
        'test_001',
        example_params,
        example_validation,
        example_aggregate
    )
    
    print(f"Risk Level: {assessment.risk_level}")
    print(f"Risk Score: {assessment.risk_score:.3f}")
    print(f"Warnings: {assessment.warning_flags}")


if __name__ == '__main__':
    main()