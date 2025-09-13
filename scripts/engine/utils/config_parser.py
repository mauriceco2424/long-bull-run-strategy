"""
Configuration Parser

Parses parameter_config.md and other configuration files.
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime


class ConfigParser:
    """
    Parses trading strategy configuration files.
    
    Handles:
    - parameter_config.md parsing
    - Type conversion and validation
    - Default value handling
    - Configuration schema validation
    """
    
    def __init__(self):
        """Initialize configuration parser."""
        self.logger = logging.getLogger(__name__)
        self.config_cache = {}
        
    def parse_config(self, config_path: str = "parameter_config.md") -> Dict[str, Any]:
        """
        Parse configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Parsed configuration dictionary
        """
        # Check cache first
        if config_path in self.config_cache:
            self.logger.debug(f"Using cached config: {config_path}")
            return self.config_cache[config_path]
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            if config_path.endswith('.md'):
                config = self._parse_markdown_config(config_path)
            elif config_path.endswith('.json'):
                config = self._parse_json_config(config_path)
            else:
                raise ValueError(f"Unsupported config file format: {config_path}")
            
            # Validate and process config
            config = self._process_config(config)
            
            # Cache the result
            self.config_cache[config_path] = config
            
            self.logger.info(f"Configuration parsed successfully: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error parsing config {config_path}: {str(e)}")
            raise
    
    def _parse_markdown_config(self, file_path: str) -> Dict[str, Any]:
        """Parse parameter_config.md file."""
        config = {}
        current_section = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into sections based on ## headers
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_name = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                config[self._normalize_section_name(section_name)] = self._parse_section_content(
                    section_content, section_name
                )
        
        return config
    
    def _parse_json_config(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON configuration file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize section name to standard format."""
        name_mapping = {
            'Strategy Parameters': 'strategy_parameters',
            'Market Configuration': 'market_config',
            'Date Range': 'date_range', 
            'Risk Management': 'risk_management',
            'Execution Settings': 'execution_settings',
            'Universe': 'universe',
            'Timeframe': 'timeframe',
            'Backtest': 'backtest'
        }
        
        return name_mapping.get(section_name, section_name.lower().replace(' ', '_'))
    
    def _parse_section_content(self, content: str, section_name: str) -> Dict[str, Any]:
        """Parse content of a configuration section."""
        section_data = {}
        
        # Parse key-value pairs and YAML lists
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        current_list_key = None
        current_list = []
        
        for line in lines:
            if line.startswith('- '):
                # YAML list item
                if current_list_key:
                    item = line[2:].strip()  # Remove '- ' prefix
                    if item and item not in ['TBD', 'TODO', '[REQUIRED]']:
                        current_list.append(item)
            elif ':' in line:
                # Finish current list if any
                if current_list_key and current_list:
                    section_data[current_list_key] = current_list
                    current_list = []
                    current_list_key = None
                
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip empty values or placeholders
                if not value or value in ['TBD', 'TODO', '[REQUIRED]']:
                    # Check if this might be a list key
                    current_list_key = key
                    continue
                
                # Convert value to appropriate type
                section_data[key] = self._convert_value_type(value, key)
            
        # Handle final list if any
        if current_list_key and current_list:
            section_data[current_list_key] = current_list
        
        return section_data
    
    def _convert_value_type(self, value: str, key: str) -> Any:
        """Convert string value to appropriate Python type."""
        # If already converted, return as is
        if not isinstance(value, str):
            return value
            
        # Remove comments (everything after #)
        if '#' in value:
            value = value.split('#')[0].strip()
        
        # Remove quotes if present
        value = value.strip('\'"')
        
        # Handle boolean values
        if value.lower() in ['true', 'yes', 'on', 'enabled']:
            return True
        elif value.lower() in ['false', 'no', 'off', 'disabled']:
            return False
        
        # Handle numeric values
        try:
            # Try integer first
            if '.' not in value and 'e' not in value.lower():
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass
        
        # Handle dates
        if 'date' in key.lower() and re.match(r'\d{4}-\d{2}-\d{2}', value):
            return value  # Keep as string for now
        
        # Handle lists (comma-separated)
        if ',' in value and not any(x in value for x in ['http', 'https', '://']):
            return [item.strip() for item in value.split(',')]
        
        # Handle ranges (e.g., "10-50")
        if re.match(r'^\d+\s*-\s*\d+$', value):
            start, end = value.split('-')
            return {'min': int(start.strip()), 'max': int(end.strip())}
        
        # Return as string
        return value
    
    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate configuration."""
        processed_config = {}
        
        # Standard configuration structure
        if 'strategy_parameters' in config:
            processed_config['strategy_parameters'] = config['strategy_parameters']
        
        # Market configuration
        if 'market_config' in config:
            processed_config['universe'] = config['market_config']
        elif 'universe' in config:
            processed_config['universe'] = config['universe']
        else:
            # Extract universe info from strategy_parameters if available
            strategy_params = config.get('strategy_parameters', {})
            universe_config = {}
            
            # Extract key universe parameters
            if 'symbols' in strategy_params:
                symbols_value = strategy_params['symbols']
                if isinstance(symbols_value, str):
                    # Parse as comma-separated list
                    universe_config['symbols'] = [s.strip() for s in symbols_value.split(',')]
                else:
                    universe_config['symbols'] = symbols_value
            if 'timeframe' in strategy_params:
                universe_config['timeframe'] = self._convert_value_type(strategy_params['timeframe'], 'timeframe')
            if 'exchange' in strategy_params:
                universe_config['exchange'] = self._convert_value_type(strategy_params['exchange'], 'exchange')
            
            if universe_config:
                processed_config['universe'] = universe_config
        
        # Date range configuration
        if 'date_range' in config:
            processed_config['backtest'] = {
                'start_date': config['date_range'].get('start_date'),
                'end_date': config['date_range'].get('end_date'),
                'initial_capital': config['date_range'].get('initial_capital', 100000)
            }
        elif 'backtest' in config:
            processed_config['backtest'] = config['backtest']
        else:
            # Extract backtest info from strategy_parameters if available
            strategy_params = config.get('strategy_parameters', {})
            backtest_config = {}
            
            # Extract key backtest parameters
            if 'start_date' in strategy_params:
                backtest_config['start_date'] = self._convert_value_type(strategy_params['start_date'], 'start_date')
            if 'end_date' in strategy_params:
                backtest_config['end_date'] = self._convert_value_type(strategy_params['end_date'], 'end_date')
            if 'initial_capital' in strategy_params:
                backtest_config['initial_capital'] = self._convert_value_type(strategy_params['initial_capital'], 'initial_capital')
            
            # Set defaults if not found
            if not backtest_config.get('initial_capital'):
                backtest_config['initial_capital'] = 100000
            
            if backtest_config:
                processed_config['backtest'] = backtest_config
        
        # Risk management
        if 'risk_management' in config:
            processed_config['risk_management'] = config['risk_management']
        
        # Execution settings
        if 'execution_settings' in config:
            processed_config['execution'] = config['execution_settings']
        elif 'execution' in config:
            processed_config['execution'] = config['execution']
        
        # Timeframe - extract from various locations
        if 'timeframe' in config:
            processed_config['timeframe'] = config['timeframe']
        elif 'universe' in processed_config and 'timeframe' in processed_config['universe']:
            processed_config['timeframe'] = processed_config['universe']['timeframe']
        else:
            # Extract from strategy_parameters
            strategy_params = config.get('strategy_parameters', {})
            if 'timeframe' in strategy_params:
                processed_config['timeframe'] = self._convert_value_type(strategy_params['timeframe'], 'timeframe')
        
        # Add any other sections
        for key, value in config.items():
            if key not in processed_config:
                processed_config[key] = value
        
        return processed_config
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration completeness and correctness.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required sections
        required_sections = ['strategy_parameters', 'universe', 'backtest']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate backtest configuration
        if 'backtest' in config:
            backtest = config['backtest']
            
            if 'start_date' not in backtest:
                errors.append("Missing start_date in backtest configuration")
            elif not re.match(r'\d{4}-\d{2}-\d{2}', str(backtest['start_date'])):
                errors.append("Invalid start_date format (expected YYYY-MM-DD)")
            
            if 'end_date' not in backtest:
                errors.append("Missing end_date in backtest configuration")
            elif not re.match(r'\d{4}-\d{2}-\d{2}', str(backtest['end_date'])):
                errors.append("Invalid end_date format (expected YYYY-MM-DD)")
            
            if 'initial_capital' not in backtest:
                errors.append("Missing initial_capital in backtest configuration")
            elif not isinstance(backtest['initial_capital'], (int, float)) or backtest['initial_capital'] <= 0:
                errors.append("initial_capital must be a positive number")
        
        # Validate universe configuration
        if 'universe' in config:
            universe = config['universe']
            if isinstance(universe, dict):
                if 'exchange' not in universe:
                    errors.append("Missing exchange in universe configuration")
                if 'symbols' not in universe and 'quote_currency' not in universe:
                    errors.append("Missing symbols or quote_currency in universe configuration")
        
        # Validate strategy parameters
        if 'strategy_parameters' in config:
            if not isinstance(config['strategy_parameters'], dict):
                errors.append("strategy_parameters must be a dictionary")
        
        return errors
    
    def get_config_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration summary for logging."""
        summary = {
            'sections': list(config.keys()),
            'strategy_parameters_count': len(config.get('strategy_parameters', {})),
            'has_risk_management': 'risk_management' in config,
            'has_execution_settings': 'execution' in config,
        }
        
        if 'backtest' in config:
            backtest = config['backtest']
            summary['backtest_period'] = f"{backtest.get('start_date')} to {backtest.get('end_date')}"
            summary['initial_capital'] = backtest.get('initial_capital')
        
        if 'universe' in config:
            universe = config['universe']
            if isinstance(universe, dict):
                summary['exchange'] = universe.get('exchange')
                summary['symbols_count'] = len(universe.get('symbols', []))
        
        return summary
    
    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self.config_cache.clear()
        self.logger.debug("Configuration cache cleared")