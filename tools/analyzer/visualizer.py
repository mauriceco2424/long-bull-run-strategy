#!/usr/bin/env python3
"""
Professional Trading Strategy Visualization Engine

This module generates publication-quality visualizations for trading strategy analysis.
It implements research-based best practices with clean, focused charts that avoid 
dual-axis confusion and prioritize visual clarity.

Key Features:
- Stacked panel layout (equity + drawdown + activity)
- Smart time axis auto-detection
- Professional typography and styling
- Colorblind-friendly palettes
- Template-based configuration
- Mock data generation for testing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
import warnings

# Suppress matplotlib warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class TradingVisualizer:
    """Professional trading strategy visualization engine."""
    
    def __init__(self, run_id: str, run_data_path: str = "data/runs"):
        self.run_id = run_id
        self.run_path = Path(run_data_path) / run_id
        self.figs_path = self.run_path / "figs"
        
        # Create figures directory if it doesn't exist
        self.figs_path.mkdir(parents=True, exist_ok=True)
        
        # Professional styling configuration
        self._setup_professional_style()
        
    def _setup_professional_style(self):
        """Configure professional matplotlib styling."""
        # Set high-quality defaults
        plt.rcParams.update({
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
        })
        
        # Colorblind-friendly palette
        self.colors = {
            'primary': '#1f77b4',      # Blue
            'secondary': '#ff7f0e',    # Orange  
            'success': '#2ca02c',      # Green
            'danger': '#d62728',       # Red
            'warning': '#ff7f0e',      # Orange
            'muted': '#7f7f7f',        # Gray
            'benchmark': '#bcbd22',    # Olive
            'background': '#f8f9fa',   # Light gray
        }
        
    def generate_default_chart(self, template_config: Optional[Dict] = None) -> str:
        """Generate the default 3-panel trading strategy visualization."""
        
        # Load or generate data
        if self._has_real_data():
            equity_data, trades_data, series_data = self._load_real_data()
        else:
            equity_data, trades_data, series_data = self._generate_mock_data()
            
        # Apply template configuration if provided
        config = self._merge_template_config(template_config)
        
        # Create the main figure with 3 panels
        fig, (ax_equity, ax_drawdown, ax_activity) = plt.subplots(
            3, 1, 
            figsize=(12, 10), 
            height_ratios=[0.7, 0.2, 0.1],
            sharex=True
        )
        
        # Panel 1: Equity Curve + Benchmark (70% height)
        self._create_equity_panel(ax_equity, equity_data, config)
        
        # Panel 2: Drawdown Analysis (20% height)
        self._create_drawdown_panel(ax_drawdown, equity_data, config)
        
        # Panel 3: Trade Activity Summary (10% height)
        self._create_activity_panel(ax_activity, trades_data, config)
        
        # Configure smart time axis
        self._configure_time_axis([ax_equity, ax_drawdown, ax_activity], equity_data.index)
        
        # Apply final styling
        plt.suptitle(f'Trading Strategy Analysis: {self.run_id}', 
                    fontsize=14, fontweight='bold', y=0.95)
        plt.tight_layout()
        plt.subplots_adjust(top=0.92, hspace=0.1)
        
        # Save in vector format (PDF) for LaTeX and raster (PNG) for HTML
        output_path_pdf = self.figs_path / "strategy_performance.pdf"
        output_path_png = self.figs_path / "strategy_performance.png"
        
        plt.savefig(output_path_pdf, bbox_inches='tight', format='pdf')  # Vector - no DPI needed
        plt.savefig(output_path_png, dpi=300, bbox_inches='tight', format='png')  # Raster - 300 DPI
        
        plt.close()
        return str(output_path_pdf)  # Return PDF path as primary
        
    def _create_equity_panel(self, ax: plt.Axes, equity_data: pd.DataFrame, config: Dict):
        """Create the main equity curve panel."""
        
        # Primary equity curve
        ax.plot(equity_data.index, equity_data['equity'], 
               color=self.colors['primary'], linewidth=2.5, 
               label='Strategy Equity', alpha=0.9)
        
        # Benchmark comparison if configured
        if config.get('show_benchmark', True) and 'benchmark' in equity_data.columns:
            ax.plot(equity_data.index, equity_data['benchmark'],
                   color=self.colors['benchmark'], linewidth=1.5,
                   label=config.get('benchmark_symbol', 'Benchmark'), 
                   alpha=0.7, linestyle='--')
        
        # Background shading for winning/losing periods
        if config.get('show_period_shading', True):
            self._add_period_shading(ax, equity_data)
            
        ax.set_ylabel('Account Value ($)', fontweight='bold')
        ax.set_title('Equity Curve Evolution', fontweight='bold', pad=10)
        ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_facecolor('#fafafa')
        
    def _create_drawdown_panel(self, ax: plt.Axes, equity_data: pd.DataFrame, config: Dict):
        """Create the drawdown analysis panel."""
        
        # Calculate drawdown
        running_max = equity_data['equity'].expanding().max()
        drawdown = (equity_data['equity'] - running_max) / running_max * 100
        
        # Inverted area chart (red fill going down from 0%)
        ax.fill_between(equity_data.index, 0, drawdown, 
                       color=self.colors['danger'], alpha=0.6, 
                       label='Drawdown %')
        
        # Zero line
        ax.axhline(y=0, color='black', linewidth=1, alpha=0.8)
        
        # Highlight maximum drawdown period
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min()
        
        if pd.notna(max_dd_idx):
            ax.scatter(max_dd_idx, max_dd_value, color=self.colors['danger'], 
                      s=50, zorder=5, marker='v')
            ax.annotate(f'Max DD: {max_dd_value:.1f}%', 
                       xy=(max_dd_idx, max_dd_value),
                       xytext=(10, -10), textcoords='offset points',
                       fontsize=8, color=self.colors['danger'], fontweight='bold')
        
        ax.set_ylabel('Drawdown (%)', fontweight='bold')
        ax.set_title('Drawdown Analysis', fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_facecolor('#fafafa')
        
    def _create_activity_panel(self, ax: plt.Axes, trades_data: pd.DataFrame, config: Dict):
        """Create the trade activity summary panel."""
        
        # Group trades by period for activity visualization
        if not trades_data.empty:
            # Convert to datetime if needed
            if 'timestamp' in trades_data.columns:
                trades_data['date'] = pd.to_datetime(trades_data['timestamp']).dt.date
                daily_activity = trades_data.groupby('date').size()
                
                # Create bar chart of daily activity
                ax.bar(daily_activity.index, daily_activity.values,
                      color=self.colors['secondary'], alpha=0.7, width=1)
        else:
            # Mock activity for visualization
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
            activity = np.random.poisson(0.5, len(dates))  # Low activity simulation
            ax.bar(dates, activity, color=self.colors['secondary'], alpha=0.7, width=1)
            
        ax.set_ylabel('Trades', fontweight='bold')
        ax.set_title('Daily Trade Activity', fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_facecolor('#fafafa')
        
    def _configure_time_axis(self, axes: List[plt.Axes], date_range: pd.DatetimeIndex):
        """Configure smart time axis with auto-detected optimal spacing."""
        
        total_days = (date_range[-1] - date_range[0]).days
        
        # Auto-detect optimal spacing based on research
        if total_days < 90:
            # Daily ticks for short periods
            major_locator = mdates.DayLocator(interval=7)  # Weekly major ticks
            minor_locator = mdates.DayLocator(interval=1)  # Daily minor ticks
            formatter = mdates.DateFormatter('%m-%d')
        elif total_days < 365:
            # Weekly ticks for medium periods  
            major_locator = mdates.WeekdayLocator(interval=2)
            minor_locator = mdates.WeekdayLocator(interval=1)
            formatter = mdates.DateFormatter('%m-%d')
        elif total_days < 1095:  # 3 years
            # Monthly ticks for longer periods
            major_locator = mdates.MonthLocator(interval=1)
            minor_locator = mdates.WeekdayLocator(interval=1)
            formatter = mdates.DateFormatter('%Y-%m')
        else:
            # Quarterly ticks for very long periods
            major_locator = mdates.MonthLocator(interval=3)
            minor_locator = mdates.MonthLocator(interval=1)
            formatter = mdates.DateFormatter('%Y-%m')
            
        # Apply to all axes
        for ax in axes:
            ax.xaxis.set_major_locator(major_locator)
            ax.xaxis.set_minor_locator(minor_locator)
            ax.xaxis.set_major_formatter(formatter)
            
        # Only show x-axis labels on bottom panel
        for ax in axes[:-1]:
            ax.tick_params(labelbottom=False)
            
        axes[-1].tick_params(axis='x', rotation=45)
        
    def _add_period_shading(self, ax: plt.Axes, equity_data: pd.DataFrame):
        """Add subtle background shading for winning/losing periods."""
        
        if 'equity' not in equity_data.columns:
            return
            
        # Calculate rolling returns to identify winning/losing periods
        returns = equity_data['equity'].pct_change().rolling(window=30).mean()
        
        winning_periods = returns > 0.001  # 0.1% monthly threshold
        
        # Add very subtle shading
        for start, end in self._get_period_ranges(winning_periods):
            if end > start:
                ax.axvspan(equity_data.index[start], equity_data.index[end], 
                          color=self.colors['success'], alpha=0.05)
                          
    def _get_period_ranges(self, boolean_series: pd.Series) -> List[Tuple[int, int]]:
        """Get start/end indices for True periods in a boolean series."""
        ranges = []
        start = None
        
        for i, value in enumerate(boolean_series):
            if value and start is None:
                start = i
            elif not value and start is not None:
                ranges.append((start, i-1))
                start = None
                
        # Handle case where series ends with True
        if start is not None:
            ranges.append((start, len(boolean_series)-1))
            
        return ranges
        
    def _merge_template_config(self, template_config: Optional[Dict]) -> Dict:
        """Merge template configuration with defaults."""
        default_config = {
            'show_benchmark': True,
            'benchmark_symbol': 'SPY',
            'show_period_shading': True,
            'visualization_level': 'basic',
            'show_trade_markers': False,
        }
        
        if template_config:
            default_config.update(template_config)
            
        return default_config
        
    def _has_real_data(self) -> bool:
        """Check if real trading data exists."""
        required_files = ['series.csv', 'trades.csv', 'metrics.json']
        return all((self.run_path / file).exists() for file in required_files)
        
    def _load_real_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load real trading data from run artifacts."""
        
        series_data = pd.read_csv(self.run_path / 'series.csv', parse_dates=['timestamp'])
        trades_data = pd.read_csv(self.run_path / 'trades.csv', parse_dates=['timestamp'])
        
        # Create equity dataframe with proper datetime index
        equity_data = series_data.set_index('timestamp')[['equity']]
        
        return equity_data, trades_data, series_data
        
    def _generate_mock_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate synthetic data for testing and development."""
        
        # Create realistic date range
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic equity curve with volatility
        np.random.seed(42)  # Reproducible results
        n_days = len(dates)
        
        # Base trend with noise
        base_return = 0.0003  # ~12% annual return
        volatility = 0.02     # 2% daily volatility
        
        daily_returns = np.random.normal(base_return, volatility, n_days)
        
        # Add some realistic drawdown periods
        drawdown_periods = [
            (50, 80),   # Early year correction
            (180, 220), # Mid-year volatility
            (300, 330), # Late year selloff
        ]
        
        for start_idx, end_idx in drawdown_periods:
            if end_idx < n_days:
                daily_returns[start_idx:end_idx] = np.random.normal(-0.001, 0.025, end_idx-start_idx)
        
        # Calculate cumulative equity
        initial_equity = 100000  # $100k starting capital
        equity_values = initial_equity * (1 + daily_returns).cumprod()
        
        # Create benchmark (simple upward trend with less volatility)
        benchmark_returns = np.random.normal(0.0002, 0.015, n_days)  # 8% annual, less volatile
        benchmark_values = initial_equity * (1 + benchmark_returns).cumprod()
        
        equity_data = pd.DataFrame({
            'equity': equity_values,
            'benchmark': benchmark_values
        }, index=dates)
        
        # Generate mock trades (sparse, realistic pattern)
        trade_dates = np.random.choice(dates, size=int(n_days * 0.1), replace=False)  # 10% of days
        trades_data = pd.DataFrame({
            'timestamp': trade_dates,
            'symbol': np.random.choice(['BTC-USDT', 'ETH-USDT', 'SOL-USDT'], len(trade_dates)),
            'side': np.random.choice(['buy', 'sell'], len(trade_dates)),
            'pnl': np.random.normal(50, 200, len(trade_dates)),  # Realistic P&L distribution
        })
        
        # Generate series data (same as equity but with additional columns)
        series_data = pd.DataFrame({
            'timestamp': dates,
            'equity': equity_values,
            'monitored_count': np.random.poisson(5, n_days),
            'open_trades_count': np.random.poisson(2, n_days),
        })
        
        return equity_data, trades_data, series_data
        
    def generate_per_symbol_charts(self, symbols: Optional[List[str]] = None, 
                                 template_config: Optional[Dict] = None) -> List[str]:
        """Generate per-symbol analysis charts (enhanced visualization)."""
        
        if symbols is None:
            symbols = ['BTC-USDT', 'ETH-USDT']  # Default mock symbols
            
        output_paths = []
        
        for symbol in symbols:
            fig, (ax_price, ax_volume) = plt.subplots(2, 1, figsize=(12, 8), 
                                                     height_ratios=[0.7, 0.3], sharex=True)
            
            # Generate mock OHLCV data
            ohlcv_data = self._generate_mock_ohlcv(symbol)
            
            # Candlestick chart
            self._plot_candlesticks(ax_price, ohlcv_data)
            
            # Volume bars
            self._plot_volume(ax_volume, ohlcv_data)
            
            # Add event markers (mock)
            self._add_event_markers(ax_price, ohlcv_data)
            
            ax_price.set_title(f'{symbol} Price Action & Trading Events', fontweight='bold', pad=10)
            ax_price.set_ylabel('Price ($)', fontweight='bold')
            ax_volume.set_ylabel('Volume', fontweight='bold')
            ax_volume.set_xlabel('Date', fontweight='bold')
            
            plt.tight_layout()
            
            # Save symbol-specific chart in both formats
            output_path_pdf = self.figs_path / f"symbol_{symbol.replace('-', '_').lower()}.pdf"
            output_path_png = self.figs_path / f"symbol_{symbol.replace('-', '_').lower()}.png"
            
            plt.savefig(output_path_pdf, bbox_inches='tight', format='pdf')  # Vector for LaTeX
            plt.savefig(output_path_png, dpi=300, bbox_inches='tight', format='png')  # Raster for HTML
            output_paths.append(str(output_path_pdf))
            
            plt.close()
            
        return output_paths
        
    def _generate_mock_ohlcv(self, symbol: str) -> pd.DataFrame:
        """Generate mock OHLCV data for symbol charts."""
        
        dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='D')
        n_days = len(dates)
        
        # Base price (varies by symbol)
        base_prices = {'BTC-USDT': 25000, 'ETH-USDT': 1500, 'SOL-USDT': 20}
        base_price = base_prices.get(symbol, 100)
        
        # Generate realistic OHLCV
        np.random.seed(hash(symbol) % 1000)  # Consistent per symbol
        
        close_prices = []
        current_price = base_price
        
        for _ in range(n_days):
            daily_change = np.random.normal(0, 0.03)  # 3% daily volatility
            current_price *= (1 + daily_change)
            close_prices.append(current_price)
            
        close_prices = np.array(close_prices)
        
        # Generate OHLC from close
        highs = close_prices * np.random.uniform(1.0, 1.05, n_days)
        lows = close_prices * np.random.uniform(0.95, 1.0, n_days)
        opens = np.roll(close_prices, 1)  # Yesterday's close
        opens[0] = base_price
        
        volumes = np.random.lognormal(10, 1, n_days)  # Realistic volume distribution
        
        return pd.DataFrame({
            'open': opens,
            'high': highs,
            'low': lows,
            'close': close_prices,
            'volume': volumes,
        }, index=dates)
        
    def _plot_candlesticks(self, ax: plt.Axes, ohlcv_data: pd.DataFrame):
        """Plot candlestick chart."""
        
        dates = ohlcv_data.index
        opens = ohlcv_data['open']
        highs = ohlcv_data['high']
        lows = ohlcv_data['low']
        closes = ohlcv_data['close']
        
        # Determine colors
        colors = ['red' if c < o else 'green' for c, o in zip(closes, opens)]
        
        for i, (date, o, h, l, c, color) in enumerate(zip(dates, opens, highs, lows, closes, colors)):
            # High-low line
            ax.plot([date, date], [l, h], color='black', linewidth=0.8)
            
            # Body rectangle
            body_height = abs(c - o)
            body_bottom = min(c, o)
            
            rect = Rectangle((date - pd.Timedelta(hours=8), body_bottom), 
                           pd.Timedelta(hours=16), body_height,
                           facecolor=color, alpha=0.7, edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
        ax.grid(True, alpha=0.3)
        
    def _plot_volume(self, ax: plt.Axes, ohlcv_data: pd.DataFrame):
        """Plot volume bars."""
        
        ax.bar(ohlcv_data.index, ohlcv_data['volume'], 
              color=self.colors['muted'], alpha=0.6, width=0.8)
        ax.grid(True, alpha=0.3)
        
    def _add_event_markers(self, ax: plt.Axes, ohlcv_data: pd.DataFrame):
        """Add mock event markers to price chart."""
        
        # Generate some mock events
        n_events = 5
        event_dates = np.random.choice(ohlcv_data.index, size=n_events, replace=False)
        event_types = ['buy', 'tp_sell', 'sl_sell', 'filter_pass', 'buy_signal']
        
        event_colors = {
            'filter_pass': 'gray',
            'buy_signal': 'black', 
            'buy': 'blue',
            'tp_sell': 'green',
            'sl_sell': 'red',
        }
        
        for date, event_type in zip(event_dates, event_types):
            price = ohlcv_data.loc[date, 'close']
            color = event_colors.get(event_type, 'purple')
            
            ax.axvline(x=date, color=color, linestyle='--', alpha=0.7, linewidth=2)
            ax.scatter(date, price, color=color, s=50, zorder=5)


def main():
    """Main entry point for visualization testing."""
    
    # Test with mock data
    visualizer = TradingVisualizer("test_run_001")
    
    print("Generating default visualization...")
    main_chart = visualizer.generate_default_chart()
    print(f"Main chart saved to: {main_chart}")
    
    print("Generating per-symbol charts...")
    symbol_charts = visualizer.generate_per_symbol_charts()
    for path in symbol_charts:
        print(f"Symbol chart saved to: {path}")
        
    print("Visualization generation completed!")


if __name__ == "__main__":
    main()