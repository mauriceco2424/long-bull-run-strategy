#!/usr/bin/env python3
"""
Optimization Orchestrator
Coordinates parameter optimization with existing analyzer/evaluator workflow
"""

import json
import os
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import itertools
import random
import numpy as np
from dataclasses import dataclass, asdict
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

from walkforward_validator import WalkForwardValidator, ValidationWindow, ParameterCombination
from overfitting_detector import OverfittingDetector

@dataclass
class OptimizationStudy:
    """Represents a complete optimization study"""
    study_id: str
    study_name: str
    config: Dict[str, Any]
    parameter_combinations: List[ParameterCombination]
    validation_windows: List[ValidationWindow]
    start_timestamp: str
    status: str  # 'running', 'completed', 'failed'
    progress: Dict[str, Any]

class OptimizationOrchestrator:
    """
    Orchestrates complete parameter optimization studies
    
    Coordinates:
    1. Parameter space generation (grid/random/Bayesian search)
    2. Walk-forward validation execution
    3. Individual run processing via analyzer
    4. Overfitting detection and prevention
    5. Results aggregation and reporting
    6. Integration with evaluator for final assessment
    """
    
    def __init__(self, config_path: str):
        """
        Initialize orchestrator with optimization configuration
        
        Args:
            config_path: Path to optimization_config.md file
        """
        self.config_path = Path(config_path)
        self.config = self._load_optimization_config()
        self.study_id = self._generate_study_id()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.validator = WalkForwardValidator(self.config)
        self.overfitting_detector = OverfittingDetector(self.config)
        
        # Setup directories
        self.study_dir = Path(f"data/optimization/{self.study_id}")
        self.study_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress tracking
        self.total_combinations = 0
        self.completed_combinations = 0
        self.failed_combinations = 0
        
    def _load_optimization_config(self) -> Dict[str, Any]:
        """Load and validate optimization configuration"""
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        # Parse markdown configuration file
        config = {}
        with open(self.config_path, 'r') as f:
            content = f.read()
            
        # Extract configuration parameters from markdown
        # This is a simplified parser - in production you might use a more robust approach
        lines = content.split('\n')
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                # Remove markdown formatting and extract key-value pairs
                clean_line = line.strip()
                if clean_line.startswith('- '):
                    clean_line = clean_line[2:]
                
                if ': [REQUIRED:' in clean_line:
                    continue  # Skip template lines
                    
                if ': ' in clean_line and not '[REQUIRED' in clean_line:
                    key, value = clean_line.split(': ', 1)
                    
                    # Clean up key
                    key = key.strip('*').strip()
                    
                    # Parse value
                    value = value.strip()
                    if value.lower() in ['true', 'false']:
                        config[key] = value.lower() == 'true'
                    elif value.replace('.', '').replace('-', '').isdigit():
                        config[key] = float(value) if '.' in value else int(value)
                    else:
                        config[key] = value
        
        # Validate required parameters
        required_params = [
            'study_name', 'search_strategy', 'max_combinations',
            'training_period_months', 'validation_period_months',
            'universe', 'timeframe', 'start_date', 'end_date',
            'primary_metric'
        ]
        
        missing_params = [p for p in required_params if p not in config]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        return config
    
    def _generate_study_id(self) -> str:
        """Generate unique study identifier"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        study_name = self.config.get('study_name', 'optimization').replace(' ', '_')
        unique_id = str(uuid.uuid4())[:8]
        return f"{study_name}_{timestamp}_{unique_id}"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for orchestrator"""
        logger = logging.getLogger(f'optimization_orchestrator_{self.study_id}')
        logger.setLevel(logging.INFO)
        
        # File handler for study-specific log
        log_file = self.study_dir / 'optimization.log' if hasattr(self, 'study_dir') else Path('optimization.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def execute_optimization_study(self) -> str:
        """
        Execute complete optimization study
        
        Returns:
            Path to study results directory
        """
        self.logger.info(f"Starting optimization study: {self.study_id}")
        
        try:
            # Phase 1: Configuration validation and setup
            self._validate_configuration()
            
            # Phase 2: Parameter space generation
            parameter_combinations = self._generate_parameter_combinations()
            
            # Phase 3: Walk-forward validation setup
            validation_windows = self.validator.generate_validation_windows()
            
            # Phase 4: Execute parameter sweep
            validation_results = self._execute_parameter_sweep(
                parameter_combinations, validation_windows
            )
            
            # Phase 5: Overfitting analysis
            overfitting_assessments = self._analyze_overfitting(validation_results)
            
            # Phase 6: Generate study artifacts
            study_results = self._generate_study_artifacts(
                parameter_combinations, validation_results, overfitting_assessments
            )
            
            # Phase 7: Update study registry
            self._update_optimization_registry(study_results)
            
            self.logger.info(f"Optimization study completed: {self.study_id}")
            return str(self.study_dir)
            
        except Exception as e:
            self.logger.error(f"Optimization study failed: {e}")
            self._update_study_status('failed', str(e))
            raise
    
    def _validate_configuration(self) -> None:
        """Validate optimization configuration completeness"""
        self.logger.info("Validating optimization configuration")
        
        # Check parameter ranges are properly defined
        required_ranges = []
        
        # Extract parameter range definitions
        with open(self.config_path, 'r') as f:
            content = f.read()
        
        # Look for parameter range patterns (simplified)
        import re
        param_patterns = [
            r'(\w+)_min:', r'(\w+)_max:', r'(\w+)_step:'
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                param_base = match.replace('_min', '').replace('_max', '').replace('_step', '')
                if param_base not in required_ranges:
                    required_ranges.append(param_base)
        
        self.logger.info(f"Found {len(required_ranges)} parameter ranges to optimize")
        
        # Validate date range supports walk-forward analysis
        total_months = self.config['training_period_months'] + self.config['validation_period_months']
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['end_date'], '%Y-%m-%d')
        available_months = (end_date - start_date).days / 30.44  # Average days per month
        
        if available_months < total_months * 2:  # Need at least 2 validation cycles
            raise ValueError(
                f"Insufficient data range for walk-forward analysis. "
                f"Need {total_months * 2:.1f} months, have {available_months:.1f} months"
            )
    
    def _generate_parameter_combinations(self) -> List[ParameterCombination]:
        """Generate parameter combinations based on search strategy"""
        self.logger.info(f"Generating parameter combinations using {self.config['search_strategy']} search")
        
        # Extract parameter ranges from configuration
        parameter_ranges = self._extract_parameter_ranges()
        
        search_strategy = self.config['search_strategy'].lower()
        max_combinations = self.config['max_combinations']
        
        if search_strategy == 'grid':
            combinations = self._generate_grid_combinations(parameter_ranges)
        elif search_strategy == 'random':
            combinations = self._generate_random_combinations(parameter_ranges, max_combinations)
        elif search_strategy == 'bayesian':
            combinations = self._generate_bayesian_combinations(parameter_ranges, max_combinations)
        else:
            raise ValueError(f"Unknown search strategy: {search_strategy}")
        
        # Limit to max combinations if needed
        if len(combinations) > max_combinations:
            if search_strategy == 'grid':
                # For grid search, warn about truncation
                self.logger.warning(f"Grid search generated {len(combinations)} combinations, truncating to {max_combinations}")
            combinations = combinations[:max_combinations]
        
        self.total_combinations = len(combinations)
        self.logger.info(f"Generated {len(combinations)} parameter combinations")
        
        return combinations
    
    def _extract_parameter_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Extract parameter ranges from configuration"""
        ranges = {}
        
        # Parse configuration for parameter ranges
        for key, value in self.config.items():
            if '_min' in key:
                param_name = key.replace('_min', '')
                if param_name not in ranges:
                    ranges[param_name] = {}
                ranges[param_name]['min'] = value
            elif '_max' in key:
                param_name = key.replace('_max', '')
                if param_name not in ranges:
                    ranges[param_name] = {}
                ranges[param_name]['max'] = value
            elif '_step' in key:
                param_name = key.replace('_step', '')
                if param_name not in ranges:
                    ranges[param_name] = {}
                ranges[param_name]['step'] = value
        
        # Validate ranges are complete
        complete_ranges = {}
        for param, range_def in ranges.items():
            if 'min' in range_def and 'max' in range_def and 'step' in range_def:
                complete_ranges[param] = range_def
            else:
                missing = [k for k in ['min', 'max', 'step'] if k not in range_def]
                self.logger.warning(f"Parameter {param} missing: {missing}")
        
        return complete_ranges
    
    def _generate_grid_combinations(
        self, 
        parameter_ranges: Dict[str, Dict[str, Any]]
    ) -> List[ParameterCombination]:
        """Generate all possible parameter combinations (grid search)"""
        
        param_values = {}
        for param, range_def in parameter_ranges.items():
            min_val = range_def['min']
            max_val = range_def['max']
            step = range_def['step']
            
            # Generate value range
            if isinstance(min_val, int) and isinstance(step, int):
                values = list(range(min_val, max_val + 1, step))
            else:
                values = []
                val = min_val
                while val <= max_val:
                    values.append(val)
                    val += step
            
            param_values[param] = values
        
        # Generate all combinations
        combinations = []
        param_names = list(param_values.keys())
        
        for combination in itertools.product(*[param_values[p] for p in param_names]):
            params = dict(zip(param_names, combination))
            
            # Add fixed parameters from configuration
            fixed_params = self._get_fixed_parameters()
            params.update(fixed_params)
            
            # Generate combination ID and hash
            combo_id = f"grid_{len(combinations):04d}"
            param_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:8]
            
            combinations.append(ParameterCombination(
                combination_id=combo_id,
                parameters=params,
                parameter_hash=param_hash
            ))
        
        return combinations
    
    def _generate_random_combinations(
        self,
        parameter_ranges: Dict[str, Dict[str, Any]],
        max_combinations: int
    ) -> List[ParameterCombination]:
        """Generate random parameter combinations"""
        
        # Set random seed for reproducibility
        if 'random_seed' in self.config:
            random.seed(self.config['random_seed'])
            np.random.seed(self.config['random_seed'])
        
        combinations = []
        fixed_params = self._get_fixed_parameters()
        
        for i in range(max_combinations):
            params = {}
            
            # Generate random value for each parameter
            for param, range_def in parameter_ranges.items():
                min_val = range_def['min']
                max_val = range_def['max']
                step = range_def['step']
                
                if isinstance(min_val, int) and isinstance(step, int):
                    # Integer parameter
                    n_steps = int((max_val - min_val) / step) + 1
                    step_idx = random.randint(0, n_steps - 1)
                    value = min_val + step_idx * step
                else:
                    # Float parameter
                    n_steps = int((max_val - min_val) / step) + 1
                    step_idx = random.randint(0, n_steps - 1)
                    value = min_val + step_idx * step
                    
                params[param] = value
            
            # Add fixed parameters
            params.update(fixed_params)
            
            # Generate combination ID and hash
            combo_id = f"rand_{i:04d}"
            param_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:8]
            
            combinations.append(ParameterCombination(
                combination_id=combo_id,
                parameters=params,
                parameter_hash=param_hash
            ))
        
        return combinations
    
    def _generate_bayesian_combinations(
        self,
        parameter_ranges: Dict[str, Dict[str, Any]],
        max_combinations: int
    ) -> List[ParameterCombination]:
        """Generate parameter combinations using Bayesian optimization"""
        # Simplified implementation - in production you might use scikit-optimize
        self.logger.warning("Bayesian optimization not fully implemented, using random sampling")
        return self._generate_random_combinations(parameter_ranges, max_combinations)
    
    def _get_fixed_parameters(self) -> Dict[str, Any]:
        """Get parameters that remain fixed during optimization"""
        fixed_params = {}
        
        # Portfolio parameters (typically fixed)
        portfolio_keys = [
            'accounting_mode', 'position_sizing_strategy', 'position_size_pct',
            'max_concurrent_positions'
        ]
        
        for key in portfolio_keys:
            if key in self.config:
                fixed_params[key] = self.config[key]
        
        # Risk parameters (typically fixed)
        risk_keys = ['max_daily_trades', 'cooldown_bars']
        
        for key in risk_keys:
            if key in self.config:
                fixed_params[key] = self.config[key]
        
        # Market configuration (always fixed)
        market_keys = ['universe', 'timeframe']
        
        for key in market_keys:
            if key in self.config:
                fixed_params[key] = self.config[key]
        
        return fixed_params
    
    def _execute_parameter_sweep(
        self,
        parameter_combinations: List[ParameterCombination],
        validation_windows: List[ValidationWindow]
    ) -> List[Any]:
        """Execute parameter sweep with walk-forward validation"""
        
        self.logger.info(f"Executing parameter sweep with {len(parameter_combinations)} combinations")
        
        # Setup progress tracking
        self.completed_combinations = 0
        self.failed_combinations = 0
        validation_results = []
        
        # Determine parallel execution strategy
        max_parallel = self.config.get('max_parallel_runs', 4)
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # Submit all validation tasks
            future_to_combination = {
                executor.submit(
                    self.validator.validate_parameter_combination,
                    combination,
                    validation_windows
                ): combination
                for combination in parameter_combinations
            }
            
            # Process completed tasks
            for future in as_completed(future_to_combination):
                combination = future_to_combination[future]
                
                try:
                    result = future.result(timeout=self.config.get('timeout_minutes_per_run', 15) * 60)
                    validation_results.append(result)
                    self.completed_combinations += 1
                    
                    # Log progress
                    progress_pct = (self.completed_combinations / self.total_combinations) * 100
                    self.logger.info(
                        f"Completed {combination.combination_id} "
                        f"({self.completed_combinations}/{self.total_combinations}, {progress_pct:.1f}%)"
                    )
                    
                except Exception as e:
                    self.failed_combinations += 1
                    self.logger.error(f"Failed {combination.combination_id}: {e}")
        
        self.logger.info(
            f"Parameter sweep completed. "
            f"Successful: {self.completed_combinations}, Failed: {self.failed_combinations}"
        )
        
        return validation_results
    
    def _analyze_overfitting(self, validation_results: List[Any]) -> List[Any]:
        """Analyze overfitting risk for all validation results"""
        
        self.logger.info("Analyzing overfitting risk for all parameter combinations")
        
        overfitting_assessments = []
        
        for result in validation_results:
            assessment = self.overfitting_detector.assess_overfitting_risk(
                result.combination_id,
                result.parameters,
                result.window_results,
                result.aggregate_metrics
            )
            overfitting_assessments.append(assessment)
        
        # Export overfitting analysis
        self.overfitting_detector.export_overfitting_analysis(
            overfitting_assessments, self.study_dir
        )
        
        return overfitting_assessments
    
    def _generate_study_artifacts(
        self,
        parameter_combinations: List[ParameterCombination],
        validation_results: List[Any],
        overfitting_assessments: List[Any]
    ) -> Dict[str, Any]:
        """Generate all optimization study artifacts"""
        
        self.logger.info("Generating optimization study artifacts")
        
        # Export validation results
        self.validator.export_validation_results(validation_results, self.study_dir)
        
        # Generate optimization summary
        summary = self._generate_optimization_summary(
            validation_results, overfitting_assessments
        )
        
        summary_file = self.study_dir / 'optimization_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Generate parameter sweep CSV
        self._generate_parameter_sweep_csv(validation_results, overfitting_assessments)
        
        # Generate study manifest
        manifest = self._generate_study_manifest(parameter_combinations)
        
        manifest_file = self.study_dir / 'study_manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        return {
            'study_id': self.study_id,
            'study_dir': str(self.study_dir),
            'total_combinations': len(parameter_combinations),
            'successful_combinations': len(validation_results),
            'best_performance': summary.get('best_combination', {}).get('performance'),
            'summary_file': str(summary_file),
            'manifest_file': str(manifest_file)
        }
    
    def _generate_optimization_summary(
        self,
        validation_results: List[Any],
        overfitting_assessments: List[Any]
    ) -> Dict[str, Any]:
        """Generate optimization study summary"""
        
        primary_metric = self.config['primary_metric']
        
        # Find best combination
        best_combination = None
        best_performance = float('-inf') if not self.config.get('minimize_metric', False) else float('inf')
        
        for result in validation_results:
            performance = result.aggregate_metrics[f"{primary_metric}_mean"]
            
            if self.config.get('minimize_metric', False):
                is_better = performance < best_performance
            else:
                is_better = performance > best_performance
            
            if is_better:
                best_performance = performance
                best_combination = result
        
        # Calculate summary statistics
        all_performances = [
            r.aggregate_metrics[f"{primary_metric}_mean"] for r in validation_results
        ]
        
        summary = {
            'study_overview': {
                'study_id': self.study_id,
                'study_name': self.config['study_name'],
                'optimization_metric': primary_metric,
                'total_combinations_tested': len(validation_results),
                'successful_combinations': len(validation_results),
                'failed_combinations': self.failed_combinations,
                'completion_timestamp': datetime.now().isoformat()
            },
            'performance_statistics': {
                'best_performance': best_performance,
                'worst_performance': min(all_performances) if all_performances else None,
                'mean_performance': np.mean(all_performances) if all_performances else None,
                'median_performance': np.median(all_performances) if all_performances else None,
                'std_performance': np.std(all_performances) if all_performances else None
            },
            'best_combination': {
                'combination_id': best_combination.combination_id if best_combination else None,
                'parameters': best_combination.parameters if best_combination else None,
                'performance': best_performance,
                'stability_score': best_combination.stability_score if best_combination else None
            } if best_combination else None,
            'overfitting_summary': {
                'low_risk_combinations': len([a for a in overfitting_assessments if a.risk_level == 'low']),
                'medium_risk_combinations': len([a for a in overfitting_assessments if a.risk_level == 'medium']),
                'high_risk_combinations': len([a for a in overfitting_assessments if a.risk_level == 'high'])
            },
            'configuration': self.config
        }
        
        return summary
    
    def _generate_parameter_sweep_csv(
        self,
        validation_results: List[Any],
        overfitting_assessments: List[Any]
    ) -> None:
        """Generate parameter sweep results CSV"""
        
        import csv
        
        csv_file = self.study_dir / 'parameter_sweep.csv'
        
        # Determine all parameter names and metrics
        if not validation_results:
            return
        
        first_result = validation_results[0]
        param_names = list(first_result.parameters.keys())
        metric_names = list(first_result.aggregate_metrics.keys())
        
        # Create overfitting lookup
        overfitting_lookup = {
            a.combination_id: a for a in overfitting_assessments
        }
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['combination_id'] + param_names + metric_names + [
                'stability_score', 'overfitting_risk', 'overfitting_score'
            ]
            writer.writerow(header)
            
            # Write data rows
            for result in validation_results:
                overfitting = overfitting_lookup.get(result.combination_id)
                
                row = [result.combination_id]
                row.extend([result.parameters[p] for p in param_names])
                row.extend([result.aggregate_metrics[m] for m in metric_names])
                row.append(result.stability_score)
                row.append(overfitting.risk_level if overfitting else 'unknown')
                row.append(overfitting.risk_score if overfitting else None)
                
                writer.writerow(row)
    
    def _generate_study_manifest(
        self,
        parameter_combinations: List[ParameterCombination]
    ) -> Dict[str, Any]:
        """Generate study manifest with metadata"""
        
        return {
            'study_metadata': {
                'study_id': self.study_id,
                'study_name': self.config['study_name'],
                'creation_timestamp': datetime.now().isoformat(),
                'config_path': str(self.config_path),
                'config_hash': hashlib.md5(str(self.config).encode()).hexdigest()
            },
            'optimization_configuration': self.config,
            'parameter_space': {
                'total_combinations_generated': len(parameter_combinations),
                'search_strategy': self.config['search_strategy'],
                'optimization_parameters': [
                    param for param in self.config.keys() 
                    if any(suffix in param for suffix in ['_min', '_max', '_step'])
                ]
            },
            'validation_methodology': {
                'method': 'walk_forward_analysis',
                'training_months': self.config['training_period_months'],
                'validation_months': self.config['validation_period_months'],
                'rolling_step_months': self.config['rolling_step_months']
            },
            'execution_summary': {
                'total_combinations': self.total_combinations,
                'completed_combinations': self.completed_combinations,
                'failed_combinations': self.failed_combinations
            }
        }
    
    def _update_optimization_registry(self, study_results: Dict[str, Any]) -> None:
        """Update optimization study registry"""
        
        registry_file = Path('docs/optimization/optimization_registry.csv')
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create registry if it doesn't exist
        if not registry_file.exists():
            with open(registry_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'study_id', 'study_name', 'completion_timestamp', 
                    'total_combinations', 'successful_combinations',
                    'best_performance', 'primary_metric', 'status'
                ])
        
        # Append study record
        with open(registry_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.study_id,
                self.config['study_name'],
                datetime.now().isoformat(),
                study_results['total_combinations'],
                study_results['successful_combinations'],
                study_results['best_performance'],
                self.config['primary_metric'],
                'completed'
            ])
    
    def _update_study_status(self, status: str, error_msg: Optional[str] = None) -> None:
        """Update study status in manifest"""
        
        status_file = self.study_dir / 'study_status.json'
        
        status_data = {
            'study_id': self.study_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'error_message': error_msg
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)


def main():
    """Example usage of OptimizationOrchestrator"""
    
    # Create example optimization config file
    config_content = """
# Trading Strategy - Parameter Optimization Configuration

study_name: Example RSI Optimization
search_strategy: random
max_combinations: 50
random_seed: 42

training_period_months: 24
validation_period_months: 6
rolling_step_months: 3
min_validation_windows: 4

universe: binance_usdt
timeframe: 4h
start_date: 2021-01-01
end_date: 2024-12-31

primary_metric: sortino_ratio
minimize_metric: false

# Parameter ranges
rsi_period_min: 10
rsi_period_max: 20
rsi_period_step: 2

rsi_threshold_min: 25
rsi_threshold_max: 35
rsi_threshold_step: 2.5

# Fixed parameters
accounting_mode: mark-to-market
position_sizing_strategy: fixed-percent
position_size_pct: 0.05
max_concurrent_positions: 5

# Overfitting prevention
min_trades_per_combination: 30
max_parameters_optimized: 3
out_of_sample_decay_threshold: 0.20
statistical_significance_p: 0.05
"""
    
    # Write example config
    config_file = Path('optimization_config_example.md')
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    # Run optimization
    orchestrator = OptimizationOrchestrator(config_file)
    results_dir = orchestrator.execute_optimization_study()
    
    print(f"Optimization study completed: {results_dir}")


if __name__ == '__main__':
    main()