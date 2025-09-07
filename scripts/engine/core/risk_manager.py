"""
Risk Manager

Handles real-time risk validation and enforcement.
Prevents excessive exposure and enforces safety limits.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime


class RiskManager:
    """
    Real-time risk management and validation.
    
    Enforces:
    - Position size limits
    - Portfolio heat limits
    - Maximum concurrent positions
    - Drawdown protection
    - Leverage constraints
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk manager with configuration.
        
        Args:
            config: Configuration dictionary from parameter_config.md
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract risk parameters
        risk_config = config.get('risk_management', {})
        
        # Position limits
        self.max_concurrent_positions = risk_config.get('max_concurrent_positions')
        self.max_position_size_pct = risk_config.get('max_position_size_pct')
        self.max_portfolio_heat_pct = risk_config.get('max_portfolio_heat_pct')
        
        # Execution limits
        execution_config = config.get('execution', {})
        self.max_leverage = execution_config.get('max_leverage', 1.0)
        self.min_notional = execution_config.get('min_notional')
        
        # Drawdown protection
        self.max_daily_loss_pct = risk_config.get('max_daily_loss_pct')
        self.max_total_drawdown_pct = risk_config.get('max_total_drawdown_pct')
        
        # Risk state tracking
        self.risk_violations = []
        self.daily_start_equity = None
        self.peak_equity = None
        
        self.logger.info("Risk manager initialized with safety limits")
    
    def validate_signals(self, 
                        signals: List[Dict[str, Any]], 
                        portfolio_state: Dict[str, Any],
                        current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Validate trading signals against risk limits.
        
        Args:
            signals: List of trading signals from strategy
            portfolio_state: Current portfolio state
            current_prices: Current market prices
            
        Returns:
            List of validated signals (may be filtered or modified)
        """
        if not signals:
            return []
        
        validated_signals = []
        
        for signal in signals:
            try:
                # Validate individual signal
                if self._validate_signal(signal, portfolio_state, current_prices):
                    validated_signals.append(signal)
                else:
                    self._log_signal_rejection(signal, "Risk limit violation")
                    
            except Exception as e:
                self.logger.error(f"Error validating signal {signal}: {str(e)}")
                continue
        
        # Additional portfolio-level validation
        validated_signals = self._validate_portfolio_level_risk(
            validated_signals, portfolio_state, current_prices
        )
        
        return validated_signals
    
    def check_position_risk(self, 
                          symbol: str, 
                          quantity: float,
                          price: float,
                          portfolio_state: Dict[str, Any]) -> bool:
        """
        Check if a position would violate risk limits.
        
        Args:
            symbol: Trading symbol
            quantity: Position quantity
            price: Entry price
            portfolio_state: Current portfolio state
            
        Returns:
            True if position is within risk limits
        """
        # Position size check
        if not self._check_position_size_limit(quantity, price, portfolio_state['total_equity']):
            return False
        
        # Portfolio heat check
        if not self._check_portfolio_heat_limit(symbol, quantity, price, portfolio_state):
            return False
        
        # Concurrent positions check
        if not self._check_concurrent_positions_limit(portfolio_state):
            return False
        
        # Minimum notional check
        if not self._check_minimum_notional(quantity, price):
            return False
        
        return True
    
    def update_daily_risk_state(self, portfolio_state: Dict[str, Any]) -> None:
        """
        Update daily risk tracking state.
        
        Args:
            portfolio_state: Current portfolio state
        """
        current_equity = portfolio_state['total_equity']
        
        # Initialize daily start equity if not set
        if self.daily_start_equity is None:
            self.daily_start_equity = current_equity
        
        # Update peak equity
        if self.peak_equity is None or current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        # Check daily loss limit
        if self.max_daily_loss_pct:
            daily_loss_pct = (self.daily_start_equity - current_equity) / self.daily_start_equity * 100
            if daily_loss_pct > self.max_daily_loss_pct:
                self._trigger_risk_event("daily_loss_limit", daily_loss_pct)
        
        # Check total drawdown limit
        if self.max_total_drawdown_pct and self.peak_equity:
            drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity * 100
            if drawdown_pct > self.max_total_drawdown_pct:
                self._trigger_risk_event("drawdown_limit", drawdown_pct)
    
    def reset_daily_state(self, portfolio_state: Dict[str, Any]) -> None:
        """Reset daily risk state (call at start of new trading day)."""
        self.daily_start_equity = portfolio_state['total_equity']
        self.logger.debug("Daily risk state reset")
    
    def get_risk_metrics(self, portfolio_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate current risk metrics.
        
        Args:
            portfolio_state: Current portfolio state
            
        Returns:
            Dictionary of risk metrics
        """
        current_equity = portfolio_state['total_equity']
        
        metrics = {
            'current_positions': portfolio_state['open_positions_count'],
            'portfolio_leverage': self._calculate_portfolio_leverage(portfolio_state),
            'portfolio_heat_pct': self._calculate_portfolio_heat(portfolio_state),
            'daily_pnl_pct': 0.0,
            'total_drawdown_pct': 0.0,
            'risk_violations_today': len([v for v in self.risk_violations 
                                         if v['timestamp'].date() == datetime.now().date()])
        }
        
        # Calculate daily P&L
        if self.daily_start_equity and self.daily_start_equity > 0:
            metrics['daily_pnl_pct'] = (current_equity - self.daily_start_equity) / self.daily_start_equity * 100
        
        # Calculate total drawdown
        if self.peak_equity and self.peak_equity > 0:
            metrics['total_drawdown_pct'] = (self.peak_equity - current_equity) / self.peak_equity * 100
        
        # Risk limit utilization
        if self.max_concurrent_positions:
            metrics['position_limit_utilization'] = portfolio_state['open_positions_count'] / self.max_concurrent_positions
        
        if self.max_portfolio_heat_pct:
            metrics['heat_limit_utilization'] = metrics['portfolio_heat_pct'] / self.max_portfolio_heat_pct
        
        return metrics
    
    def get_risk_status(self) -> Dict[str, Any]:
        """Get overall risk status and recent violations."""
        return {
            'status': 'healthy',  # Could be 'healthy', 'warning', 'critical'
            'recent_violations': self.risk_violations[-10:],  # Last 10 violations
            'total_violations': len(self.risk_violations),
            'last_violation': self.risk_violations[-1] if self.risk_violations else None
        }
    
    def _validate_signal(self, 
                        signal: Dict[str, Any], 
                        portfolio_state: Dict[str, Any],
                        current_prices: Dict[str, float]) -> bool:
        """Validate individual signal against risk limits."""
        symbol = signal['symbol']
        action = signal['action']
        
        # Skip validation for close orders
        if action == 'close':
            return True
        
        # Get current price
        if symbol not in current_prices:
            self.logger.warning(f"No price data for signal validation: {symbol}")
            return False
        
        current_price = current_prices[symbol]
        
        # Estimate quantity if not provided
        quantity = signal.get('quantity')
        if quantity is None:
            # This would need integration with position sizing logic
            # For now, assume reasonable default
            quantity = portfolio_state['total_equity'] * 0.02 / current_price  # 2% position
        
        # Check position risk
        return self.check_position_risk(symbol, quantity, current_price, portfolio_state)
    
    def _validate_portfolio_level_risk(self, 
                                     signals: List[Dict[str, Any]], 
                                     portfolio_state: Dict[str, Any],
                                     current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """Additional portfolio-level risk validation."""
        # If too many signals, prioritize by some criteria (e.g., signal strength)
        if self.max_concurrent_positions:
            open_positions = portfolio_state['open_positions_count']
            new_positions = len([s for s in signals if s['action'] in ['buy', 'sell', 'long', 'short']])
            
            if open_positions + new_positions > self.max_concurrent_positions:
                # Keep only the strongest signals (would need signal strength metric)
                max_new = self.max_concurrent_positions - open_positions
                signals = signals[:max(0, max_new)]
                self.logger.warning(f"Limited signals due to position count limit: {max_new} allowed")
        
        return signals
    
    def _check_position_size_limit(self, quantity: float, price: float, total_equity: float) -> bool:
        """Check if position size exceeds limits."""
        if not self.max_position_size_pct:
            return True
        
        position_value = abs(quantity * price)
        position_pct = position_value / total_equity * 100
        
        if position_pct > self.max_position_size_pct:
            self.logger.warning(f"Position size {position_pct:.2f}% exceeds limit {self.max_position_size_pct}%")
            return False
        
        return True
    
    def _check_portfolio_heat_limit(self, 
                                  symbol: str, 
                                  quantity: float, 
                                  price: float,
                                  portfolio_state: Dict[str, Any]) -> bool:
        """Check if position would exceed portfolio heat limit."""
        if not self.max_portfolio_heat_pct:
            return True
        
        current_heat = self._calculate_portfolio_heat(portfolio_state)
        new_position_heat = abs(quantity * price) / portfolio_state['total_equity'] * 100
        
        if current_heat + new_position_heat > self.max_portfolio_heat_pct:
            self.logger.warning(f"Portfolio heat {current_heat + new_position_heat:.2f}% would exceed limit {self.max_portfolio_heat_pct}%")
            return False
        
        return True
    
    def _check_concurrent_positions_limit(self, portfolio_state: Dict[str, Any]) -> bool:
        """Check concurrent positions limit."""
        if not self.max_concurrent_positions:
            return True
        
        if portfolio_state['open_positions_count'] >= self.max_concurrent_positions:
            self.logger.warning(f"Concurrent positions {portfolio_state['open_positions_count']} at limit {self.max_concurrent_positions}")
            return False
        
        return True
    
    def _check_minimum_notional(self, quantity: float, price: float) -> bool:
        """Check minimum notional requirement."""
        if not self.min_notional:
            return True
        
        notional = abs(quantity * price)
        if notional < self.min_notional:
            self.logger.warning(f"Position notional ${notional:.2f} below minimum ${self.min_notional}")
            return False
        
        return True
    
    def _calculate_portfolio_leverage(self, portfolio_state: Dict[str, Any]) -> float:
        """Calculate current portfolio leverage."""
        if portfolio_state['total_equity'] <= 0:
            return 0.0
        
        total_position_value = abs(portfolio_state['positions_value'])
        return total_position_value / portfolio_state['total_equity']
    
    def _calculate_portfolio_heat(self, portfolio_state: Dict[str, Any]) -> float:
        """Calculate portfolio heat (total exposure percentage)."""
        if portfolio_state['total_equity'] <= 0:
            return 0.0
        
        total_exposure = abs(portfolio_state['positions_value'])
        return total_exposure / portfolio_state['total_equity'] * 100
    
    def _trigger_risk_event(self, event_type: str, value: float) -> None:
        """Log and handle risk limit violation."""
        violation = {
            'timestamp': datetime.now(),
            'type': event_type,
            'value': value,
            'severity': 'warning'
        }
        
        self.risk_violations.append(violation)
        self.logger.warning(f"Risk event: {event_type} = {value:.2f}")
        
        # Could trigger additional actions like position closure
        # if event_type == 'daily_loss_limit':
        #     self._emergency_position_closure()
    
    def _log_signal_rejection(self, signal: Dict[str, Any], reason: str) -> None:
        """Log signal rejection for analysis."""
        self.logger.info(f"Signal rejected: {signal['symbol']} {signal['action']} - {reason}")
        
        # Could maintain rejection statistics for analysis
        violation = {
            'timestamp': datetime.now(),
            'type': 'signal_rejection',
            'symbol': signal['symbol'],
            'action': signal['action'],
            'reason': reason
        }
        self.risk_violations.append(violation)