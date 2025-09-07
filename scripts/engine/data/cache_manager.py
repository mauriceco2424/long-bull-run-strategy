"""
Cache Manager

Handles caching of fetched market data to avoid repeated API calls.
"""

import os
import json
import pickle
import hashlib
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging


class CacheManager:
    """
    Manages local caching of market data.
    
    Features:
    - File-based caching with compression
    - Cache expiration handling
    - Data integrity validation
    - Efficient cache key generation
    """
    
    def __init__(self, cache_dir: str = "data/cache", cache_ttl_hours: int = 24):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.cache_dir = cache_dir
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache metadata file
        self.metadata_file = os.path.join(cache_dir, "cache_metadata.json")
        self.metadata = self._load_metadata()
    
    def get_cached_data(self, 
                       symbol: str,
                       start_date: str,
                       end_date: str,
                       timeframe: str) -> Optional[pd.DataFrame]:
        """
        Retrieve cached data if available and valid.
        
        Args:
            symbol: Trading symbol
            start_date: Start date string
            end_date: End date string
            timeframe: Timeframe string
            
        Returns:
            Cached DataFrame or None if not available
        """
        cache_key = self._generate_cache_key(symbol, start_date, end_date, timeframe)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        # Check if cache file exists
        if not os.path.exists(cache_file):
            return None
        
        # Check cache expiration
        if self._is_cache_expired(cache_key):
            self._remove_cache_entry(cache_key)
            return None
        
        try:
            # Load cached data
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Validate data integrity
            if self._validate_cached_data(cached_data, symbol, start_date, end_date):
                self.logger.debug(f"Cache hit for {cache_key}")
                return cached_data
            else:
                self.logger.warning(f"Cache validation failed for {cache_key}")
                self._remove_cache_entry(cache_key)
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading cached data for {cache_key}: {str(e)}")
            self._remove_cache_entry(cache_key)
            return None
    
    def cache_data(self,
                   symbol: str,
                   data: pd.DataFrame,
                   start_date: str,
                   end_date: str,
                   timeframe: str) -> None:
        """
        Cache market data.
        
        Args:
            symbol: Trading symbol
            data: OHLCV DataFrame to cache
            start_date: Start date string
            end_date: End date string
            timeframe: Timeframe string
        """
        if data is None or data.empty:
            return
        
        cache_key = self._generate_cache_key(symbol, start_date, end_date, timeframe)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            # Save data to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Update metadata
            self.metadata[cache_key] = {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'timeframe': timeframe,
                'cached_at': datetime.now().isoformat(),
                'file_size': os.path.getsize(cache_file),
                'row_count': len(data),
                'checksum': self._calculate_data_checksum(data)
            }
            
            self._save_metadata()
            self.logger.debug(f"Cached data for {cache_key}")
            
        except Exception as e:
            self.logger.error(f"Error caching data for {cache_key}: {str(e)}")
    
    def clear_cache(self, older_than_hours: Optional[int] = None) -> None:
        """
        Clear cache entries.
        
        Args:
            older_than_hours: Clear entries older than N hours. If None, clear all.
        """
        if older_than_hours is None:
            # Clear all cache
            for cache_key in list(self.metadata.keys()):
                self._remove_cache_entry(cache_key)
            self.logger.info("Cleared all cache entries")
        else:
            # Clear old entries
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            expired_keys = []
            
            for cache_key, metadata in self.metadata.items():
                cached_at = datetime.fromisoformat(metadata['cached_at'])
                if cached_at < cutoff_time:
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                self._remove_cache_entry(cache_key)
            
            self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'total_entries': len(self.metadata),
            'total_size_mb': 0,
            'oldest_entry': None,
            'newest_entry': None,
            'symbols_cached': set(),
            'timeframes_cached': set()
        }
        
        if not self.metadata:
            return stats
        
        cached_times = []
        
        for cache_key, metadata in self.metadata.items():
            # Size calculation
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
            if os.path.exists(cache_file):
                stats['total_size_mb'] += os.path.getsize(cache_file) / (1024 * 1024)
            
            # Time tracking
            cached_at = datetime.fromisoformat(metadata['cached_at'])
            cached_times.append(cached_at)
            
            # Symbol and timeframe tracking
            stats['symbols_cached'].add(metadata['symbol'])
            stats['timeframes_cached'].add(metadata['timeframe'])
        
        if cached_times:
            stats['oldest_entry'] = min(cached_times).isoformat()
            stats['newest_entry'] = max(cached_times).isoformat()
        
        stats['symbols_cached'] = list(stats['symbols_cached'])
        stats['timeframes_cached'] = list(stats['timeframes_cached'])
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        
        return stats
    
    def _generate_cache_key(self, symbol: str, start_date: str, end_date: str, timeframe: str) -> str:
        """Generate unique cache key for data request."""
        key_string = f"{symbol}_{start_date}_{end_date}_{timeframe}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_expired(self, cache_key: str) -> bool:
        """Check if cache entry is expired."""
        if cache_key not in self.metadata:
            return True
        
        cached_at = datetime.fromisoformat(self.metadata[cache_key]['cached_at'])
        return datetime.now() - cached_at > self.cache_ttl
    
    def _validate_cached_data(self, 
                             data: pd.DataFrame,
                             symbol: str,
                             start_date: str,
                             end_date: str) -> bool:
        """Validate cached data integrity."""
        try:
            # Check if data is a valid DataFrame
            if not isinstance(data, pd.DataFrame) or data.empty:
                return False
            
            # Check required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_cols):
                return False
            
            # Check date range coverage
            data_start = data.index.min()
            data_end = data.index.max()
            
            # Allow for some flexibility in date range (data might extend beyond requested range)
            requested_start = pd.Timestamp(start_date)
            requested_end = pd.Timestamp(end_date)
            
            if data_start > requested_start or data_end < requested_end:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _calculate_data_checksum(self, data: pd.DataFrame) -> str:
        """Calculate checksum of DataFrame for integrity verification."""
        try:
            # Create a string representation of the data
            data_string = data.to_csv()
            return hashlib.md5(data_string.encode()).hexdigest()
        except Exception:
            return ""
    
    def _remove_cache_entry(self, cache_key: str) -> None:
        """Remove cache entry and its metadata."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        # Remove file if it exists
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception as e:
                self.logger.error(f"Error removing cache file {cache_file}: {str(e)}")
        
        # Remove from metadata
        if cache_key in self.metadata:
            del self.metadata[cache_key]
            self._save_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file."""
        if not os.path.exists(self.metadata_file):
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cache metadata: {str(e)}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache metadata: {str(e)}")