"""
Create test data with accounting discrepancy to test HALT conditions.
This simulates the exact scenario where metrics claim positive returns
but the actual equity shows flat/negative performance.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

def create_discrepancy_test_data(run_id="test_discrepancy_20241210", test_mode=True):
    """Create test run data with intentional discrepancy to test HALT conditions."""
    
    # Determine output directory based on mode
    if test_mode:
        base_dir = Path("data/test_runs") / run_id
    else:
        base_dir = Path("data/runs") / run_id
    
    # Create directories
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "figures").mkdir(exist_ok=True)
    
    # Test parameters
    initial_capital = 100000.0
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)  # 3 months
    num_days = (end_date - start_date).days + 1
    
    # Create timestamps
    timestamps = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # CRITICAL: Create discrepancy scenario
    # Actual equity shows FLAT performance (0% return)
    equity_values = np.ones(num_days) * initial_capital
    actual_final_equity = initial_capital  # Flat
    
    # But metrics will claim POSITIVE return (10%)
    fake_final_equity = initial_capital * 1.10  # +10% claimed
    fake_total_return = 0.10
    
    # Create manifest.json
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "strategy": "RSIMeanReversionStrategy",
        "parameters": {
            "initial_capital": initial_capital,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "status": "completed"
    }
    
    with open(base_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create MISLEADING metrics.json (claims positive return)
    metrics = {
        "performance": {
            "total_return": fake_total_return,  # Claims 10% return
            "cagr": fake_total_return * 4,  # Annualized
            "sharpe_ratio": 1.5,  # Fake good Sharpe
            "sortino_ratio": 2.0,  # Fake good Sortino
            "max_drawdown": -0.02,
            "win_rate": 0.65,
            "profit_factor": 1.8
        },
        "risk": {
            "volatility": 0.15,
            "var_95": -0.02,
            "cvar_95": -0.03
        },
        "execution": {
            "total_trades": 50,
            "winning_trades": 33,
            "losing_trades": 17
        },
        "accounting": {
            "initial_capital": initial_capital,
            "final_equity": fake_final_equity,  # WRONG: Claims 110k
            "total_pnl": fake_final_equity - initial_capital,  # Claims +10k
            "total_fees": 500.0,
            "unrealized_pnl": 0.0,
            "open_positions": 0
        }
    }
    
    with open(base_dir / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Create ACCURATE series.csv (shows flat performance)
    series_data = pd.DataFrame({
        'timestamp': timestamps,
        'equity': equity_values,  # ACTUAL: Flat at 100k
        'drawdown': 0.0,
        'returns': 0.0,
        'positions': 0,
        'exposure': 0.0
    })
    series_data.to_csv(base_dir / "series.csv", index=False)
    
    # Create empty trades.csv
    trades_data = pd.DataFrame({
        'timestamp': [],
        'symbol': [],
        'side': [],
        'quantity': [],
        'price': [],
        'fee': [],
        'pnl': []
    })
    trades_data.to_csv(base_dir / "trades.csv", index=False)
    
    # Create visualization showing FLAT equity (truth)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # Panel 1: Equity Curve (FLAT - the truth)
    ax1 = axes[0]
    ax1.plot(timestamps, equity_values, 'b-', linewidth=1.5, label='Actual Equity')
    ax1.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_ylabel('Equity ($)')
    ax1.set_title(f'DISCREPANCY TEST - Visual shows FLAT, Metrics claim +10%')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([95000, 115000])
    
    # Add text showing the discrepancy
    ax1.text(timestamps[len(timestamps)//2], 112000, 
             'Metrics claim: $110,000 (+10%)', 
             color='red', fontsize=12, ha='center',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax1.text(timestamps[len(timestamps)//2], 102000, 
             'Actual equity: $100,000 (0%)', 
             color='green', fontsize=12, ha='center',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    # Panel 2: Drawdown (none)
    ax2 = axes[1]
    ax2.fill_between(timestamps, 0, 0, color='red', alpha=0.3)
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_ylim([-5, 0])
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Activity
    ax3 = axes[2]
    ax3.bar(timestamps[::10], np.zeros(len(timestamps[::10])), width=1, color='green', alpha=0.5)
    ax3.set_ylabel('Positions')
    ax3.set_xlabel('Date')
    ax3.grid(True, alpha=0.3)
    
    # Format x-axis
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # Save visualization
    fig.savefig(base_dir / "figures" / "main_analysis.png", dpi=150, bbox_inches='tight')
    fig.savefig(base_dir / "figures" / "main_analysis.pdf", bbox_inches='tight')
    plt.close(fig)
    
    print(f"Discrepancy test data created in {base_dir}")
    print(f"DISCREPANCY DETAILS:")
    print(f"  - Metrics claim final equity: ${fake_final_equity:,.2f} (+{fake_total_return:.1%})")
    print(f"  - Actual final equity (series.csv): ${actual_final_equity:,.2f} (0.0%)")
    print(f"  - Visual chart shows: FLAT performance")
    print(f"  - Expected result: EVALUATION SHOULD HALT")
    
    return str(base_dir)

if __name__ == "__main__":
    # Create discrepancy test data
    run_dir = create_discrepancy_test_data(test_mode=True)
    print(f"\nDiscrepancy test created: {run_dir}")
    print("\nRun evaluation to test HALT condition:")
    print("python scripts/single_evaluation/evaluator.py test_discrepancy_20241210 --test")