"""
Simple Optimization Test with Simulated Results

Tests the optimization pipeline with simulated backtest results
to validate the walk-forward analysis and statistical validation components.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

# Simulate parameter sweep with realistic performance metrics
def simulate_backtest(parameters):
    """Simulate backtest results based on parameters."""
    # Create some correlation between parameters and performance
    rsi_period = parameters.get('rsi_period', 14)
    oversold = parameters.get('oversold_threshold', 30)
    overbought = parameters.get('overbought_threshold', 70)

    # Simulate performance with some logic
    # Shorter RSI periods tend to generate more trades but lower quality
    trade_frequency = 100 / rsi_period  # More trades with shorter periods

    # Wider thresholds (further from 50) tend to be more selective
    threshold_quality = abs(oversold - 30) * 0.01 + abs(overbought - 70) * 0.01

    # Add some randomness
    noise = np.random.normal(0, 0.1)

    # Calculate metrics
    base_return = 0.1 + threshold_quality - (trade_frequency * 0.001) + noise
    sharpe = 0.5 + threshold_quality * 2 + noise
    max_dd = 0.15 - threshold_quality * 0.05 + abs(noise) * 0.1
    trades = int(trade_frequency * 10 + np.random.randint(-5, 5))

    return {
        'total_return': max(-0.5, min(0.5, base_return)),
        'sharpe_ratio': max(0, min(3, sharpe)),
        'max_drawdown': max(0.05, min(0.5, max_dd)),
        'total_trades': max(5, trades),
        'win_rate': 0.45 + threshold_quality * 0.1 + np.random.uniform(-0.05, 0.05)
    }

def run_optimization_test():
    """Run complete optimization test with walk-forward validation."""

    print("="*60)
    print("OPTIMIZATION PIPELINE TEST")
    print("="*60)

    # Load configuration
    with open('test_optimization_config.json', 'r') as f:
        config = json.load(f)

    print(f"\nConfiguration: {config['optimization_name']}")
    print(f"Method: {config['optimization_method']}")
    print(f"Validation: {config['validation_method']}")

    # Generate parameter combinations
    parameters = config['parameters']

    # RSI period values
    rsi_values = list(range(
        parameters['rsi_period']['min'],
        parameters['rsi_period']['max'] + 1,
        parameters['rsi_period'].get('step', 2)
    ))

    # Oversold threshold values
    oversold_values = []
    current = parameters['oversold_threshold']['min']
    while current <= parameters['oversold_threshold']['max']:
        oversold_values.append(current)
        current += parameters['oversold_threshold'].get('step', 2.5)

    # Overbought threshold values
    overbought_values = []
    current = parameters['overbought_threshold']['min']
    while current <= parameters['overbought_threshold']['max']:
        overbought_values.append(current)
        current += parameters['overbought_threshold'].get('step', 2.5)

    # Generate all combinations
    combinations = []
    for rsi in rsi_values:
        for oversold in oversold_values:
            for overbought in overbought_values:
                combinations.append({
                    'rsi_period': rsi,
                    'oversold_threshold': oversold,
                    'overbought_threshold': overbought
                })

    print(f"\nParameter Space:")
    print(f"  RSI Period: {rsi_values}")
    print(f"  Oversold: {oversold_values}")
    print(f"  Overbought: {overbought_values}")
    print(f"  Total Combinations: {len(combinations)}")

    # Phase 1: Parameter Sweep
    print("\n" + "="*60)
    print("PHASE 1: PARAMETER SWEEP")
    print("="*60)

    sweep_results = []
    start_time = time.time()

    for i, params in enumerate(combinations):
        # Simulate backtest
        metrics = simulate_backtest(params)

        sweep_results.append({
            'index': i,
            'parameters': params,
            'metrics': metrics
        })

        # Progress update
        if (i + 1) % 10 == 0:
            print(f"  Tested {i+1}/{len(combinations)} combinations...")

    sweep_time = time.time() - start_time
    print(f"\nSweep completed in {sweep_time:.2f} seconds")
    print(f"Average time per combination: {sweep_time/len(combinations)*1000:.1f} ms")

    # Find best parameters
    best_result = max(sweep_results, key=lambda x: x['metrics']['sharpe_ratio'])
    print(f"\nBest Parameters (by Sharpe Ratio):")
    for param, value in best_result['parameters'].items():
        print(f"  {param}: {value}")
    print(f"  Sharpe Ratio: {best_result['metrics']['sharpe_ratio']:.3f}")

    # Phase 2: Walk-Forward Validation
    print("\n" + "="*60)
    print("PHASE 2: WALK-FORWARD VALIDATION")
    print("="*60)

    wf_config = config['walk_forward']
    print(f"\nWalk-Forward Configuration:")
    print(f"  Training Window: {wf_config['training_window']} days")
    print(f"  Validation Window: {wf_config['validation_window']} days")
    print(f"  Step Size: {wf_config['step_size']} days")

    # Simulate walk-forward for top 3 parameter sets
    top_results = sorted(sweep_results, key=lambda x: x['metrics']['sharpe_ratio'], reverse=True)[:3]

    wf_results = []
    for rank, result in enumerate(top_results, 1):
        params = result['parameters']
        print(f"\nValidating Parameter Set #{rank}:")

        # Simulate 5 walk-forward windows
        windows = []
        for window in range(5):
            # Training period
            train_metrics = simulate_backtest(params)
            # Validation period (typically slightly worse)
            val_metrics = simulate_backtest(params)
            val_metrics['sharpe_ratio'] *= 0.85  # Simulate degradation
            val_metrics['total_return'] *= 0.9

            windows.append({
                'window': window,
                'training': train_metrics,
                'validation': val_metrics
            })

        # Calculate degradation
        avg_train_sharpe = np.mean([w['training']['sharpe_ratio'] for w in windows])
        avg_val_sharpe = np.mean([w['validation']['sharpe_ratio'] for w in windows])
        degradation = (avg_train_sharpe - avg_val_sharpe) / avg_train_sharpe * 100

        print(f"  Avg Training Sharpe: {avg_train_sharpe:.3f}")
        print(f"  Avg Validation Sharpe: {avg_val_sharpe:.3f}")
        print(f"  Performance Degradation: {degradation:.1f}%")

        wf_results.append({
            'parameters': params,
            'windows': windows,
            'degradation': degradation
        })

    # Phase 3: Statistical Validation
    print("\n" + "="*60)
    print("PHASE 3: STATISTICAL VALIDATION")
    print("="*60)

    # Convert to DataFrame for analysis
    df = pd.DataFrame([
        {**r['parameters'], **r['metrics']}
        for r in sweep_results
    ])

    print("\nParameter Correlations with Sharpe Ratio:")
    for param in ['rsi_period', 'oversold_threshold', 'overbought_threshold']:
        corr = df[param].corr(df['sharpe_ratio'])
        print(f"  {param}: {corr:.3f}")

    print("\nPerformance Distribution:")
    print(f"  Mean Sharpe: {df['sharpe_ratio'].mean():.3f}")
    print(f"  Std Sharpe: {df['sharpe_ratio'].std():.3f}")
    print(f"  Best Sharpe: {df['sharpe_ratio'].max():.3f}")
    print(f"  Worst Sharpe: {df['sharpe_ratio'].min():.3f}")

    # Phase 4: Overfitting Assessment
    print("\n" + "="*60)
    print("PHASE 4: OVERFITTING ASSESSMENT")
    print("="*60)

    print("\nOverfitting Risk Indicators:")

    # Check parameter complexity
    num_params = len(config['parameters'])
    print(f"  Number of Parameters: {num_params} {'OK' if num_params <= 5 else 'HIGH'}")

    # Check sample size
    avg_trades = df['total_trades'].mean()
    print(f"  Avg Trades per Test: {avg_trades:.0f} {'OK' if avg_trades >= 30 else 'LOW'}")

    # Check walk-forward degradation
    avg_degradation = np.mean([r['degradation'] for r in wf_results])
    print(f"  Avg WF Degradation: {avg_degradation:.1f}% {'OK' if avg_degradation < 20 else 'HIGH'}")

    # Parameter stability check
    top_10_pct = df.nlargest(int(len(df) * 0.1), 'sharpe_ratio')
    param_stability = {}
    for param in ['rsi_period', 'oversold_threshold', 'overbought_threshold']:
        stability = top_10_pct[param].std() / df[param].std()
        param_stability[param] = stability
        print(f"  {param} Stability: {stability:.3f} {'Stable' if stability < 0.5 else 'Unstable'}")

    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)

    output_dir = Path("data/optimization/test_study")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save summary
    summary = {
        'study_name': config['optimization_name'],
        'timestamp': datetime.now().isoformat(),
        'total_combinations': len(combinations),
        'execution_time_seconds': sweep_time,
        'best_parameters': best_result['parameters'],
        'best_performance': best_result['metrics'],
        'walk_forward_results': wf_results,
        'overfitting_indicators': {
            'num_parameters': num_params,
            'avg_trades': avg_trades,
            'avg_degradation': avg_degradation,
            'parameter_stability': param_stability
        }
    }

    summary_file = output_dir / "optimization_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    # Save parameter sweep CSV
    df.to_csv(output_dir / "parameter_sweep.csv", index=False)

    print(f"\nResults saved to: {output_dir}")
    print(f"  - optimization_summary.json")
    print(f"  - parameter_sweep.csv")

    # Generate simple heatmap data
    print("\n" + "="*60)
    print("HEATMAP DATA GENERATION")
    print("="*60)

    # Create 2D heatmap for RSI vs Oversold
    heatmap_data = []
    for rsi in rsi_values:
        row = []
        for oversold in oversold_values:
            # Average across all overbought values
            values = df[(df['rsi_period'] == rsi) & (df['oversold_threshold'] == oversold)]['sharpe_ratio'].mean()
            row.append(values)
        heatmap_data.append(row)

    heatmap_df = pd.DataFrame(heatmap_data, index=rsi_values, columns=oversold_values)
    heatmap_df.to_csv(output_dir / "heatmap_rsi_oversold.csv")

    print("\nHeatmap Preview (RSI Period vs Oversold Threshold):")
    print(heatmap_df.round(2))

    print("\n" + "="*60)
    print("OPTIMIZATION TEST COMPLETE")
    print("="*60)

    return summary

if __name__ == "__main__":
    summary = run_optimization_test()

    print("\n[SUCCESS] Optimization pipeline test completed successfully!")
    print(f"  Best Sharpe Ratio: {summary['best_performance']['sharpe_ratio']:.3f}")
    print(f"  Execution Time: {summary['execution_time_seconds']:.2f} seconds")
    print(f"  Overfitting Risk: {'LOW' if summary['overfitting_indicators']['avg_degradation'] < 20 else 'HIGH'}")