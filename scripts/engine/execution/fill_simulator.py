"""
Fill Simulator

Simulates realistic trade fills using OHLC data with proper timing and market impact.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime


class FillSimulator:
    """
    Simulates realistic trade execution with OHLC-based fills.
    
    Features:
    - Realistic fill prices using OHLC data
    - Market impact modeling
    - Partial fill simulation
    - Slippage integration
    - Volume-based execution limits
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize fill simulator with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Execution settings
        execution_config = config.get('execution', {})
        self.enable_slippage = execution_config.get('enable_slippage', True)
        self.enable_market_impact = execution_config.get('enable_market_impact', True)
        self.enable_partial_fills = execution_config.get('enable_partial_fills', False)
        
        # Market impact parameters
        self.market_impact_factor = execution_config.get('market_impact_factor', 0.001)  # 0.1%
        self.volume_limit_pct = execution_config.get('volume_limit_pct', 0.1)  # 10% of bar volume
        
        # Fill quality parameters
        self.min_fill_pct = execution_config.get('min_fill_pct', 0.5)  # Minimum 50% fill
        self.max_slippage_pct = execution_config.get('max_slippage_pct', 0.5)  # Max 0.5% slippage
        
    def simulate_fill(self, 
                     order, 
                     bar_data: Dict[str, float], 
                     target_price: float) -> Optional[Dict[str, Any]]:
        """
        Simulate realistic order fill.
        
        Args:
            order: Order object to fill
            bar_data: OHLCV data for the current bar
            target_price: Target fill price from order manager
            
        Returns:
            Fill information dictionary or None if no fill
        """
        try:
            # Check if fill is possible given OHLC constraints
            if not self._is_fill_possible(order, bar_data, target_price):
                return None
            
            # Calculate realistic fill price
            fill_price = self._calculate_fill_price(order, bar_data, target_price)
            
            # Calculate fill quantity (may be partial)
            fill_quantity = self._calculate_fill_quantity(order, bar_data)
            
            if fill_quantity <= 0:
                return None
            
            # Create fill info
            fill_info = {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'action': order.action,
                'quantity': fill_quantity,
                'fill_price': fill_price,
                'target_price': target_price,
                'timestamp': datetime.now(),
                'bar_data': bar_data.copy(),
                'execution_quality': self._assess_execution_quality(fill_price, target_price, order),
                'metadata': {
                    'slippage': fill_price - target_price if order.is_buy_order() else target_price - fill_price,
                    'market_impact_applied': self.enable_market_impact,
                    'partial_fill': fill_quantity < order.remaining_quantity
                }
            }
            
            self.logger.debug(f"Fill simulated: {order.order_id} - {fill_quantity} @ {fill_price:.4f}")
            
            return fill_info
            
        except Exception as e:
            self.logger.error(f"Error simulating fill for {order.order_id}: {str(e)}")
            return None
    
    def _is_fill_possible(self, order, bar_data: Dict[str, float], target_price: float) -> bool:
        """Check if fill is possible given OHLC constraints."""
        high = bar_data['high']
        low = bar_data['low']
        
        # Market orders can always fill (at open)
        if order.order_type.value == 'market':
            return True
        
        # Limit and stop orders need price to be touched
        if order.is_buy_order():
            # Buy order: price must reach target or below
            return low <= target_price
        else:
            # Sell order: price must reach target or above
            return high >= target_price
    
    def _calculate_fill_price(self, order, bar_data: Dict[str, float], target_price: float) -> float:
        """Calculate realistic fill price with slippage and market impact."""
        base_price = target_price
        
        # Apply slippage if enabled
        if self.enable_slippage:
            slippage = self._calculate_slippage(order, bar_data, base_price)
            if order.is_buy_order():
                base_price += slippage  # Worse for buyer
            else:
                base_price -= slippage  # Worse for seller
        
        # Apply market impact if enabled
        if self.enable_market_impact:
            impact = self._calculate_market_impact(order, bar_data, base_price)
            if order.is_buy_order():
                base_price += impact  # Push price up
            else:
                base_price -= impact  # Push price down
        
        # Ensure price is within OHLC bounds
        final_price = self._constrain_price_to_ohlc(base_price, bar_data, order)
        
        return round(final_price, 8)  # Round to reasonable precision
    
    def _calculate_fill_quantity(self, order, bar_data: Dict[str, float]) -> float:
        """Calculate fill quantity (may be partial based on volume)."""
        remaining_quantity = order.remaining_quantity
        
        # If partial fills are disabled, fill completely
        if not self.enable_partial_fills:
            return remaining_quantity
        
        # Calculate volume-based fill limitation
        bar_volume = bar_data.get('volume', 0)
        if bar_volume <= 0:
            return remaining_quantity  # No volume data, assume full fill
        
        # Limit fill to percentage of bar volume
        max_volume_quantity = bar_volume * self.volume_limit_pct
        
        # For monetary instruments, convert volume to quantity
        # This is simplified - real implementation would depend on instrument type
        if remaining_quantity > max_volume_quantity:
            # Partial fill based on volume constraint
            fill_ratio = max(self.min_fill_pct, max_volume_quantity / remaining_quantity)
            return remaining_quantity * fill_ratio
        
        return remaining_quantity
    
    def _calculate_slippage(self, order, bar_data: Dict[str, float], base_price: float) -> float:
        """Calculate slippage based on market conditions."""
        # Simple slippage model based on volatility
        high = bar_data['high']
        low = bar_data['low']
        
        # Calculate bar volatility as basis for slippage
        if high > low:
            volatility_pct = (high - low) / base_price
        else:
            volatility_pct = 0.001  # Minimum volatility assumption
        
        # Slippage proportional to volatility, capped at maximum
        slippage_pct = min(volatility_pct * 0.1, self.max_slippage_pct / 100)  # 10% of volatility
        
        return base_price * slippage_pct
    
    def _calculate_market_impact(self, order, bar_data: Dict[str, float], base_price: float) -> float:
        """Calculate market impact based on order size."""
        # Simple market impact model
        bar_volume = bar_data.get('volume', 1)
        order_volume = order.remaining_quantity * base_price
        
        # Impact proportional to order size relative to bar volume
        if bar_volume > 0:
            volume_ratio = order_volume / (bar_volume * base_price)
            impact_pct = volume_ratio * self.market_impact_factor
        else:
            impact_pct = self.market_impact_factor
        
        return base_price * impact_pct
    
    def _constrain_price_to_ohlc(self, price: float, bar_data: Dict[str, float], order) -> float:
        """Ensure fill price is within OHLC bounds."""
        high = bar_data['high']
        low = bar_data['low']
        open_price = bar_data['open']
        close_price = bar_data['close']
        
        # Market orders typically fill closer to open
        if order.order_type.value == 'market':
            # Allow some deviation from open, but keep within OHLC
            if order.is_buy_order():
                # Buyers get worse prices (higher), but not above high
                return min(price, high)
            else:
                # Sellers get worse prices (lower), but not below low
                return max(price, low)
        
        # Limit orders must respect OHLC bounds
        return max(low, min(high, price))
    
    def _assess_execution_quality(self, fill_price: float, target_price: float, order) -> str:
        """Assess execution quality relative to target."""
        if abs(fill_price - target_price) < 1e-8:
            return "excellent"
        
        slippage_pct = abs(fill_price - target_price) / target_price * 100
        
        if slippage_pct < 0.1:
            return "good"
        elif slippage_pct < 0.25:
            return "acceptable"
        elif slippage_pct < 0.5:
            return "poor"
        else:
            return "very_poor"
    
    def get_fill_statistics(self) -> Dict[str, Any]:
        """Get fill simulator statistics (would track over time)."""
        return {
            'slippage_enabled': self.enable_slippage,
            'market_impact_enabled': self.enable_market_impact,
            'partial_fills_enabled': self.enable_partial_fills,
            'market_impact_factor': self.market_impact_factor,
            'max_slippage_pct': self.max_slippage_pct,
            'volume_limit_pct': self.volume_limit_pct
        }