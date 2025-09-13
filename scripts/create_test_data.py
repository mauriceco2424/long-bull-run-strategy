"""
Create test data for evaluating the single-run evaluator system.
This creates realistic test data with known characteristics to validate
the evaluation system's visual validation and accounting reconciliation.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

def create_test_run_data(run_id="test_20241210_120000", test_mode=True):
    """Create complete test run data with known characteristics."""
    
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
    
    # Scenario: Flat equity with minimal activity (testing 0% return case)
    # This tests our system's ability to detect and validate flat performance
    equity_values = np.ones(num_days) * initial_capital
    # Add tiny variations to make it realistic (±0.01%)
    equity_values += np.random.randn(num_days) * 10
    equity_values = np.maximum(equity_values, initial_capital * 0.95)  # Floor at -5%
    
    # Ensure final equity matches expected (flat performance)
    equity_values[-1] = initial_capital  # Exactly flat
    
    # Calculate metrics
    returns = pd.Series(equity_values).pct_change().fillna(0)
    cumulative_return = (equity_values[-1] / initial_capital) - 1
    
    # Create manifest.json
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "strategy": "RSIMeanReversionStrategy",
        "parameters": {
            "initial_capital": initial_capital,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70
        },
        "universe": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
        "data_source": "test_data",
        "status": "completed"
    }
    
    with open(base_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create metrics.json with consistent values
    metrics = {
        "performance": {
            "total_return": cumulative_return,
            "cagr": cumulative_return * (365 / num_days),  # Annualized
            "sharpe_ratio": 0.0,  # No excess return
            "sortino_ratio": 0.0,
            "max_drawdown": -0.0001,  # Tiny drawdown from variations
            "win_rate": 0.5,
            "profit_factor": 1.0
        },
        "risk": {
            "volatility": returns.std() * np.sqrt(252),
            "var_95": np.percentile(returns, 5),
            "cvar_95": returns[returns <= np.percentile(returns, 5)].mean()
        },
        "execution": {
            "total_trades": 10,
            "winning_trades": 5,
            "losing_trades": 5,
            "avg_win": 100.0,
            "avg_loss": -100.0,
            "largest_win": 200.0,
            "largest_loss": -200.0
        },
        "accounting": {
            "initial_capital": initial_capital,
            "final_equity": equity_values[-1],
            "total_pnl": equity_values[-1] - initial_capital,
            "total_fees": 50.0,
            "unrealized_pnl": 0.0,  # No open positions
            "open_positions": 0
        }
    }
    
    with open(base_dir / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Create series.csv
    series_data = pd.DataFrame({
        'timestamp': timestamps,
        'equity': equity_values,
        'drawdown': 0.0,  # Flat performance = no drawdown
        'returns': returns.values,
        'positions': 0,  # No positions held
        'exposure': 0.0
    })
    series_data.to_csv(base_dir / "series.csv", index=False)
    
    # Create trades.csv (minimal trading activity)
    trades_data = pd.DataFrame({
        'timestamp': pd.date_range(start=start_date, periods=10, freq='W'),
        'symbol': ['BTCUSDT'] * 5 + ['ETHUSDT'] * 5,
        'side': ['buy', 'sell'] * 5,
        'quantity': [0.001] * 10,
        'price': [50000, 50100, 50200, 50150, 50000] * 2,
        'fee': [5.0] * 10,
        'pnl': [0, 100, 0, -50, -50, 0, 100, 0, -50, -50]
    })
    trades_data.to_csv(base_dir / "trades.csv", index=False)
    
    # Create events.csv
    events_data = pd.DataFrame({
        'timestamp': pd.date_range(start=start_date, periods=5, freq='2W'),
        'event_type': ['rebalance', 'risk_limit', 'rebalance', 'signal_generated', 'rebalance'],
        'description': [
            'Portfolio rebalanced',
            'Risk limit triggered',
            'Portfolio rebalanced',
            'RSI signal generated',
            'Portfolio rebalanced'
        ]
    })
    events_data.to_csv(base_dir / "events.csv", index=False)
    
    # Create main_analysis visualization (critical for visual validation)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # Panel 1: Equity Curve (should be flat)
    ax1 = axes[0]
    ax1.plot(timestamps, equity_values, 'b-', linewidth=1.5, label='Equity')
    ax1.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_ylabel('Equity ($)')
    ax1.set_title(f'Backtest Performance - {run_id}')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([initial_capital * 0.95, initial_capital * 1.05])
    
    # Panel 2: Drawdown (should be near zero)
    ax2 = axes[1]
    drawdown = np.zeros(num_days)  # Flat performance = no drawdown
    ax2.fill_between(timestamps, 0, drawdown, color='red', alpha=0.3)
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_ylim([-5, 0])
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Activity (positions)
    ax3 = axes[2]
    positions = np.zeros(num_days)  # No positions for clean test
    ax3.bar(timestamps[::10], positions[::10], width=1, color='green', alpha=0.5)
    ax3.set_ylabel('Positions')
    ax3.set_xlabel('Date')
    ax3.grid(True, alpha=0.3)
    
    # Format x-axis
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # Save as both PNG and PDF
    fig.savefig(base_dir / "figures" / "main_analysis.png", dpi=150, bbox_inches='tight')
    fig.savefig(base_dir / "figures" / "main_analysis.pdf", bbox_inches='tight')
    plt.close(fig)
    
    # Create performance heatmap
    fig2, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Monthly returns matrix (all near zero for flat performance)
    monthly_returns = pd.DataFrame({
        'Jan': [0.0],
        'Feb': [0.0],
        'Mar': [0.0]
    }, index=['2024'])
    
    im = ax.imshow([[0.0, 0.0, 0.0]], cmap='RdYlGn', vmin=-0.1, vmax=0.1, aspect='auto')
    ax.set_xticks(range(3))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar'])
    ax.set_yticks([0])
    ax.set_yticklabels(['2024'])
    ax.set_title('Monthly Returns Heatmap')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Return (%)')
    
    # Add text annotations
    for i in range(1):
        for j in range(3):
            text = ax.text(j, i, '0.0%', ha="center", va="center", color="black")
    
    plt.tight_layout()
    fig2.savefig(base_dir / "figures" / "returns_heatmap.png", dpi=150, bbox_inches='tight')
    fig2.savefig(base_dir / "figures" / "returns_heatmap.pdf", bbox_inches='tight')
    plt.close(fig2)
    
    print(f"Test data created successfully in {base_dir}")
    print(f"Key characteristics:")
    print(f"  - Initial capital: ${initial_capital:,.2f}")
    print(f"  - Final equity: ${equity_values[-1]:,.2f}")
    print(f"  - Total return: {cumulative_return:.2%}")
    print(f"  - Open positions: 0 (clean test)")
    print(f"  - Visual validation: Flat equity curve matching 0% return")
    
    return str(base_dir)

if __name__ == "__main__":
    # Create test run data
    run_dir = create_test_run_data(test_mode=True)
    print(f"\nTest run created: {run_dir}")
    print("\nYou can now run: /evaluate-single-run test_20241210_120000 --test")