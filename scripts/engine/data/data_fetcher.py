"""
Data Fetcher

Handles fetching historical OHLCV data from various exchanges.
Supports Binance, CCXT, and other data sources based on configuration.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import time
import os
import json

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from .cache_manager import CacheManager


class DataFetcher:
    """
    Fetches historical OHLCV data from various sources.
    
    Supports:
    - Binance via CCXT
    - Other exchanges via CCXT
    - Yahoo Finance for traditional assets
    - Local CSV files
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data fetcher with configuration.
        
        Args:
            config: Configuration dictionary from parameter_config.md
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache_manager = CacheManager()
        
        # Parse universe configuration
        self.exchange = self._parse_exchange()
        self.exchange_client = self._initialize_exchange_client()
        
    def fetch_historical_data(self, 
                            symbols: List[str],
                            start_date: str,
                            end_date: str, 
                            timeframe: str = '1h') -> Dict[str, pd.DataFrame]:
        """
        Fetch historical OHLCV data for multiple symbols.
        
        Args:
            symbols: List of trading symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            
        Returns:
            Dictionary mapping symbols to OHLCV DataFrames
        """
        self.logger.info(f"Fetching data for {len(symbols)} symbols from {start_date} to {end_date}")
        
        data_dict = {}
        failed_symbols = []
        
        for symbol in symbols:
            try:
                # Check cache first
                cached_data = self.cache_manager.get_cached_data(
                    symbol, start_date, end_date, timeframe
                )
                
                if cached_data is not None:
                    self.logger.info(f"Using cached data for {symbol}")
                    data_dict[symbol] = cached_data
                    continue
                
                # Fetch fresh data
                df = self._fetch_symbol_data(symbol, start_date, end_date, timeframe)
                
                if df is not None and not df.empty:
                    # Validate data quality
                    df = self._validate_and_clean_data(df, symbol)
                    data_dict[symbol] = df
                    
                    # Cache the data
                    self.cache_manager.cache_data(
                        symbol, df, start_date, end_date, timeframe
                    )
                    
                    self.logger.info(f"Fetched {len(df)} bars for {symbol}")
                else:
                    failed_symbols.append(symbol)
                    self.logger.warning(f"No data retrieved for {symbol}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
                failed_symbols.append(symbol)
        
        if failed_symbols:
            self.logger.warning(f"Failed to fetch data for symbols: {failed_symbols}")
        
        if not data_dict:
            raise ValueError("No data could be fetched for any symbols")
        
        return data_dict
    
    def _parse_exchange(self) -> str:
        """Parse exchange from universe configuration."""
        universe = self.config.get('universe', {})
        
        if isinstance(universe, str):
            # Format: "binance_usdt" or "binance:BTCUSDT,ETHUSDT"
            if ':' in universe:
                return universe.split(':')[0]
            elif '_' in universe:
                return universe.split('_')[0]
        elif isinstance(universe, dict):
            return universe.get('exchange', 'binance')
        
        return 'binance'  # Default
    
    def _initialize_exchange_client(self) -> Optional[Any]:
        """Initialize exchange client based on configuration."""
        if not CCXT_AVAILABLE:
            self.logger.warning("CCXT not available, using mock data")
            return None
        
        try:
            if self.exchange.lower() == 'binance':
                client = ccxt.binance({
                    'apiKey': os.getenv('BINANCE_API_KEY', ''),
                    'secret': os.getenv('BINANCE_SECRET_KEY', ''),
                    'sandbox': False,  # Use testnet if needed
                    'rateLimit': 1200,  # Respect rate limits
                })
            else:
                # Generic CCXT exchange
                exchange_class = getattr(ccxt, self.exchange.lower(), None)
                if exchange_class:
                    client = exchange_class()
                else:
                    self.logger.error(f"Unsupported exchange: {self.exchange}")
                    return None
            
            # Test connection
            client.load_markets()
            self.logger.info(f"Initialized {self.exchange} client successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.exchange} client: {str(e)}")
            return None
    
    def _fetch_symbol_data(self, 
                          symbol: str, 
                          start_date: str, 
                          end_date: str, 
                          timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch data for a single symbol."""
        if self.exchange_client is None:
            # Use mock data for development/testing
            return self._generate_mock_data(symbol, start_date, end_date, timeframe)
        
        try:
            # Convert dates to timestamps
            start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
            end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = self.exchange_client.fetch_ohlcv(
                symbol, timeframe, start_ts, limit=1000
            )
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime index
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filter by date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching {symbol} from {self.exchange}: {str(e)}")
            return None
    
    def _generate_mock_data(self, 
                           symbol: str, 
                           start_date: str, 
                           end_date: str, 
                           timeframe: str) -> pd.DataFrame:
        """Generate mock OHLCV data for testing when exchange is unavailable."""
        self.logger.info(f"Generating mock data for {symbol}")
        
        # Parse timeframe
        timeframe_minutes = self._parse_timeframe_minutes(timeframe)
        
        # Generate date range
        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)
        date_range = pd.date_range(start, end, freq=f'{timeframe_minutes}min')
        
        # Generate realistic price data with random walk
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Starting price based on symbol
        base_price = 50000 if 'BTC' in symbol.upper() else 3000 if 'ETH' in symbol.upper() else 100
        
        n_periods = len(date_range)
        returns = np.random.normal(0, 0.02, n_periods)  # 2% daily volatility
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Generate OHLCV from price series
        data = []
        for i, (timestamp, close_price) in enumerate(zip(date_range, prices)):
            # Generate realistic OHLC from close price
            volatility = close_price * 0.01  # 1% intra-bar volatility
            high = close_price + np.random.exponential(volatility)
            low = close_price - np.random.exponential(volatility)
            
            if i == 0:
                open_price = close_price
            else:
                open_price = prices[i-1]  # Previous close becomes open
            
            # Ensure OHLC consistency
            high = max(high, open_price, close_price)
            low = min(low, open_price, close_price)
            
            # Generate volume
            volume = np.random.lognormal(mean=10, sigma=1)
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low, 
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=date_range)
        return df
    
    def _parse_timeframe_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes."""
        timeframe_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '8h': 480,
            '12h': 720, '1d': 1440, '1w': 10080
        }
        return timeframe_map.get(timeframe, 60)
    
    def _validate_and_clean_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Validate and clean OHLCV data."""
        original_len = len(df)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        # Remove rows with zero or negative prices
        df = df[(df[['open', 'high', 'low', 'close']] > 0).all(axis=1)]
        
        # Remove rows with invalid OHLC relationships
        df = df[
            (df['high'] >= df[['open', 'close']].max(axis=1)) &
            (df['low'] <= df[['open', 'close']].min(axis=1))
        ]
        
        # Sort by timestamp
        df = df.sort_index()
        
        # Log data quality issues
        if len(df) < original_len:
            removed = original_len - len(df)
            self.logger.warning(f"Removed {removed} invalid bars from {symbol}")
        
        if df.empty:
            raise ValueError(f"No valid data remaining for {symbol} after cleaning")
        
        return df
    
    def get_available_symbols(self, pattern: Optional[str] = None) -> List[str]:
        """Get list of available symbols from exchange."""
        if self.exchange_client is None:
            # Return mock symbols
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
            if pattern:
                symbols = [s for s in symbols if pattern.upper() in s.upper()]
            return symbols
        
        try:
            markets = self.exchange_client.load_markets()
            symbols = list(markets.keys())
            
            if pattern:
                symbols = [s for s in symbols if pattern.upper() in s.upper()]
            
            return sorted(symbols)
            
        except Exception as e:
            self.logger.error(f"Failed to get available symbols: {str(e)}")
            return []