"""
Filter Gate Manager

Universal filter optimization system that works with any strategy.
Provides monotone filter caching and smart symbol universe management.
"""

import logging
from typing import Dict, List, Set, Any, Optional, Callable, Tuple
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
from enum import Enum


class FilterType(Enum):
    """Types of filters for optimization classification."""
    MONOTONE_GREATER = "monotone_greater"  # RSI > X, Volume > Y
    MONOTONE_LESSER = "monotone_lesser"    # Volatility < X, Drawdown < Y  
    BOOLEAN = "boolean"                    # Market cap category, sector
    RANGE = "range"                        # Price between X and Y
    CUSTOM = "custom"                      # Non-optimizable custom logic


@dataclass
class FilterResult:
    """Result of a filter operation."""
    filter_name: str
    filter_type: FilterType
    threshold_value: Any
    passed_symbols: Set[str]
    timestamp: datetime
    computation_time_ms: float


@dataclass
class FilterDefinition:
    """Definition of a filter for optimization purposes."""
    name: str
    filter_type: FilterType
    compute_func: Callable
    dependency_features: List[str]
    description: str


class FilterGateManager:
    """
    Universal filter optimization system.
    
    Key Features:
    - Monotone filter caching: If RSI > 30 passes for a symbol, cache for RSI > 25, 20, etc.
    - Smart symbol elimination: Remove symbols that can't pass stricter filters
    - Universal application: Works with ANY threshold-based strategy filter
    - Performance tracking: Measure and optimize filter computation time
    
    Usage Examples:
    - RSI-based filters: RSI > 30, RSI > 50, etc.
    - Volume filters: Volume > 1M, Volume > 5M, etc.
    - Price filters: Price > SMA(20), Price > SMA(50), etc.
    - Custom filters: Any monotone threshold-based condition
    """
    
    def __init__(self):
        """Initialize filter gate manager."""
        self.logger = logging.getLogger(__name__)
        
        # Filter result cache: {filter_name: {threshold: FilterResult}}
        self.filter_cache: Dict[str, Dict[Any, FilterResult]] = {}
        
        # Filter definitions registry
        self.registered_filters: Dict[str, FilterDefinition] = {}
        
        # Performance tracking
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'filters_computed': 0,
            'symbols_eliminated': 0,
            'total_computation_time_ms': 0.0
        }
        
        self.logger.info("FilterGateManager initialized for universal filter optimization")
    
    def register_filter(self, 
                       name: str,
                       filter_type: FilterType,
                       compute_func: Callable,
                       dependency_features: List[str],
                       description: str) -> None:
        """
        Register a filter for optimization.
        
        Args:
            name: Unique filter name (e.g., "rsi_threshold", "volume_filter")
            filter_type: Type of filter for optimization classification
            compute_func: Function that computes the filter
            dependency_features: List of required features/indicators
            description: Human-readable description
            
        Example:
            manager.register_filter(
                "rsi_threshold", 
                FilterType.MONOTONE_GREATER,
                lambda data, threshold: data['rsi_14'] > threshold,
                ["rsi_14"],
                "RSI above threshold filter"
            )
        """
        filter_def = FilterDefinition(
            name=name,
            filter_type=filter_type, 
            compute_func=compute_func,
            dependency_features=dependency_features,
            description=description
        )
        
        self.registered_filters[name] = filter_def
        self.filter_cache[name] = {}
        
        self.logger.debug(f"Registered filter: {name} ({filter_type.value})")
    
    def apply_filter(self,
                    filter_name: str,
                    threshold_value: Any,
                    symbol_data: Dict[str, pd.DataFrame],
                    features_data: Dict[str, pd.DataFrame],
                    current_timestamp: datetime) -> Set[str]:
        """
        Apply a filter with optimization.
        
        Args:
            filter_name: Name of registered filter
            threshold_value: Threshold value for the filter
            symbol_data: OHLCV data for all symbols
            features_data: Technical features for all symbols  
            current_timestamp: Current evaluation timestamp
            
        Returns:
            Set of symbols that pass the filter
            
        Examples:
            # RSI filter
            passing_symbols = manager.apply_filter(
                "rsi_threshold", 30, ohlcv_data, features_data, current_time
            )
            
            # Volume filter  
            high_volume_symbols = manager.apply_filter(
                "volume_threshold", 1000000, ohlcv_data, features_data, current_time
            )
        """
        if filter_name not in self.registered_filters:
            raise ValueError(f"Filter '{filter_name}' not registered")
        
        filter_def = self.registered_filters[filter_name]
        
        # Check for optimization opportunities
        cached_result = self._check_cache_optimization(filter_name, threshold_value, filter_def.filter_type)
        if cached_result:
            self.performance_stats['cache_hits'] += 1
            self.logger.debug(f"Cache hit for {filter_name} threshold {threshold_value}")
            return cached_result
        
        # Compute filter result
        start_time = datetime.now()
        passed_symbols = self._compute_filter(filter_def, threshold_value, symbol_data, features_data, current_timestamp)
        computation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Cache the result
        result = FilterResult(
            filter_name=filter_name,
            filter_type=filter_def.filter_type,
            threshold_value=threshold_value,
            passed_symbols=passed_symbols,
            timestamp=current_timestamp,
            computation_time_ms=computation_time
        )
        
        self.filter_cache[filter_name][threshold_value] = result
        
        # Update performance stats
        self.performance_stats['cache_misses'] += 1
        self.performance_stats['filters_computed'] += 1
        self.performance_stats['total_computation_time_ms'] += computation_time
        
        self.logger.debug(f"Computed filter {filter_name} threshold {threshold_value}: {len(passed_symbols)} symbols passed")
        
        return passed_symbols
    
    def get_optimized_symbol_universe(self, 
                                    base_symbols: List[str],
                                    filter_sequence: List[Tuple[str, Any]]) -> Set[str]:
        """
        Get optimized symbol universe by applying filters in optimal order.
        
        Args:
            base_symbols: Initial symbol universe
            filter_sequence: List of (filter_name, threshold) tuples
            
        Returns:
            Set of symbols that pass all filters
            
        Example:
            # Apply multiple filters efficiently
            universe = manager.get_optimized_symbol_universe(
                all_symbols,
                [
                    ("rsi_threshold", 30),      # Apply RSI > 30 first
                    ("volume_threshold", 1000000), # Then Volume > 1M  
                    ("price_above_sma", 50)     # Finally Price > SMA(50)
                ]
            )
        """
        current_universe = set(base_symbols)
        
        # Sort filters by expected selectivity (most restrictive first)
        ordered_filters = self._optimize_filter_order(filter_sequence)
        
        for filter_name, threshold in ordered_filters:
            if not current_universe:  # No symbols left
                break
                
            # Only test symbols that are still in the universe
            filtered_symbols = self.apply_filter(
                filter_name, threshold, {}, {}, datetime.now()
            )
            
            # Intersect with current universe
            current_universe = current_universe.intersection(filtered_symbols)
            
            eliminated = len(filtered_symbols) - len(current_universe)
            self.performance_stats['symbols_eliminated'] += eliminated
        
        return current_universe
    
    def _check_cache_optimization(self, 
                                filter_name: str, 
                                threshold: Any, 
                                filter_type: FilterType) -> Optional[Set[str]]:
        """Check if we can optimize using cached results."""
        if filter_name not in self.filter_cache:
            return None
        
        cached_results = self.filter_cache[filter_name]
        if not cached_results:
            return None
        
        # Monotone optimization logic
        if filter_type == FilterType.MONOTONE_GREATER:
            return self._optimize_monotone_greater(cached_results, threshold)
        elif filter_type == FilterType.MONOTONE_LESSER:
            return self._optimize_monotone_lesser(cached_results, threshold)
        elif filter_type == FilterType.BOOLEAN:
            # Boolean filters: exact match only
            return cached_results.get(threshold, {}).get('passed_symbols')
        
        return None
    
    def _optimize_monotone_greater(self, cached_results: Dict[Any, FilterResult], threshold: Any) -> Optional[Set[str]]:
        """
        Optimize monotone greater filters (e.g., RSI > X).
        
        Logic: If we want RSI > 30 and have RSI > 25 cached,
        the result is a subset of RSI > 25 symbols.
        """
        # Find the closest cached threshold that is <= our target
        suitable_thresholds = [t for t in cached_results.keys() if t <= threshold]
        
        if not suitable_thresholds:
            return None
        
        # Use the highest suitable threshold (most restrictive that's still useful)
        best_threshold = max(suitable_thresholds)
        
        if best_threshold == threshold:
            # Exact match
            return cached_results[best_threshold].passed_symbols
        else:
            # We can use this as a starting point for further filtering
            # For now, return None to trigger full computation
            # Future enhancement: compute only the delta
            return None
    
    def _optimize_monotone_lesser(self, cached_results: Dict[Any, FilterResult], threshold: Any) -> Optional[Set[str]]:
        """
        Optimize monotone lesser filters (e.g., Volatility < X).
        
        Logic: If we want Vol < 0.05 and have Vol < 0.1 cached,
        the result is a subset of Vol < 0.1 symbols.
        """
        # Find the closest cached threshold that is >= our target
        suitable_thresholds = [t for t in cached_results.keys() if t >= threshold]
        
        if not suitable_thresholds:
            return None
        
        # Use the lowest suitable threshold (most restrictive that's still useful)
        best_threshold = min(suitable_thresholds)
        
        if best_threshold == threshold:
            # Exact match
            return cached_results[best_threshold].passed_symbols
        else:
            # Future enhancement: compute only the delta
            return None
    
    def _compute_filter(self,
                       filter_def: FilterDefinition,
                       threshold_value: Any,
                       symbol_data: Dict[str, pd.DataFrame],
                       features_data: Dict[str, pd.DataFrame],
                       current_timestamp: datetime) -> Set[str]:
        """Compute filter result for all symbols."""
        passed_symbols = set()
        
        for symbol in symbol_data.keys():
            try:
                # Get data for this symbol
                symbol_ohlcv = symbol_data.get(symbol)
                symbol_features = features_data.get(symbol)
                
                if symbol_ohlcv is None or symbol_features is None:
                    continue
                
                # Check if we have data for the current timestamp
                if current_timestamp not in symbol_features.index:
                    continue
                
                # Apply filter function
                symbol_data_point = {
                    'ohlcv': symbol_ohlcv.loc[current_timestamp],
                    'features': symbol_features.loc[current_timestamp]
                }
                
                # Merge features into a single series for easy access
                combined_data = {**symbol_data_point['ohlcv'].to_dict(), 
                               **symbol_data_point['features'].to_dict()}
                
                if filter_def.compute_func(combined_data, threshold_value):
                    passed_symbols.add(symbol)
                    
            except Exception as e:
                self.logger.warning(f"Error computing filter {filter_def.name} for {symbol}: {str(e)}")
                continue
        
        return passed_symbols
    
    def _optimize_filter_order(self, filter_sequence: List[Tuple[str, Any]]) -> List[Tuple[str, Any]]:
        """
        Optimize the order of filter application.
        
        Strategy: Apply most selective filters first to reduce computation.
        """
        # For now, return as-is. Future enhancement: use historical selectivity data
        return filter_sequence
    
    def clear_cache(self, filter_name: Optional[str] = None) -> None:
        """
        Clear filter cache.
        
        Args:
            filter_name: Specific filter to clear, or None for all filters
        """
        if filter_name:
            if filter_name in self.filter_cache:
                self.filter_cache[filter_name].clear()
                self.logger.debug(f"Cleared cache for filter: {filter_name}")
        else:
            self.filter_cache.clear()
            self.logger.debug("Cleared all filter caches")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total_requests = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
        cache_hit_rate = (self.performance_stats['cache_hits'] / max(1, total_requests)) * 100
        
        return {
            **self.performance_stats,
            'cache_hit_rate_pct': round(cache_hit_rate, 2),
            'avg_computation_time_ms': round(
                self.performance_stats['total_computation_time_ms'] / max(1, self.performance_stats['filters_computed']), 2
            )
        }
    
    def get_registered_filters(self) -> Dict[str, str]:
        """Get summary of registered filters."""
        return {name: f"{filter_def.filter_type.value} - {filter_def.description}" 
                for name, filter_def in self.registered_filters.items()}
    
    def register_common_filters(self) -> None:
        """
        Register commonly used filters that work with any strategy.
        
        These are examples that agents can use and extend.
        """
        # RSI-based filters (works for any RSI period)
        def rsi_greater_filter(data: Dict[str, float], threshold: float) -> bool:
            rsi_keys = [k for k in data.keys() if k.startswith('rsi_')]
            if not rsi_keys:
                return False
            # Use first available RSI (agents should specify which RSI they want)
            return data[rsi_keys[0]] > threshold
        
        self.register_filter(
            "rsi_threshold",
            FilterType.MONOTONE_GREATER,
            rsi_greater_filter,
            ["rsi_14", "rsi_21", "rsi_30"],  # Common RSI periods
            "RSI above threshold - works with any RSI period"
        )
        
        # Volume filters
        def volume_filter(data: Dict[str, float], threshold: float) -> bool:
            return data.get('volume', 0) > threshold
        
        self.register_filter(
            "volume_threshold", 
            FilterType.MONOTONE_GREATER,
            volume_filter,
            ["volume"],
            "Volume above threshold"
        )
        
        # Price above moving average filters  
        def price_above_ma_filter(data: Dict[str, float], ma_period: int) -> bool:
            ma_key = f"sma_{ma_period}"
            if ma_key not in data:
                return False
            return data['close'] > data[ma_key]
        
        self.register_filter(
            "price_above_sma",
            FilterType.MONOTONE_GREATER, 
            price_above_ma_filter,
            ["close", "sma_10", "sma_20", "sma_50", "sma_200"],
            "Price above Simple Moving Average"
        )
        
        # Volatility filters (lower is more restrictive)
        def volatility_filter(data: Dict[str, float], threshold: float) -> bool:
            volatility_keys = [k for k in data.keys() if 'volatility' in k]
            if not volatility_keys:
                return False
            return data[volatility_keys[0]] < threshold
        
        self.register_filter(
            "volatility_threshold",
            FilterType.MONOTONE_LESSER,
            volatility_filter, 
            ["volatility_20", "volatility_30"],
            "Volatility below threshold"
        )
        
        self.logger.info("Registered common filters for universal strategy use")