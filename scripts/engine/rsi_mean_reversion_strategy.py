"""
RSI Mean Reversion Strategy Engine

Test strategy implementation for skeleton validation.
Implements RSI oversold/overbought mean reversion with stop loss.

Strategy Specification (from test_SMR.md):
- Entry: RSI(14) < 30 (oversold)
- Exit: RSI(14) > 70 (overbought) OR 5% stop loss
- Position Size: 10% of equity
- Universe: BTCUSDT, ETHUSDT, ADAUSDT
- Timeframe: 1h
- Backtest Period: 2023-01-01 to 2023-06-30
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Import optimization components
try:
    from .core.filter_gate_manager import FilterGateManager, FilterType
    from .data.data_processor import DataProcessor
    from .optimization.reference_engine import ReferenceEngine
except ImportError:
    from core.filter_gate_manager import FilterGateManager, FilterType
    from data.data_processor import DataProcessor
    from optimization.reference_engine import ReferenceEngine


class SignalType(Enum):
    """Signal types for the strategy."""
    ENTRY_LONG = "entry_long"
    EXIT_OVERBOUGHT = "exit_overbought"
    EXIT_STOP_LOSS = "exit_stop_loss"


@dataclass
class Signal:
    """Trading signal data structure."""
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    price: float
    metadata: Dict[str, Any]


class RSIMeanReversionStrategy:
    """
    RSI Mean Reversion Strategy Implementation.
    
    Features:
    - RSI(14) calculation with oversold/overbought thresholds
    - 5% stop loss implementation
    - Optimized with FilterGateManager for efficient symbol filtering
    - Feature caching through DataProcessor
    - Universe reduction via ReferenceEngine
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Strategy parameters (with defaults from test_SMR.md)
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.05)
        self.position_size_pct = config.get('position_size_pct', 0.10)
        
        # Fixed symbol universe for test strategy
        self.symbol_universe = config.get('symbols', ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])
        
        # Minimum data requirements
        self.min_bars_required = max(50, self.rsi_period * 3)  # At least 50 bars for RSI warmup
        
        # Position tracking
        self.positions: Dict[str, Dict[str, Any]] = {}  # symbol -> position info
        
        # Initialize optimization components
        self._initialize_optimization_components()
        
        # Performance tracking
        self.signal_stats = {
            'total_signals': 0,
            'entry_signals': 0,
            'exit_signals': 0,
            'stop_losses_triggered': 0,
            'overbought_exits': 0
        }
        
        self.logger.info(f"RSI Mean Reversion Strategy initialized: "
                        f"RSI({self.rsi_period}) oversold={self.rsi_oversold} "
                        f"overbought={self.rsi_overbought} stop_loss={self.stop_loss_pct*100}%")
    
    def _initialize_optimization_components(self) -> None:
        """Initialize optimization components for maximum performance."""
        # FilterGateManager for efficient symbol filtering
        self.filter_gate_manager = FilterGateManager()
        
        # Register RSI filters for the strategy
        self.filter_gate_manager.register_filter(
            "rsi_oversold",
            FilterType.MONOTONE_LESSER,  # RSI < threshold
            lambda data, threshold: data.get(f'rsi_{self.rsi_period}', 100) < threshold,
            [f'rsi_{self.rsi_period}'],
            "RSI oversold condition filter"
        )
        
        self.filter_gate_manager.register_filter(
            "rsi_overbought",
            FilterType.MONOTONE_GREATER,  # RSI > threshold
            lambda data, threshold: data.get(f'rsi_{self.rsi_period}', 0) > threshold,
            [f'rsi_{self.rsi_period}'],
            "RSI overbought condition filter"
        )
        
        # DataProcessor for optimized feature calculation
        self.data_processor = DataProcessor({
            'enable_feature_optimization': True,
            'missing_data_policy': 'forward_fill'
        })
        
        # ReferenceEngine for universe reduction in optimization
        self.reference_engine = ReferenceEngine()
        
        self.logger.debug("Optimization components initialized: FilterGateManager, DataProcessor, ReferenceEngine")
    
    def calculate_features(self, 
                          ohlcv_data: Dict[str, pd.DataFrame],
                          current_timestamp: datetime) -> Dict[str, pd.DataFrame]:
        """
        Calculate required features for the strategy.
        
        Args:
            ohlcv_data: OHLCV data for all symbols
            current_timestamp: Current evaluation timestamp
            
        Returns:
            Dictionary of symbol -> features DataFrame
        """
        # Use optimized DataProcessor for feature calculation
        feature_names = [f'rsi_{self.rsi_period}']
        features_data = self.data_processor.calculate_features(ohlcv_data, feature_names)
        
        # Log feature calculation stats
        stats = self.data_processor.get_optimization_stats()
        if stats['cache_hit_rate_pct'] > 0:
            self.logger.debug(f"Feature calculation: {stats['cache_hit_rate_pct']}% cache hit rate")
        
        return features_data
    
    def generate_signals(self,
                        current_timestamp: datetime,
                        ohlcv_data: Dict[str, pd.DataFrame],
                        features_data: Dict[str, pd.DataFrame],
                        portfolio_state: Dict[str, Any]) -> List[Signal]:
        """
        Generate trading signals based on RSI mean reversion logic.
        
        Args:
            current_timestamp: Current evaluation timestamp
            ohlcv_data: OHLCV data for all symbols
            features_data: Calculated features for all symbols
            portfolio_state: Current portfolio state
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # Process each symbol in the universe
        for symbol in self.symbol_universe:
            if symbol not in ohlcv_data or symbol not in features_data:
                continue
            
            try:
                # Get current bar data
                symbol_ohlcv = ohlcv_data[symbol]
                symbol_features = features_data[symbol]
                
                # Check if we have data for current timestamp
                if current_timestamp not in symbol_ohlcv.index:
                    continue
                
                # Get current values
                current_bar = symbol_ohlcv.loc[current_timestamp]
                current_price = current_bar['close']
                
                # Check for sufficient history
                if len(symbol_features) < self.min_bars_required:
                    continue
                
                # Get RSI value
                if current_timestamp not in symbol_features.index:
                    continue
                    
                current_features = symbol_features.loc[current_timestamp]
                rsi_value = current_features.get(f'rsi_{self.rsi_period}')
                
                if pd.isna(rsi_value):
                    continue
                
                # Check if we have an open position
                has_position = symbol in self.positions
                
                if has_position:
                    # EXIT LOGIC
                    position = self.positions[symbol]
                    entry_price = position['entry_price']
                    
                    # Check stop loss condition first (priority)
                    stop_loss_price = entry_price * (1 - self.stop_loss_pct)
                    if current_price <= stop_loss_price:
                        signal = Signal(
                            timestamp=current_timestamp,
                            symbol=symbol,
                            signal_type=SignalType.EXIT_STOP_LOSS,
                            price=current_price,
                            metadata={
                                'rsi': rsi_value,
                                'entry_price': entry_price,
                                'stop_loss_price': stop_loss_price,
                                'loss_pct': (current_price - entry_price) / entry_price
                            }
                        )
                        signals.append(signal)
                        self.signal_stats['stop_losses_triggered'] += 1
                        self.logger.debug(f"{symbol}: Stop loss triggered at {current_price:.2f} "
                                        f"(entry: {entry_price:.2f}, RSI: {rsi_value:.2f})")
                    
                    # Check RSI overbought exit condition
                    elif rsi_value > self.rsi_overbought:
                        signal = Signal(
                            timestamp=current_timestamp,
                            symbol=symbol,
                            signal_type=SignalType.EXIT_OVERBOUGHT,
                            price=current_price,
                            metadata={
                                'rsi': rsi_value,
                                'entry_price': entry_price,
                                'profit_pct': (current_price - entry_price) / entry_price
                            }
                        )
                        signals.append(signal)
                        self.signal_stats['overbought_exits'] += 1
                        self.logger.debug(f"{symbol}: Overbought exit at {current_price:.2f} "
                                        f"(RSI: {rsi_value:.2f})")
                
                else:
                    # ENTRY LOGIC
                    # Check RSI oversold entry condition
                    if rsi_value < self.rsi_oversold:
                        # Check portfolio constraints (position limits, available cash, etc.)
                        available_cash = portfolio_state.get('available_cash', 0)
                        current_equity = portfolio_state.get('equity', 100000)
                        position_value = current_equity * self.position_size_pct
                        
                        # Check minimum notional requirement ($50)
                        min_notional = 50
                        if position_value >= min_notional and available_cash >= position_value:
                            signal = Signal(
                                timestamp=current_timestamp,
                                symbol=symbol,
                                signal_type=SignalType.ENTRY_LONG,
                                price=current_price,
                                metadata={
                                    'rsi': rsi_value,
                                    'position_size_pct': self.position_size_pct,
                                    'position_value': position_value
                                }
                            )
                            signals.append(signal)
                            self.signal_stats['entry_signals'] += 1
                            self.logger.debug(f"{symbol}: Oversold entry signal at {current_price:.2f} "
                                            f"(RSI: {rsi_value:.2f})")
                
            except Exception as e:
                self.logger.error(f"Error generating signal for {symbol}: {str(e)}")
                continue
        
        # Update signal statistics
        self.signal_stats['total_signals'] += len(signals)
        self.signal_stats['exit_signals'] = (self.signal_stats['stop_losses_triggered'] + 
                                             self.signal_stats['overbought_exits'])
        
        return signals
    
    def apply_filters(self,
                     current_timestamp: datetime,
                     ohlcv_data: Dict[str, pd.DataFrame],
                     features_data: Dict[str, pd.DataFrame]) -> Set[str]:
        """
        Apply filters to determine eligible symbols using optimization.
        
        Args:
            current_timestamp: Current evaluation timestamp
            ohlcv_data: OHLCV data for all symbols
            features_data: Calculated features for all symbols
            
        Returns:
            Set of symbols that pass all filters
        """
        # Use FilterGateManager for optimized filtering
        oversold_symbols = self.filter_gate_manager.apply_filter(
            "rsi_oversold",
            self.rsi_oversold,
            ohlcv_data,
            features_data,
            current_timestamp
        )
        
        # Log filter performance
        filter_stats = self.filter_gate_manager.get_performance_stats()
        if filter_stats['cache_hit_rate_pct'] > 0:
            self.logger.debug(f"Filter optimization: {filter_stats['cache_hit_rate_pct']}% cache hit rate")
        
        return oversold_symbols
    
    def update_positions(self, executed_signals: List[Dict[str, Any]]) -> None:
        """
        Update internal position tracking based on executed signals.
        
        Args:
            executed_signals: List of executed signal dictionaries
        """
        for signal in executed_signals:
            symbol = signal.get('symbol')
            signal_type = signal.get('signal_type')
            
            if signal_type == SignalType.ENTRY_LONG.value:
                # Open new position
                self.positions[symbol] = {
                    'entry_price': signal.get('execution_price', signal.get('price')),
                    'entry_timestamp': signal.get('timestamp'),
                    'quantity': signal.get('quantity', 0),
                    'position_value': signal.get('position_value', 0)
                }
                self.logger.debug(f"Opened position in {symbol}")
                
            elif signal_type in [SignalType.EXIT_OVERBOUGHT.value, SignalType.EXIT_STOP_LOSS.value]:
                # Close position
                if symbol in self.positions:
                    del self.positions[symbol]
                    self.logger.debug(f"Closed position in {symbol}")
    
    def get_optimization_universe(self, 
                                 full_universe: List[str],
                                 current_parameters: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Get optimized symbol universe for parameter optimization.
        
        Args:
            full_universe: Complete list of symbols
            current_parameters: Current parameter values for optimization
            
        Returns:
            Optimized list of symbols
        """
        if current_parameters is None:
            current_parameters = {
                'rsi_period': self.rsi_period,
                'rsi_oversold': self.rsi_oversold,
                'rsi_overbought': self.rsi_overbought
            }
        
        # Use ReferenceEngine for universe reduction
        optimized_universe, metadata = self.reference_engine.get_optimized_universe(
            full_universe, current_parameters
        )
        
        if metadata.get('reduction_applied'):
            self.logger.info(f"Universe optimization: {metadata['original_universe_size']} -> "
                           f"{metadata['reduced_universe_size']} symbols "
                           f"({metadata['estimated_speedup']}x speedup)")
        
        return optimized_universe
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get strategy performance statistics."""
        return {
            'signal_stats': self.signal_stats,
            'filter_optimization': self.filter_gate_manager.get_performance_stats(),
            'feature_optimization': self.data_processor.get_optimization_stats(),
            'universe_optimization': self.reference_engine.get_optimization_stats(),
            'active_positions': len(self.positions),
            'position_symbols': list(self.positions.keys())
        }
    
    def reset(self) -> None:
        """Reset strategy state for new backtest run."""
        self.positions.clear()
        self.signal_stats = {
            'total_signals': 0,
            'entry_signals': 0,
            'exit_signals': 0,
            'stop_losses_triggered': 0,
            'overbought_exits': 0
        }
        # Clear optimization caches for fresh run
        self.filter_gate_manager.clear_cache()
        self.data_processor.clear_feature_cache()
        self.logger.debug("Strategy state reset")