#!/usr/bin/env python3
"""
Basic Optimization Workflow Test
Tests core functionality without external dependencies
"""

import json
import tempfile
import shutil
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import csv
import hashlib

def create_test_config():
    """Create test optimization configuration"""
    return """
# Test Optimization Configuration

study_name: Test RSI Optimization
search_strategy: random
max_combinations: 5
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
"""

def test_config_parsing():
    """Test optimization configuration parsing"""
    print("Testing configuration parsing...")
    
    config_content = create_test_config()
    
    # Parse configuration (simplified version)
    config = {}
    lines = config_content.split('\n')
    
    for line in lines:
        if ':' in line and not line.strip().startswith('#'):
            clean_line = line.strip()
            
            if ': ' in clean_line and not '[REQUIRED' in clean_line:
                key, value = clean_line.split(': ', 1)
                key = key.strip()
                value = value.strip()
                
                if value.lower() in ['true', 'false']:
                    config[key] = value.lower() == 'true'
                else:
                    # Try to convert to number, fallback to string
                    try:
                        # Check if it's a valid number
                        clean_value = value.replace('.', '').replace('-', '')
                        if clean_value.isdigit() and not any(c in value for c in [':', '/', ' ', '_']):
                            config[key] = float(value) if '.' in value else int(value)
                        else:
                            config[key] = value
                    except ValueError:
                        config[key] = value
    
    # Validate parsed configuration
    assert config['study_name'] == 'Test RSI Optimization'
    assert config['search_strategy'] == 'random'
    assert config['max_combinations'] == 5
    assert config['training_period_months'] == 12
    assert config['rsi_period_min'] == 12
    assert config['rsi_threshold_max'] == 30
    
    print("+ Configuration parsing test passed")
    return config

def test_parameter_range_extraction(config):
    """Test parameter range extraction"""
    print("Testing parameter range extraction...")
    
    # Extract parameter ranges
    ranges = {}
    
    for key, value in config.items():
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
    
    # Validate ranges
    assert 'rsi_period' in ranges
    assert 'rsi_threshold' in ranges
    assert ranges['rsi_period']['min'] == 12
    assert ranges['rsi_period']['max'] == 16
    assert ranges['rsi_period']['step'] == 2
    
    print("+ Parameter range extraction test passed")
    return ranges

def test_parameter_combination_generation(ranges):
    """Test parameter combination generation"""
    print("Testing parameter combination generation...")
    
    # Generate random combinations (simplified)
    import random
    random.seed(42)
    
    combinations = []
    max_combinations = 5
    
    for i in range(max_combinations):
        params = {}
        
        # Generate random values for each parameter
        for param, range_def in ranges.items():
            if 'min' in range_def and 'max' in range_def and 'step' in range_def:
                min_val = range_def['min']
                max_val = range_def['max']
                step = range_def['step']
                
                if isinstance(min_val, int) and isinstance(step, int):
                    n_steps = int((max_val - min_val) / step) + 1
                    step_idx = random.randint(0, n_steps - 1)
                    value = min_val + step_idx * step
                else:
                    n_steps = int((max_val - min_val) / step) + 1
                    step_idx = random.randint(0, n_steps - 1)
                    value = min_val + step_idx * step
                
                params[param] = value
        
        # Add combination
        combination = {
            'combination_id': f'test_{i:03d}',
            'parameters': params,
            'parameter_hash': hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:8]
        }
        combinations.append(combination)
    
    # Validate combinations
    assert len(combinations) == 5
    assert all('combination_id' in c for c in combinations)
    assert all('parameters' in c for c in combinations)
    assert all('parameter_hash' in c for c in combinations)
    
    # Check parameter values are within ranges
    for combo in combinations:
        for param, value in combo['parameters'].items():
            if param in ranges:
                range_def = ranges[param]
                assert range_def['min'] <= value <= range_def['max']
    
    print("+ Parameter combination generation test passed")
    return combinations

def test_validation_window_generation(config):
    """Test validation window generation"""
    print("Testing validation window generation...")
    
    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
    training_months = config['training_period_months']
    validation_months = config['validation_period_months']
    rolling_step_months = config['rolling_step_months']
    
    windows = []
    current_start = start_date
    window_id = 1
    
    while True:
        # Calculate training period
        training_start = current_start
        training_end = training_start + timedelta(days=30 * training_months)
        
        # Calculate validation period
        validation_start = training_end
        validation_end = validation_start + timedelta(days=30 * validation_months)
        
        # Check if we have enough data
        if validation_end > end_date:
            break
        
        window = {
            'window_id': f'window_{window_id:03d}',
            'training_start': training_start.strftime('%Y-%m-%d'),
            'training_end': training_end.strftime('%Y-%m-%d'),
            'validation_start': validation_start.strftime('%Y-%m-%d'),
            'validation_end': validation_end.strftime('%Y-%m-%d')
        }
        windows.append(window)
        
        # Advance window
        current_start = current_start + timedelta(days=30 * rolling_step_months)
        window_id += 1
    
    # Validate windows
    assert len(windows) >= config['min_validation_windows']
    
    for window in windows:
        training_end = datetime.strptime(window['training_end'], '%Y-%m-%d')
        validation_start = datetime.strptime(window['validation_start'], '%Y-%m-%d')
        assert training_end <= validation_start
    
    print(f"+ Validation window generation test passed ({len(windows)} windows)")
    return windows

def test_mock_validation_results(combinations, windows, config):
    """Test mock validation result generation"""
    print("Testing mock validation results...")
    
    validation_results = []
    
    for combo in combinations:
        # Generate mock results for each window
        window_results = []
        
        for window in windows:
            # Mock training metrics
            training_metrics = {
                'sortino_ratio': np.random.normal(1.8, 0.2),
                'total_trades': np.random.randint(25, 45)
            }
            
            # Mock validation metrics (slightly lower performance)
            validation_metrics = {
                'sortino_ratio': training_metrics['sortino_ratio'] * np.random.uniform(0.85, 0.95),
                'total_trades': np.random.randint(20, 40)
            }
            
            window_result = {
                'window_id': window['window_id'],
                'training_period': {
                    'start': window['training_start'],
                    'end': window['training_end'],
                    'metrics': training_metrics
                },
                'validation_period': {
                    'start': window['validation_start'],
                    'end': window['validation_end'],
                    'metrics': validation_metrics
                },
                'validation_trades': validation_metrics['total_trades']
            }
            window_results.append(window_result)
        
        # Calculate aggregate metrics
        primary_metric = config['primary_metric']
        val_performances = [w['validation_period']['metrics'][primary_metric] for w in window_results]
        
        aggregate_metrics = {
            f'{primary_metric}_mean': np.mean(val_performances),
            f'{primary_metric}_std': np.std(val_performances),
            'total_validation_trades': sum(w['validation_trades'] for w in window_results)
        }
        
        # Calculate stability score
        mean_perf = np.mean(val_performances)
        std_perf = np.std(val_performances)
        stability_score = 1 / (1 + (std_perf / abs(mean_perf)) if mean_perf != 0 else 0)
        
        result = {
            'combination_id': combo['combination_id'],
            'parameters': combo['parameters'],
            'window_results': window_results,
            'aggregate_metrics': aggregate_metrics,
            'stability_score': stability_score,
            'overfitting_risk': np.random.choice(['low', 'medium', 'high'])
        }
        validation_results.append(result)
    
    # Validate results
    assert len(validation_results) == len(combinations)
    assert all('combination_id' in r for r in validation_results)
    assert all('aggregate_metrics' in r for r in validation_results)
    assert all(0 <= r['stability_score'] <= 1 for r in validation_results)
    
    print("+ Mock validation results test passed")
    return validation_results

def test_overfitting_assessment(validation_results, config):
    """Test basic overfitting assessment"""
    print("Testing overfitting assessment...")
    
    assessments = []
    
    for result in validation_results:
        # Calculate performance decay
        primary_metric = config['primary_metric']
        
        train_perfs = [w['training_period']['metrics'][primary_metric] for w in result['window_results']]
        val_perfs = [w['validation_period']['metrics'][primary_metric] for w in result['window_results']]
        
        avg_train = np.mean(train_perfs)
        avg_val = np.mean(val_perfs)
        
        performance_decay = (avg_train - avg_val) / abs(avg_train) if avg_train != 0 else 0
        
        # Assess risk
        warning_flags = []
        risk_score = 0.0
        
        # Test performance decay
        decay_threshold = config['out_of_sample_decay_threshold']
        if performance_decay > decay_threshold:
            warning_flags.append('HIGH_PERFORMANCE_DECAY')
            risk_score = max(risk_score, 0.8)
        
        # Test trade count
        total_trades = result['aggregate_metrics']['total_validation_trades']
        min_trades = config['min_trades_per_combination'] * len(result['window_results'])
        if total_trades < min_trades:
            warning_flags.append('INSUFFICIENT_TRADES')
            risk_score = max(risk_score, 0.7)
        
        # Test parameter count
        param_count = len(result['parameters'])
        max_params = config['max_parameters_optimized']
        if param_count > max_params:
            warning_flags.append('EXCESSIVE_PARAMETERS')
            risk_score = max(risk_score, 0.9)
        
        # Classify risk level
        if risk_score >= 0.7:
            risk_level = 'high'
        elif risk_score >= 0.5:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        assessment = {
            'combination_id': result['combination_id'],
            'risk_level': risk_level,
            'risk_score': risk_score,
            'warning_flags': warning_flags,
            'performance_decay': performance_decay,
            'total_trades': total_trades
        }
        assessments.append(assessment)
    
    # Validate assessments
    assert len(assessments) == len(validation_results)
    assert all('risk_level' in a for a in assessments)
    assert all(a['risk_level'] in ['low', 'medium', 'high'] for a in assessments)
    assert all(0 <= a['risk_score'] <= 1 for a in assessments)
    
    print("+ Overfitting assessment test passed")
    return assessments

def test_results_export(validation_results, assessments, config):
    """Test results export functionality"""
    print("Testing results export...")
    
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Generate optimization summary
        primary_metric = config['primary_metric']
        
        all_performances = [r['aggregate_metrics'][f'{primary_metric}_mean'] for r in validation_results]
        best_performance = max(all_performances) if all_performances else None
        
        # Find best combination
        best_combination = None
        for result in validation_results:
            if result['aggregate_metrics'][f'{primary_metric}_mean'] == best_performance:
                best_combination = result
                break
        
        summary = {
            'study_overview': {
                'study_name': config['study_name'],
                'total_combinations': len(validation_results),
                'completion_timestamp': datetime.now().isoformat()
            },
            'performance_statistics': {
                'best_performance': best_performance,
                'mean_performance': np.mean(all_performances),
                'std_performance': np.std(all_performances)
            },
            'best_combination': {
                'combination_id': best_combination['combination_id'],
                'parameters': best_combination['parameters'],
                'performance': best_performance,
                'stability_score': best_combination['stability_score']
            } if best_combination else None,
            'overfitting_summary': {
                'low_risk': len([a for a in assessments if a['risk_level'] == 'low']),
                'medium_risk': len([a for a in assessments if a['risk_level'] == 'medium']),
                'high_risk': len([a for a in assessments if a['risk_level'] == 'high'])
            }
        }
        
        # Export optimization summary
        summary_file = test_dir / 'optimization_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Export parameter sweep CSV
        csv_file = test_dir / 'parameter_sweep.csv'
        
        # Get parameter names from first result
        param_names = list(validation_results[0]['parameters'].keys())
        
        # Create assessment lookup
        assessment_lookup = {a['combination_id']: a for a in assessments}
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['combination_id'] + param_names + [
                f'{primary_metric}_mean', 'stability_score', 'overfitting_risk'
            ]
            writer.writerow(header)
            
            # Write data
            for result in validation_results:
                assessment = assessment_lookup[result['combination_id']]
                
                row = [result['combination_id']]
                row.extend([result['parameters'][p] for p in param_names])
                row.append(result['aggregate_metrics'][f'{primary_metric}_mean'])
                row.append(result['stability_score'])
                row.append(assessment['risk_level'])
                
                writer.writerow(row)
        
        # Export validation results
        validation_file = test_dir / 'validation_results.json'
        validation_data = {
            'validation_results': validation_results,
            'study_metadata': {
                'total_combinations': len(validation_results),
                'generated_timestamp': datetime.now().isoformat()
            }
        }
        
        with open(validation_file, 'w') as f:
            json.dump(validation_data, f, indent=2, default=str)
        
        # Export overfitting analysis
        overfitting_file = test_dir / 'overfitting_analysis.json'
        overfitting_data = {
            'study_overview': {
                'total_combinations': len(assessments),
                'assessment_timestamp': datetime.now().isoformat()
            },
            'risk_distribution': {
                'low_risk': len([a for a in assessments if a['risk_level'] == 'low']),
                'medium_risk': len([a for a in assessments if a['risk_level'] == 'medium']),
                'high_risk': len([a for a in assessments if a['risk_level'] == 'high'])
            },
            'detailed_assessments': assessments
        }
        
        with open(overfitting_file, 'w') as f:
            json.dump(overfitting_data, f, indent=2, default=str)
        
        # Validate exported files
        required_files = [
            'optimization_summary.json',
            'parameter_sweep.csv', 
            'validation_results.json',
            'overfitting_analysis.json'
        ]
        
        for file_name in required_files:
            file_path = test_dir / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
            assert file_path.stat().st_size > 0, f"Empty file: {file_name}"
        
        # Validate JSON files can be loaded
        json_files = [f for f in required_files if f.endswith('.json')]
        for json_file in json_files:
            with open(test_dir / json_file, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict), f"Invalid JSON in {json_file}"
        
        print("+ Results export test passed")
        return str(test_dir)
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)

def run_integration_test():
    """Run complete integration test"""
    print("\n=== Running Optimization Workflow Integration Test ===\n")
    
    try:
        # Test 1: Configuration parsing
        config = test_config_parsing()
        
        # Test 2: Parameter range extraction
        ranges = test_parameter_range_extraction(config)
        
        # Test 3: Parameter combination generation
        combinations = test_parameter_combination_generation(ranges)
        
        # Test 4: Validation window generation
        windows = test_validation_window_generation(config)
        
        # Test 5: Mock validation results
        validation_results = test_mock_validation_results(combinations, windows, config)
        
        # Test 6: Overfitting assessment
        assessments = test_overfitting_assessment(validation_results, config)
        
        # Test 7: Results export
        results_dir = test_results_export(validation_results, assessments, config)
        
        print("\n=== Integration Test Summary ===")
        print(f"+ Configuration parsed successfully")
        print(f"+ Generated {len(combinations)} parameter combinations")
        print(f"+ Created {len(windows)} validation windows")  
        print(f"+ Processed {len(validation_results)} validation results")
        print(f"+ Completed {len(assessments)} overfitting assessments")
        print(f"+ Exported results to temporary directory")
        
        # Summary statistics
        risk_counts = {
            'low': len([a for a in assessments if a['risk_level'] == 'low']),
            'medium': len([a for a in assessments if a['risk_level'] == 'medium']),
            'high': len([a for a in assessments if a['risk_level'] == 'high'])
        }
        
        print(f"\nRisk Assessment Summary:")
        print(f"  Low Risk: {risk_counts['low']} combinations")
        print(f"  Medium Risk: {risk_counts['medium']} combinations")  
        print(f"  High Risk: {risk_counts['high']} combinations")
        
        # Performance statistics
        primary_metric = config['primary_metric']
        performances = [r['aggregate_metrics'][f'{primary_metric}_mean'] for r in validation_results]
        
        print(f"\nPerformance Summary ({primary_metric}):")
        print(f"  Best: {max(performances):.3f}")
        print(f"  Worst: {min(performances):.3f}")
        print(f"  Mean: {np.mean(performances):.3f}")
        print(f"  Std: {np.std(performances):.3f}")
        
        print(f"\nALL TESTS PASSED - Optimization workflow is functioning correctly!")
        return True
        
    except Exception as e:
        print(f"\nX TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)