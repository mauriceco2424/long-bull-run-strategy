#!/usr/bin/env python3
"""
Test Optimization Workflow End-to-End
Validates the complete parameter optimization system
"""

import json
import tempfile
import shutil
from pathlib import Path
import pytest
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add tools directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from walkforward_validator import WalkForwardValidator, ParameterCombination
from overfitting_detector import OverfittingDetector
from optimization_orchestrator import OptimizationOrchestrator

class TestOptimizationWorkflow:
    """Comprehensive test suite for optimization workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test optimization configuration
        self.config_content = """
# Test Optimization Configuration

study_name: Test RSI Optimization
search_strategy: random
max_combinations: 10
random_seed: 42

training_period_months: 12
validation_period_months: 3
rolling_step_months: 2
min_validation_windows: 3

universe: test_universe
timeframe: 1h
start_date: 2022-01-01
end_date: 2023-12-31

primary_metric: sortino_ratio
minimize_metric: false

# Parameter ranges - small for testing
rsi_period_min: 12
rsi_period_max: 16
rsi_period_step: 2

rsi_threshold_min: 25
rsi_threshold_max: 30
rsi_threshold_step: 2.5

stop_loss_pct_min: 0.01
stop_loss_pct_max: 0.03
stop_loss_pct_step: 0.01

# Fixed parameters
accounting_mode: mark-to-market
position_sizing_strategy: fixed-percent
position_size_pct: 0.05
max_concurrent_positions: 3

# Overfitting prevention settings
min_trades_per_combination: 20
max_parameters_optimized: 3
out_of_sample_decay_threshold: 0.25
statistical_significance_p: 0.05
max_parallel_runs: 2
timeout_minutes_per_run: 5
"""
        
        self.config_file = self.test_dir / 'test_optimization_config.md'
        with open(self.config_file, 'w') as f:
            f.write(self.config_content)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_walkforward_validator_initialization(self):
        """Test WalkForwardValidator initialization and configuration"""
        
        config = {
            'training_period_months': 12,
            'validation_period_months': 3,
            'rolling_step_months': 2,
            'min_validation_windows': 3,
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'primary_metric': 'sortino_ratio',
            'min_trades_per_combination': 20,
            'statistical_significance_p': 0.05,
            'out_of_sample_decay_threshold': 0.25
        }
        
        validator = WalkForwardValidator(config)
        
        assert validator.training_months == 12
        assert validator.validation_months == 3
        assert validator.rolling_step_months == 2
        assert validator.min_windows == 3
        assert validator.min_trades == 20
    
    def test_walkforward_window_generation(self):
        """Test validation window generation"""
        
        config = {
            'training_period_months': 12,
            'validation_period_months': 3,
            'rolling_step_months': 2,
            'min_validation_windows': 3,
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'primary_metric': 'sortino_ratio',
            'min_trades_per_combination': 20,
            'statistical_significance_p': 0.05,
            'out_of_sample_decay_threshold': 0.25
        }
        
        validator = WalkForwardValidator(config)
        windows = validator.generate_validation_windows()
        
        # Should generate at least the minimum required windows
        assert len(windows) >= 3
        
        # Check window structure
        for window in windows:
            assert hasattr(window, 'window_id')
            assert hasattr(window, 'training_start')
            assert hasattr(window, 'training_end')
            assert hasattr(window, 'validation_start')
            assert hasattr(window, 'validation_end')
            
            # Validation should start after training ends
            training_end = datetime.strptime(window.training_end, '%Y-%m-%d')
            validation_start = datetime.strptime(window.validation_start, '%Y-%m-%d')
            assert training_end <= validation_start
    
    def test_parameter_combination_validation(self):
        """Test parameter combination validation with mock data"""
        
        config = {
            'training_period_months': 12,
            'validation_period_months': 3,
            'rolling_step_months': 3,
            'min_validation_windows': 2,
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'primary_metric': 'sortino_ratio',
            'min_trades_per_combination': 20,
            'statistical_significance_p': 0.05,
            'out_of_sample_decay_threshold': 0.25
        }
        
        validator = WalkForwardValidator(config)
        windows = validator.generate_validation_windows()
        
        # Create test parameter combination
        combination = ParameterCombination(
            combination_id='test_001',
            parameters={'rsi_period': 14, 'rsi_threshold': 30},
            parameter_hash='test_hash'
        )
        
        # Validate combination (uses mock backtest results)
        result = validator.validate_parameter_combination(combination, windows)
        
        assert result.combination_id == 'test_001'
        assert result.parameters == {'rsi_period': 14, 'rsi_threshold': 30}
        assert len(result.window_results) == len(windows)
        assert 'sortino_ratio_mean' in result.aggregate_metrics
        assert 0 <= result.stability_score <= 1
        assert result.overfitting_risk in ['low', 'medium', 'high']
    
    def test_overfitting_detector_initialization(self):
        """Test OverfittingDetector initialization"""
        
        config = {
            'max_parameters_optimized': 3,
            'min_trades_per_combination': 20,
            'out_of_sample_decay_threshold': 0.25,
            'statistical_significance_p': 0.05,
            'primary_metric': 'sortino_ratio'
        }
        
        detector = OverfittingDetector(config)
        
        assert detector.max_parameters == 3
        assert detector.min_trades == 20
        assert detector.decay_threshold == 0.25
        assert detector.significance_p == 0.05
    
    def test_overfitting_risk_assessment(self):
        """Test overfitting risk assessment"""
        
        config = {
            'max_parameters_optimized': 3,
            'min_trades_per_combination': 20,
            'out_of_sample_decay_threshold': 0.25,
            'statistical_significance_p': 0.05,
            'primary_metric': 'sortino_ratio'
        }
        
        detector = OverfittingDetector(config)
        
        # Create mock validation results
        mock_validation_results = [
            {
                'training_period': {'metrics': {'sortino_ratio': 2.0}},
                'validation_period': {'metrics': {'sortino_ratio': 1.8}},
                'validation_trades': 35
            },
            {
                'training_period': {'metrics': {'sortino_ratio': 1.9}},
                'validation_period': {'metrics': {'sortino_ratio': 1.7}},
                'validation_trades': 32
            }
        ]
        
        mock_aggregate = {'total_validation_trades': 67}
        mock_params = {'rsi_period': 14, 'rsi_threshold': 30}
        
        assessment = detector.assess_overfitting_risk(
            'test_001', mock_params, mock_validation_results, mock_aggregate
        )
        
        assert assessment.combination_id == 'test_001'
        assert assessment.risk_level in ['low', 'medium', 'high']
        assert 0 <= assessment.risk_score <= 1
        assert isinstance(assessment.warning_flags, list)
        assert isinstance(assessment.statistical_tests, dict)
        assert isinstance(assessment.recommendations, list)
    
    def test_optimization_orchestrator_initialization(self):
        """Test OptimizationOrchestrator initialization"""
        
        # Change to test directory so relative paths work
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            assert orchestrator.config['study_name'] == 'Test RSI Optimization'
            assert orchestrator.config['search_strategy'] == 'random'
            assert orchestrator.config['max_combinations'] == 10
            assert orchestrator.study_id.startswith('Test_RSI_Optimization_')
            assert orchestrator.study_dir.exists()
            
        finally:
            os.chdir(original_cwd)
    
    def test_parameter_combination_generation(self):
        """Test parameter combination generation"""
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            # Extract parameter ranges
            param_ranges = orchestrator._extract_parameter_ranges()
            
            assert 'rsi_period' in param_ranges
            assert 'rsi_threshold' in param_ranges
            assert 'stop_loss_pct' in param_ranges
            
            # Check range definitions
            rsi_range = param_ranges['rsi_period']
            assert rsi_range['min'] == 12
            assert rsi_range['max'] == 16
            assert rsi_range['step'] == 2
            
            # Generate combinations
            combinations = orchestrator._generate_parameter_combinations()
            
            assert len(combinations) <= 10  # Max combinations
            assert all(hasattr(c, 'combination_id') for c in combinations)
            assert all(hasattr(c, 'parameters') for c in combinations)
            assert all(hasattr(c, 'parameter_hash') for c in combinations)
            
            # Check parameter values are within ranges
            for combo in combinations:
                assert param_ranges['rsi_period']['min'] <= combo.parameters['rsi_period'] <= param_ranges['rsi_period']['max']
                assert param_ranges['rsi_threshold']['min'] <= combo.parameters['rsi_threshold'] <= param_ranges['rsi_threshold']['max']
                
        finally:
            os.chdir(original_cwd)
    
    def test_grid_search_generation(self):
        """Test grid search parameter generation"""
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            # Small parameter ranges for grid test
            param_ranges = {
                'rsi_period': {'min': 12, 'max': 14, 'step': 2},  # 2 values: 12, 14
                'rsi_threshold': {'min': 25, 'max': 30, 'step': 5}  # 2 values: 25, 30
            }
            
            combinations = orchestrator._generate_grid_combinations(param_ranges)
            
            # Should generate 2 × 2 = 4 combinations
            assert len(combinations) == 4
            
            # Check all combinations are unique
            param_sets = [tuple(sorted(c.parameters.items())) for c in combinations]
            assert len(set(param_sets)) == len(combinations)
            
        finally:
            os.chdir(original_cwd)
    
    def test_random_search_generation(self):
        """Test random search parameter generation"""
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            param_ranges = {
                'rsi_period': {'min': 10, 'max': 20, 'step': 1},
                'rsi_threshold': {'min': 20, 'max': 40, 'step': 1}
            }
            
            combinations = orchestrator._generate_random_combinations(param_ranges, 5)
            
            assert len(combinations) == 5
            
            # Check parameter values are within ranges
            for combo in combinations:
                assert 10 <= combo.parameters['rsi_period'] <= 20
                assert 20 <= combo.parameters['rsi_threshold'] <= 40
                
        finally:
            os.chdir(original_cwd)
    
    def test_validation_results_export(self):
        """Test validation results export functionality"""
        
        config = {
            'training_period_months': 12,
            'validation_period_months': 3,
            'rolling_step_months': 3,
            'min_validation_windows': 2,
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'primary_metric': 'sortino_ratio',
            'min_trades_per_combination': 20,
            'statistical_significance_p': 0.05,
            'out_of_sample_decay_threshold': 0.25
        }
        
        validator = WalkForwardValidator(config)
        
        # Create mock validation results
        mock_results = []
        for i in range(3):
            result = type('MockResult', (), {
                'combination_id': f'test_{i:03d}',
                'parameters': {'rsi_period': 14 + i, 'rsi_threshold': 30},
                'window_results': [
                    {
                        'window_id': 'window_001',
                        'training_period': {'metrics': {'sortino_ratio': 1.8 + i * 0.1}},
                        'validation_period': {'metrics': {'sortino_ratio': 1.7 + i * 0.1}},
                        'validation_trades': 30 + i * 5
                    }
                ],
                'aggregate_metrics': {f'{config["primary_metric"]}_mean': 1.7 + i * 0.1},
                'stability_score': 0.8 - i * 0.1,
                'overfitting_risk': ['low', 'medium', 'high'][i],
                'statistical_significance': {'mean_significant': True}
            })()
            mock_results.append(result)
        
        # Export results
        export_dir = self.test_dir / 'validation_results'
        exported_files = validator.export_validation_results(mock_results, export_dir)
        
        # Check exported files exist
        assert 'walkforward_results' in exported_files
        assert 'validation_summary' in exported_files
        assert 'robustness_analysis' in exported_files
        
        # Check file contents
        walkforward_file = Path(exported_files['walkforward_results'])
        assert walkforward_file.exists()
        
        with open(walkforward_file, 'r') as f:
            data = json.load(f)
        
        assert 'study_metadata' in data
        assert 'validation_results' in data
        assert len(data['validation_results']) == 3
    
    def test_overfitting_analysis_export(self):
        """Test overfitting analysis export functionality"""
        
        config = {
            'max_parameters_optimized': 3,
            'min_trades_per_combination': 20,
            'out_of_sample_decay_threshold': 0.25,
            'statistical_significance_p': 0.05,
            'primary_metric': 'sortino_ratio'
        }
        
        detector = OverfittingDetector(config)
        
        # Create mock assessments
        mock_assessments = []
        for i in range(3):
            assessment = type('MockAssessment', (), {
                'combination_id': f'test_{i:03d}',
                'risk_level': ['low', 'medium', 'high'][i],
                'risk_score': i * 0.3,
                'warning_flags': [f'warning_{i}'],
                'statistical_tests': {'test': i},
                'recommendations': [f'recommendation_{i}']
            })()
            mock_assessments.append(assessment)
        
        # Export analysis
        export_dir = self.test_dir / 'overfitting_analysis'
        analysis_file = detector.export_overfitting_analysis(mock_assessments, export_dir)
        
        assert Path(analysis_file).exists()
        
        # Check file contents
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        
        assert 'study_overview' in data
        assert 'risk_distribution' in data
        assert 'detailed_assessments' in data
        assert len(data['detailed_assessments']) == 3
    
    def test_configuration_validation(self):
        """Test configuration validation logic"""
        
        # Create configuration with insufficient data range
        invalid_config = self.config_content.replace(
            'end_date: 2023-12-31', 
            'end_date: 2022-06-01'  # Only 5 months of data
        )
        
        invalid_config_file = self.test_dir / 'invalid_config.md'
        with open(invalid_config_file, 'w') as f:
            f.write(invalid_config)
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            with pytest.raises(ValueError, match="Insufficient data range"):
                orchestrator = OptimizationOrchestrator(invalid_config_file)
                orchestrator._validate_configuration()
                
        finally:
            os.chdir(original_cwd)
    
    def test_study_manifest_generation(self):
        """Test study manifest generation"""
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            # Generate mock combinations
            combinations = [
                ParameterCombination(
                    combination_id=f'test_{i:03d}',
                    parameters={'rsi_period': 14, 'rsi_threshold': 30},
                    parameter_hash=f'hash_{i}'
                ) for i in range(5)
            ]
            
            manifest = orchestrator._generate_study_manifest(combinations)
            
            assert 'study_metadata' in manifest
            assert 'optimization_configuration' in manifest
            assert 'parameter_space' in manifest
            assert 'validation_methodology' in manifest
            assert 'execution_summary' in manifest
            
            # Check specific values
            assert manifest['study_metadata']['study_name'] == 'Test RSI Optimization'
            assert manifest['parameter_space']['total_combinations_generated'] == 5
            assert manifest['validation_methodology']['method'] == 'walk_forward_analysis'
            
        finally:
            os.chdir(original_cwd)
    
    def run_integration_test(self):
        """Run complete end-to-end integration test"""
        
        print("Running optimization workflow integration test...")
        
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            # Create orchestrator
            orchestrator = OptimizationOrchestrator(self.config_file)
            
            # Override some methods for testing to avoid actual backtest execution
            def mock_execute_parameter_sweep(combinations, windows):
                """Mock parameter sweep execution"""
                mock_results = []
                
                for combo in combinations:
                    # Create mock validation result
                    window_results = []
                    for window in windows:
                        window_result = {
                            'window_id': window.window_id,
                            'training_period': {
                                'start': window.training_start,
                                'end': window.training_end,
                                'metrics': {
                                    'sortino_ratio': np.random.normal(1.8, 0.2),
                                    'total_trades': np.random.randint(25, 45)
                                }
                            },
                            'validation_period': {
                                'start': window.validation_start,
                                'end': window.validation_end,
                                'metrics': {
                                    'sortino_ratio': np.random.normal(1.6, 0.3),
                                    'total_trades': np.random.randint(20, 40)
                                }
                            },
                            'validation_trades': np.random.randint(20, 40)
                        }
                        window_results.append(window_result)
                    
                    # Create mock validation result object
                    result = type('MockValidationResult', (), {
                        'combination_id': combo.combination_id,
                        'parameters': combo.parameters,
                        'window_results': window_results,
                        'aggregate_metrics': {
                            'sortino_ratio_mean': np.mean([w['validation_period']['metrics']['sortino_ratio'] for w in window_results]),
                            'total_validation_trades': sum(w['validation_trades'] for w in window_results)
                        },
                        'stability_score': np.random.uniform(0.5, 0.9),
                        'overfitting_risk': np.random.choice(['low', 'medium', 'high']),
                        'statistical_significance': {'mean_significant': True}
                    })()
                    
                    mock_results.append(result)
                    orchestrator.completed_combinations += 1
                
                return mock_results
            
            # Replace the method
            orchestrator._execute_parameter_sweep = mock_execute_parameter_sweep
            
            # Execute optimization study
            results_dir = orchestrator.execute_optimization_study()
            
            # Verify results
            results_path = Path(results_dir)
            assert results_path.exists()
            
            # Check required files were created
            required_files = [
                'optimization_summary.json',
                'parameter_sweep.csv',
                'walkforward_results.json',
                'robustness_analysis.json',
                'overfitting_analysis.json',
                'study_manifest.json',
                'optimization.log'
            ]
            
            for file_name in required_files:
                file_path = results_path / file_name
                assert file_path.exists(), f"Missing required file: {file_name}"
                
                # Check file is not empty
                assert file_path.stat().st_size > 0, f"Empty file: {file_name}"
            
            # Validate JSON files can be loaded
            json_files = [f for f in required_files if f.endswith('.json')]
            for json_file in json_files:
                with open(results_path / json_file, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, dict), f"Invalid JSON structure in {json_file}"
            
            print("Integration test completed successfully!")
            return True
            
        except Exception as e:
            print(f"Integration test failed: {e}")
            return False
            
        finally:
            os.chdir(original_cwd)


def run_all_tests():
    """Run all optimization workflow tests"""
    
    print("Starting optimization workflow test suite...")
    
    test_suite = TestOptimizationWorkflow()
    
    tests = [
        'test_walkforward_validator_initialization',
        'test_walkforward_window_generation',
        'test_parameter_combination_validation',
        'test_overfitting_detector_initialization',
        'test_overfitting_risk_assessment',
        'test_optimization_orchestrator_initialization',
        'test_parameter_combination_generation',
        'test_grid_search_generation',
        'test_random_search_generation',
        'test_validation_results_export',
        'test_overfitting_analysis_export',
        'test_configuration_validation',
        'test_study_manifest_generation'
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name in tests:
        try:
            print(f"Running {test_name}...")
            test_suite.setup_method()
            getattr(test_suite, test_name)()
            test_suite.teardown_method()
            print(f"✓ {test_name} passed")
            passed_tests += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            failed_tests += 1
            test_suite.teardown_method()
    
    # Run integration test
    try:
        print("Running integration test...")
        test_suite.setup_method()
        success = test_suite.run_integration_test()
        test_suite.teardown_method()
        
        if success:
            print("✓ Integration test passed")
            passed_tests += 1
        else:
            print("✗ Integration test failed")
            failed_tests += 1
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        failed_tests += 1
        test_suite.teardown_method()
    
    print(f"\nTest Results: {passed_tests} passed, {failed_tests} failed")
    
    if failed_tests == 0:
        print("All tests passed! Optimization workflow is ready for production.")
    else:
        print("Some tests failed. Please review and fix issues before deployment.")
    
    return failed_tests == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)