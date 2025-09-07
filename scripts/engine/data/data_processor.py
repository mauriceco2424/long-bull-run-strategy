"""
Data Processor

Handles OHLCV data cleaning, alignment, and feature calculation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta


class DataProcessor:
    """
    Processes OHLCV data for backtesting.
    
    Handles:
    - Data alignment across symbols
    - Missing data handling
    - Feature calculation
    - Data validation and cleaning
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data processor with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Missing data handling configuration
        self.missing_data_policy = config.get('missing_data_policy', 'forward_fill')
        self.max_missing_pct = config.get('max_missing_pct', 0.1)  # 10% max missing
        
    def process_ohlcv_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Process raw OHLCV data for backtesting.
        
        Args:
            raw_data: Dictionary of symbol -> OHLCV DataFrame
            
        Returns:
            Processed and aligned OHLCV data
        """
        self.logger.info(f"Processing OHLCV data for {len(raw_data)} symbols")
        
        if not raw_data:
            raise ValueError("No data provided for processing")
        
        # Step 1: Align timestamps across all symbols
        aligned_data = self._align_timestamps(raw_data)
        
        # Step 2: Handle missing data
        cleaned_data = self._handle_missing_data(aligned_data)
        
        # Step 3: Validate data quality
        validated_data = self._validate_processed_data(cleaned_data)
        
        self.logger.info(f"Data processing complete: {len(validated_data)} symbols")
        return validated_data
    
    def calculate_features(self, 
                          ohlcv_data: Dict[str, pd.DataFrame],
                          feature_names: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Calculate technical features for strategy use.
        
        Args:
            ohlcv_data: Processed OHLCV data
            feature_names: List of feature names to calculate
            
        Returns:
            Dictionary of symbol -> features DataFrame
        """
        if not feature_names:
            return {}
        
        self.logger.info(f"Calculating features: {feature_names}")
        
        features_data = {}
        
        for symbol, df in ohlcv_data.items():
            try:
                features_df = pd.DataFrame(index=df.index)
                
                for feature_name in feature_names:
                    feature_values = self._calculate_single_feature(df, feature_name)
                    if feature_values is not None:
                        features_df[feature_name] = feature_values
                
                features_data[symbol] = features_df
                
            except Exception as e:
                self.logger.error(f"Failed to calculate features for {symbol}: {str(e)}")
                # Create empty features DataFrame to maintain alignment
                features_data[symbol] = pd.DataFrame(index=df.index)
        
        return features_data
    
    def _align_timestamps(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Align timestamps across all symbols."""
        if len(raw_data) == 1:
            return raw_data
        
        # Find common timestamp range
        all_indices = [df.index for df in raw_data.values()]
        
        # Get intersection of all timestamps
        common_index = all_indices[0]
        for idx in all_indices[1:]:
            common_index = common_index.intersection(idx)
        
        if len(common_index) == 0:
            raise ValueError("No common timestamps found across symbols")
        
        self.logger.info(f"Aligned to {len(common_index)} common timestamps")
        
        # Align all DataFrames to common timestamps
        aligned_data = {}
        for symbol, df in raw_data.items():
            aligned_data[symbol] = df.loc[common_index].copy()
        
        return aligned_data
    
    def _handle_missing_data(self, aligned_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Handle missing data according to policy."""
        cleaned_data = {}
        
        for symbol, df in aligned_data.items():
            # Check missing data percentage
            missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns))
            
            if missing_pct > self.max_missing_pct:
                self.logger.warning(f"High missing data percentage for {symbol}: {missing_pct:.2%}")
            
            # Apply missing data policy
            if self.missing_data_policy == 'forward_fill':
                cleaned_df = df.fillna(method='ffill')
            elif self.missing_data_policy == 'backward_fill':
                cleaned_df = df.fillna(method='bfill')
            elif self.missing_data_policy == 'interpolate':
                cleaned_df = df.interpolate(method='linear')
            elif self.missing_data_policy == 'drop':
                cleaned_df = df.dropna()
            else:
                # Default: forward fill
                cleaned_df = df.fillna(method='ffill')
            
            # Drop any remaining NaN values
            cleaned_df = cleaned_df.dropna()
            
            if cleaned_df.empty:
                self.logger.error(f"No data remaining for {symbol} after cleaning")
                continue
            
            cleaned_data[symbol] = cleaned_df
        
        return cleaned_data
    
    def _validate_processed_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Validate processed data quality."""
        validated_data = {}
        
        for symbol, df in data.items():
            try:
                # Basic validation
                if df.empty:
                    self.logger.error(f"Empty data for {symbol}")
                    continue
                
                # Check for required columns
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns for {symbol}: {missing_cols}")
                    continue
                
                # Validate OHLC relationships
                invalid_ohlc = (
                    (df['high'] < df[['open', 'close']].max(axis=1)) |
                    (df['low'] > df[['open', 'close']].min(axis=1))
                )
                
                if invalid_ohlc.any():
                    invalid_count = invalid_ohlc.sum()
                    self.logger.warning(f"Invalid OHLC relationships in {symbol}: {invalid_count} bars")
                    # Fix invalid relationships
                    df.loc[invalid_ohlc, 'high'] = df.loc[invalid_ohlc, ['open', 'close']].max(axis=1)
                    df.loc[invalid_ohlc, 'low'] = df.loc[invalid_ohlc, ['open', 'close']].min(axis=1)
                
                # Check for negative prices
                negative_prices = (df[['open', 'high', 'low', 'close']] <= 0).any(axis=1)
                if negative_prices.any():
                    self.logger.error(f"Negative prices in {symbol}: {negative_prices.sum()} bars")
                    df = df[~negative_prices]
                
                # Check for extreme price changes (potential data errors)
                price_changes = df['close'].pct_change().abs()
                extreme_changes = price_changes > 0.5  # 50% change threshold
                if extreme_changes.any():
                    self.logger.warning(f"Extreme price changes in {symbol}: {extreme_changes.sum()} bars")
                
                # Ensure chronological order
                if not df.index.is_monotonic_increasing:
                    df = df.sort_index()
                    self.logger.warning(f"Data reordered chronologically for {symbol}")
                
                validated_data[symbol] = df
                
            except Exception as e:
                self.logger.error(f"Validation failed for {symbol}: {str(e)}")
                continue
        
        if not validated_data:
            raise ValueError("No valid data remaining after validation")
        
        return validated_data
    
    def _calculate_single_feature(self, df: pd.DataFrame, feature_name: str) -> Optional[pd.Series]:
        """Calculate a single technical feature."""
        try:
            if feature_name == 'sma_20':
                return df['close'].rolling(window=20).mean()
            elif feature_name == 'sma_50':
                return df['close'].rolling(window=50).mean()
            elif feature_name == 'ema_12':
                return df['close'].ewm(span=12).mean()
            elif feature_name == 'ema_26':
                return df['close'].ewm(span=26).mean()
            elif feature_name == 'rsi_14':
                return self._calculate_rsi(df['close'], window=14)
            elif feature_name == 'macd':
                return self._calculate_macd(df['close'])
            elif feature_name == 'bb_upper':
                return self._calculate_bollinger_bands(df['close'])[0]
            elif feature_name == 'bb_lower':
                return self._calculate_bollinger_bands(df['close'])[1]
            elif feature_name == 'volume_sma_20':
                return df['volume'].rolling(window=20).mean()
            elif feature_name == 'volatility_20':
                return df['close'].pct_change().rolling(window=20).std()
            elif feature_name.startswith('return_'):
                # Extract period from feature name (e.g., return_1, return_5)
                period = int(feature_name.split('_')[1])
                return df['close'].pct_change(periods=period)
            else:
                self.logger.warning(f"Unknown feature: {feature_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calculating {feature_name}: {str(e)}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """Calculate MACD line (not including signal or histogram)."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, lower_band
    
    def get_data_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Get summary statistics of processed data."""
        if not data:
            return {}
        
        summary = {
            'symbols': list(data.keys()),
            'symbol_count': len(data),
            'date_range': {},
            'bar_counts': {},
            'data_quality': {}
        }
        
        all_start_dates = []
        all_end_dates = []
        
        for symbol, df in data.items():
            if not df.empty:
                start_date = df.index.min()
                end_date = df.index.max()
                
                all_start_dates.append(start_date)
                all_end_dates.append(end_date)
                
                summary['bar_counts'][symbol] = len(df)
                summary['data_quality'][symbol] = {
                    'missing_values': df.isnull().sum().sum(),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
        
        if all_start_dates and all_end_dates:
            summary['date_range'] = {
                'start': min(all_start_dates).isoformat(),
                'end': max(all_end_dates).isoformat(),
                'total_days': (max(all_end_dates) - min(all_start_dates)).days
            }
        
        return summary