"""
Fee Calculator

Handles exchange-specific fee calculations and cost modeling.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging


class FeeCalculator:
    """
    Calculates trading fees based on exchange and trading parameters.
    
    Supports:
    - Maker/taker fee models
    - Tiered fee structures
    - Exchange-specific fee schedules
    - Fee rebates and discounts
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize fee calculator with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract fee configuration
        execution_config = config.get('execution', {})
        fees_config = execution_config.get('fees', {})
        
        # Default fee rates (Binance-like structure)
        self.maker_fee_rate = fees_config.get('maker', 0.001)  # 0.1%
        self.taker_fee_rate = fees_config.get('taker', 0.001)  # 0.1%
        
        # Exchange-specific settings
        self.exchange = self._parse_exchange()
        self.fee_structure = self._initialize_fee_structure()
        
        # Fee calculation settings
        self.minimum_fee = fees_config.get('minimum_fee', 0.0)
        self.fee_currency = fees_config.get('fee_currency', 'USD')
        
        # Volume-based fee tiers
        self.volume_tiers = fees_config.get('volume_tiers', {})
        self.monthly_volume = 0.0  # Would track over time
        
        self.logger.info(f"Fee calculator initialized for {self.exchange}")
    
    def calculate_fees(self, 
                      symbol: str, 
                      quantity: float, 
                      price: float,
                      is_maker: bool = False) -> float:
        """
        Calculate trading fees for an order.
        
        Args:
            symbol: Trading symbol
            quantity: Trade quantity
            price: Trade price
            is_maker: True if maker order, False if taker order
            
        Returns:
            Fee amount in base currency
        """
        try:
            # Calculate trade value
            trade_value = abs(quantity * price)
            
            if trade_value == 0:
                return 0.0
            
            # Determine fee rate
            fee_rate = self._get_fee_rate(symbol, trade_value, is_maker)
            
            # Calculate base fee
            fee_amount = trade_value * fee_rate
            
            # Apply minimum fee if specified
            if self.minimum_fee > 0:
                fee_amount = max(fee_amount, self.minimum_fee)
            
            # Apply any additional adjustments
            fee_amount = self._apply_fee_adjustments(symbol, fee_amount, trade_value)
            
            self.logger.debug(f"Fee calculated: ${fee_amount:.4f} for {symbol} "
                             f"(value: ${trade_value:.2f}, rate: {fee_rate:.4f})")
            
            return round(fee_amount, 8)
            
        except Exception as e:
            self.logger.error(f"Error calculating fees for {symbol}: {str(e)}")
            return 0.0
    
    def calculate_round_trip_fees(self, 
                                 symbol: str, 
                                 quantity: float, 
                                 entry_price: float, 
                                 exit_price: float) -> Dict[str, float]:
        """
        Calculate fees for a complete round-trip trade.
        
        Args:
            symbol: Trading symbol
            quantity: Trade quantity
            entry_price: Entry price
            exit_price: Exit price
            
        Returns:
            Dictionary with entry, exit, and total fees
        """
        entry_fee = self.calculate_fees(symbol, quantity, entry_price, is_maker=False)
        exit_fee = self.calculate_fees(symbol, quantity, exit_price, is_maker=False)
        
        return {
            'entry_fee': entry_fee,
            'exit_fee': exit_fee,
            'total_fee': entry_fee + exit_fee,
            'fee_percentage': (entry_fee + exit_fee) / (quantity * entry_price) * 100
        }
    
    def get_effective_fee_rate(self, symbol: str, trade_value: float, is_maker: bool = False) -> float:
        """
        Get effective fee rate for a given trade.
        
        Args:
            symbol: Trading symbol
            trade_value: Trade value
            is_maker: True if maker order
            
        Returns:
            Effective fee rate as decimal
        """
        return self._get_fee_rate(symbol, trade_value, is_maker)
    
    def update_monthly_volume(self, volume: float) -> None:
        """Update monthly trading volume for tier calculations."""
        self.monthly_volume += volume
        self.logger.debug(f"Monthly volume updated: ${self.monthly_volume:,.2f}")
    
    def reset_monthly_volume(self) -> None:
        """Reset monthly volume (call at start of new month)."""
        self.monthly_volume = 0.0
        self.logger.info("Monthly volume reset for new period")
    
    def get_fee_summary(self) -> Dict[str, Any]:
        """Get fee calculator summary and statistics."""
        return {
            'exchange': self.exchange,
            'maker_fee_rate': self.maker_fee_rate,
            'taker_fee_rate': self.taker_fee_rate,
            'minimum_fee': self.minimum_fee,
            'fee_currency': self.fee_currency,
            'current_monthly_volume': self.monthly_volume,
            'current_tier': self._get_current_volume_tier(),
            'volume_tiers_available': bool(self.volume_tiers)
        }
    
    def _parse_exchange(self) -> str:
        """Parse exchange from configuration."""
        universe = self.config.get('universe', {})
        
        if isinstance(universe, str):
            if ':' in universe:
                return universe.split(':')[0]
            elif '_' in universe:
                return universe.split('_')[0]
        elif isinstance(universe, dict):
            return universe.get('exchange', 'binance')
        
        return 'binance'  # Default
    
    def _initialize_fee_structure(self) -> Dict[str, Any]:
        """Initialize exchange-specific fee structure."""
        # Default Binance-like fee structure
        structures = {
            'binance': {
                'spot': {
                    'maker': 0.001,  # 0.1%
                    'taker': 0.001   # 0.1%
                },
                'futures': {
                    'maker': 0.0002,  # 0.02%
                    'taker': 0.0004   # 0.04%
                }
            },
            'coinbase': {
                'spot': {
                    'maker': 0.005,  # 0.5%
                    'taker': 0.005   # 0.5%
                }
            },
            'kraken': {
                'spot': {
                    'maker': 0.0016,  # 0.16%
                    'taker': 0.0026   # 0.26%
                }
            }
        }
        
        return structures.get(self.exchange.lower(), structures['binance'])
    
    def _get_fee_rate(self, symbol: str, trade_value: float, is_maker: bool) -> float:
        """Get fee rate for specific trade parameters."""
        # Check for volume tier discounts
        tier_rate = self._get_tier_fee_rate(is_maker)
        if tier_rate is not None:
            return tier_rate
        
        # Use standard maker/taker rates
        if is_maker:
            return self.maker_fee_rate
        else:
            return self.taker_fee_rate
    
    def _get_tier_fee_rate(self, is_maker: bool) -> Optional[float]:
        """Get fee rate based on volume tier."""
        if not self.volume_tiers:
            return None
        
        # Find appropriate tier based on monthly volume
        applicable_tier = None
        for tier_volume, tier_rates in sorted(self.volume_tiers.items()):
            if self.monthly_volume >= float(tier_volume):
                applicable_tier = tier_rates
            else:
                break
        
        if applicable_tier:
            fee_type = 'maker' if is_maker else 'taker'
            return applicable_tier.get(fee_type)
        
        return None
    
    def _get_current_volume_tier(self) -> str:
        """Get current volume tier name."""
        if not self.volume_tiers:
            return "standard"
        
        current_tier = "standard"
        for tier_volume in sorted(self.volume_tiers.keys()):
            if self.monthly_volume >= float(tier_volume):
                current_tier = f"tier_{tier_volume}"
            else:
                break
        
        return current_tier
    
    def _apply_fee_adjustments(self, symbol: str, fee_amount: float, trade_value: float) -> float:
        """Apply any additional fee adjustments."""
        # Could implement:
        # - Symbol-specific fee adjustments
        # - Promotional discounts
        # - Fee rebates for high volume
        # - Special handling for certain pairs
        
        return fee_amount
    
    def estimate_daily_fees(self, daily_volume: float) -> Dict[str, float]:
        """
        Estimate daily fees based on expected volume.
        
        Args:
            daily_volume: Expected daily trading volume
            
        Returns:
            Dictionary with fee estimates
        """
        # Assume 50/50 maker/taker split
        maker_volume = daily_volume * 0.5
        taker_volume = daily_volume * 0.5
        
        maker_fees = maker_volume * self.maker_fee_rate
        taker_fees = taker_volume * self.taker_fee_rate
        
        return {
            'maker_fees': maker_fees,
            'taker_fees': taker_fees,
            'total_fees': maker_fees + taker_fees,
            'average_rate': (maker_fees + taker_fees) / daily_volume if daily_volume > 0 else 0
        }