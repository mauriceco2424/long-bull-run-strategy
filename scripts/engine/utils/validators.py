"""
Data Validators

Validation utilities for OHLCV data and backtest integrity.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging


class DataValidator:
    """
    Data validation utilities for backtesting.
    
    Ensures data integrity and prevents lookahead bias.
    """
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = logging.getLogger(__name__)
    
    def validate_ohlcv_data(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Validate OHLCV data integrity.
        
        Args:
            data: Dictionary of symbol -> OHLCV DataFrame
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        for symbol, df in data.items():
            # Check required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                errors.append(f"{symbol}: Missing columns {missing_cols}")
            
            # Check for invalid OHLC relationships
            if not missing_cols:
                invalid_ohlc = (
                    (df['high'] < df[['open', 'close']].max(axis=1)) |
                    (df['low'] > df[['open', 'close']].min(axis=1))
                )
                
                if invalid_ohlc.any():
                    errors.append(f"{symbol}: {invalid_ohlc.sum()} invalid OHLC relationships")
            
            # Check for negative prices
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df.columns and (df[col] <= 0).any():
                    errors.append(f"{symbol}: Negative/zero prices in {col}")
        
        return errors
    
    def validate_no_lookahead(self, features_data: Dict[str, pd.DataFrame], 
                            current_time: pd.Timestamp) -> bool:
        """
        Validate that features don't contain future information.
        
        Args:
            features_data: Dictionary of symbol -> features DataFrame
            current_time: Current timestamp being evaluated
            
        Returns:
            True if no lookahead detected
        """
        for symbol, features_df in features_data.items():
            if current_time in features_df.index:
                # Check that we're not using future data
                future_data = features_df.loc[features_df.index > current_time]
                if not future_data.empty:
                    self.logger.warning(f"Potential lookahead in {symbol} features")
                    return False
        
        return True