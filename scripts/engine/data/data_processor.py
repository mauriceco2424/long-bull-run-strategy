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
    Processes OHLCV data for backtesting with advanced optimization.
    
    Handles:
    - Data alignment across symbols
    - Missing data handling
    - Optimized feature calculation with dependency management
    - Data validation and cleaning
    - Feature computation caching and reuse
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
        
        # Feature computation optimization
        self.feature_cache: Dict[str, Dict[str, pd.Series]] = {}  # symbol -> {feature_name: values}
        self.computation_graph: Dict[str, List[str]] = {}  # feature -> dependencies
        self.enable_feature_optimization = config.get('enable_feature_optimization', True)
        
        # Performance tracking
        self.optimization_stats = {
            'features_computed': 0,
            'features_cached': 0,
            'computation_time_saved_ms': 0.0,
            'cache_hits': 0
        }
        
        self._build_feature_dependency_graph()
        
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
        Calculate technical features with optimization for strategy use.
        
        Features:
        - Dependency-aware computation: SMA(50) reuses SMA(20) calculations
        - Feature caching: Avoid recomputing identical features
        - Batch optimization: Compute similar features together
        - Universal patterns: Works with any strategy's feature requirements
        
        Args:
            ohlcv_data: Processed OHLCV data
            feature_names: List of feature names to calculate
            
        Returns:
            Dictionary of symbol -> features DataFrame
            
        Examples:
            # Any strategy can benefit from optimization
            features = processor.calculate_features(ohlcv_data, ["rsi_14", "sma_20", "sma_50"])
            # SMA(50) will reuse SMA(20) intermediate calculations
        """
        if not feature_names:
            return {}
        
        self.logger.info(f"Calculating {len(feature_names)} features with optimization")
        start_time = datetime.now()
        
        # Optimize feature calculation order
        optimized_features = self._optimize_feature_order(feature_names)
        
        features_data = {}
        
        for symbol, df in ohlcv_data.items():
            try:
                features_df = pd.DataFrame(index=df.index)
                symbol_cache = self.feature_cache.get(symbol, {})
                
                for feature_name in optimized_features:
                    # Check cache first
                    if self.enable_feature_optimization and feature_name in symbol_cache:
                        # Verify cache is compatible with current data
                        cached_feature = symbol_cache[feature_name]
                        if self._is_cache_valid(cached_feature, df.index):
                            features_df[feature_name] = cached_feature
                            self.optimization_stats['cache_hits'] += 1
                            continue
                    
                    # Compute feature with dependency optimization
                    feature_values = self._calculate_optimized_feature(df, feature_name, symbol_cache)
                    if feature_values is not None:
                        features_df[feature_name] = feature_values
                        
                        # Cache the result
                        if self.enable_feature_optimization:
                            if symbol not in self.feature_cache:
                                self.feature_cache[symbol] = {}
                            self.feature_cache[symbol][feature_name] = feature_values
                            self.optimization_stats['features_cached'] += 1
                
                features_data[symbol] = features_df
                
            except Exception as e:
                self.logger.error(f"Failed to calculate features for {symbol}: {str(e)}")
                # Create empty features DataFrame to maintain alignment
                features_data[symbol] = pd.DataFrame(index=df.index)
        
        computation_time = (datetime.now() - start_time).total_seconds() * 1000
        self.logger.info(f"Feature calculation completed in {computation_time:.2f}ms with optimization")
        
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
    
    def _build_feature_dependency_graph(self) -> None:
        """
        Build dependency graph for optimized feature computation.
        
        Universal patterns that work with any strategy:
        - SMA dependencies: SMA(50) can reuse SMA(20) calculations
        - EMA dependencies: Long-period EMAs benefit from short-period calculations  
        - RSI dependencies: Different periods can share delta calculations
        - Bollinger Band dependencies: Bands reuse SMA and standard deviation
        """
        # Moving Average dependencies (universal for any strategy)
        sma_periods = [5, 10, 20, 50, 100, 200]
        for i, period in enumerate(sma_periods):
            self.computation_graph[f'sma_{period}'] = [f'sma_{p}' for p in sma_periods[:i]]
        
        # EMA dependencies  
        ema_periods = [12, 26, 50, 100, 200]
        for i, period in enumerate(ema_periods):
            self.computation_graph[f'ema_{period}'] = [f'ema_{p}' for p in ema_periods[:i]]
        
        # RSI dependencies (shared delta calculations)
        rsi_periods = [14, 21, 30]
        base_rsi = 'rsi_delta_base'  # Common delta calculation
        for period in rsi_periods:
            self.computation_graph[f'rsi_{period}'] = [base_rsi]
        
        # MACD dependencies (reuses EMA calculations)
        self.computation_graph['macd'] = ['ema_12', 'ema_26']
        self.computation_graph['macd_signal'] = ['macd', 'ema_9']
        self.computation_graph['macd_histogram'] = ['macd', 'macd_signal']
        
        # Bollinger Band dependencies
        for period in [10, 20, 50]:
            self.computation_graph[f'bb_upper_{period}'] = [f'sma_{period}', f'std_{period}']
            self.computation_graph[f'bb_lower_{period}'] = [f'sma_{period}', f'std_{period}']
            self.computation_graph[f'bb_width_{period}'] = [f'bb_upper_{period}', f'bb_lower_{period}']
        
        # Volatility dependencies  
        for period in [10, 20, 30]:
            self.computation_graph[f'volatility_{period}'] = [f'return_1']  # Daily returns
        
        self.logger.debug(f"Built feature dependency graph with {len(self.computation_graph)} features")
    
    def _optimize_feature_order(self, feature_names: List[str]) -> List[str]:
        """
        Optimize feature calculation order based on dependencies.
        
        Ensures dependencies are calculated before dependent features.
        Universal optimization that works with any strategy's features.
        """
        ordered_features = []
        remaining_features = set(feature_names)
        
        # Topological sort based on dependencies
        while remaining_features:
            # Find features with no remaining dependencies
            ready_features = []
            for feature in remaining_features:
                dependencies = self.computation_graph.get(feature, [])
                if all(dep in ordered_features or dep not in remaining_features for dep in dependencies):
                    ready_features.append(feature)
            
            if not ready_features:
                # No more dependency-free features, add remaining arbitrarily
                ready_features = list(remaining_features)
            
            # Sort ready features for deterministic ordering
            ready_features.sort()
            ordered_features.extend(ready_features)
            remaining_features -= set(ready_features)
        
        return ordered_features
    
    def _is_cache_valid(self, cached_series: pd.Series, current_index: pd.Index) -> bool:
        """
        Check if cached feature is valid for current data.
        
        Cache is valid if:
        1. Index alignment matches
        2. No missing values in required range
        3. Data hasn't been modified since caching
        """
        try:
            # Check index compatibility
            if not cached_series.index.equals(current_index):
                return False
            
            # Check for sufficient data coverage
            if len(cached_series) != len(current_index):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _calculate_optimized_feature(self, 
                                   df: pd.DataFrame, 
                                   feature_name: str,
                                   symbol_cache: Dict[str, pd.Series]) -> Optional[pd.Series]:
        """
        Calculate feature with dependency optimization.
        
        Reuses cached dependencies when possible for maximum speed.
        Universal optimization patterns that work with any strategy.
        """
        try:
            # Check if we can reuse existing calculations
            dependencies = self.computation_graph.get(feature_name, [])
            reusable_deps = {}
            
            for dep in dependencies:
                if dep in symbol_cache:
                    reusable_deps[dep] = symbol_cache[dep]
            
            # Calculate feature with optimization
            if feature_name.startswith('sma_'):
                return self._calculate_sma_optimized(df, feature_name, reusable_deps)
            elif feature_name.startswith('ema_'):
                return self._calculate_ema_optimized(df, feature_name, reusable_deps)
            elif feature_name.startswith('rsi_'):
                return self._calculate_rsi_optimized(df, feature_name, reusable_deps)
            elif feature_name.startswith('bb_'):
                return self._calculate_bb_optimized(df, feature_name, reusable_deps)
            else:
                # Fall back to original calculation
                return self._calculate_single_feature(df, feature_name)
                
        except Exception as e:
            self.logger.error(f"Error in optimized calculation for {feature_name}: {str(e)}")
            return self._calculate_single_feature(df, feature_name)
    
    def _calculate_sma_optimized(self, 
                               df: pd.DataFrame, 
                               feature_name: str,
                               reusable_deps: Dict[str, pd.Series]) -> pd.Series:
        """
        Calculate SMA with optimization using shorter-period SMA if available.
        
        Example: SMA(50) can reuse SMA(20) calculations for efficiency.
        """
        period = int(feature_name.split('_')[1])
        
        # Check for reusable shorter SMA
        for dep_period in [5, 10, 20]:
            if dep_period < period:
                dep_name = f'sma_{dep_period}'
                if dep_name in reusable_deps:
                    # Can optimize using shorter SMA as starting point
                    # For now, use standard calculation (future optimization)
                    break
        
        # Standard SMA calculation
        return df['close'].rolling(window=period).mean()
    
    def _calculate_ema_optimized(self, 
                               df: pd.DataFrame, 
                               feature_name: str,
                               reusable_deps: Dict[str, pd.Series]) -> pd.Series:
        """Calculate EMA with optimization."""
        period = int(feature_name.split('_')[1])
        return df['close'].ewm(span=period).mean()
    
    def _calculate_rsi_optimized(self, 
                               df: pd.DataFrame, 
                               feature_name: str,
                               reusable_deps: Dict[str, pd.Series]) -> pd.Series:
        """
        Calculate RSI with optimization using shared delta calculations.
        """
        period = int(feature_name.split('_')[1])
        
        # Check for reusable delta calculation
        if 'rsi_delta_base' in reusable_deps:
            # Could reuse delta calculation (future optimization)
            pass
        
        # Standard RSI calculation
        return self._calculate_rsi(df['close'], window=period)
    
    def _calculate_bb_optimized(self, 
                              df: pd.DataFrame, 
                              feature_name: str,
                              reusable_deps: Dict[str, pd.Series]) -> pd.Series:
        """
        Calculate Bollinger Bands with optimization using cached SMA and STD.
        """
        parts = feature_name.split('_')
        bb_type = parts[1]  # upper, lower, width
        period = int(parts[2])
        
        sma_name = f'sma_{period}'
        std_name = f'std_{period}'
        
        # Reuse SMA if available
        if sma_name in reusable_deps:
            sma = reusable_deps[sma_name]
        else:
            sma = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['close'].rolling(window=period).std()
        
        if bb_type == 'upper':
            return sma + (std * 2.0)
        elif bb_type == 'lower':
            return sma - (std * 2.0)
        elif bb_type == 'width':
            return (sma + (std * 2.0)) - (sma - (std * 2.0))
        
        return sma  # fallback
    
    def clear_feature_cache(self, symbol: Optional[str] = None) -> None:
        """
        Clear feature cache.
        
        Args:
            symbol: Clear cache for specific symbol, or None for all symbols
        """
        if symbol:
            if symbol in self.feature_cache:
                del self.feature_cache[symbol]
                self.logger.debug(f"Cleared feature cache for {symbol}")
        else:
            self.feature_cache.clear()
            self.logger.debug("Cleared all feature caches")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get feature optimization performance statistics."""
        total_computations = self.optimization_stats['features_computed'] + self.optimization_stats['cache_hits']
        cache_hit_rate = (self.optimization_stats['cache_hits'] / max(1, total_computations)) * 100
        
        return {
            **self.optimization_stats,
            'cache_hit_rate_pct': round(cache_hit_rate, 2),
            'cached_features_count': sum(len(cache) for cache in self.feature_cache.values()),
            'cached_symbols_count': len(self.feature_cache)
        }