#!/usr/bin/env python3
"""
Parameter Configuration Auto-Generation System

This script reads the strategy template (STRAT_TEMPLATE.md) and automatically generates
a parameter_config.md template with all required parameters for the user to fill in.

Usage:
    python tools/generate_parameter_config.py [--template-path STRAT_TEMPLATE.md] [--output parameter_config.md]
"""

import re
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import json


class ParameterExtractor:
    """Extracts parameter schema from strategy template."""
    
    def __init__(self):
        self.parameters = {}
        self.market_config = {}
        self.template_metadata = {}
    
    def extract_from_template(self, template_path: str) -> Dict[str, Any]:
        """Extract all parameters from strategy template."""
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract strategy metadata
        self.template_metadata = self._extract_metadata(content)
        
        # Extract parameters from different sections
        self._extract_entry_parameters(content)
        self._extract_exit_parameters(content)
        self._extract_portfolio_parameters(content)
        self._extract_filter_parameters(content)
        self._extract_market_universe(content)
        
        return {
            'metadata': self.template_metadata,
            'parameters': self.parameters,
            'market_config': self.market_config
        }
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract strategy name and description."""
        metadata = {}
        
        # Extract strategy name from title
        title_match = re.search(r'^#\s*(.+?)(?:\n|$)', content, re.MULTILINE)
        if title_match:
            metadata['strategy_name'] = title_match.group(1).strip()
        
        # Extract narrative description if present
        narrative_match = re.search(
            r'## 1a\) Strategy Description \(Narrative\)(.*?)(?=##|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        if narrative_match:
            metadata['description'] = narrative_match.group(1).strip()
        
        return metadata
    
    def _extract_entry_parameters(self, content: str):
        """Extract entry logic parameters."""
        entry_section = re.search(
            r'## 2\) Entry Logic.*?(?=##)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if entry_section:
            section_text = entry_section.group(0)
            
            # Extract parameters line
            params_match = re.search(
                r'\*\*Parameters\*\*:\s*`([^`]+)`', 
                section_text, 
                re.IGNORECASE
            )
            
            if params_match:
                params_text = params_match.group(1)
                self._parse_parameter_definitions(params_text, 'entry')
    
    def _extract_exit_parameters(self, content: str):
        """Extract exit logic parameters."""
        exit_section = re.search(
            r'## 3\) Exit Logic.*?(?=##)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if exit_section:
            section_text = exit_section.group(0)
            
            # Extract parameters line
            params_match = re.search(
                r'\*\*Parameters\*\*:\s*`([^`]+)`', 
                section_text, 
                re.IGNORECASE
            )
            
            if params_match:
                params_text = params_match.group(1)
                self._parse_parameter_definitions(params_text, 'exit')
    
    def _extract_portfolio_parameters(self, content: str):
        """Extract portfolio and risk management parameters."""
        portfolio_section = re.search(
            r'## 4\) Portfolio & Risk Management.*?(?=##)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if portfolio_section:
            section_text = portfolio_section.group(0)
            
            # Extract accounting mode
            accounting_match = re.search(
                r'### 4\.1 Portfolio Accounting Mode.*?(\d+)\.\s*\*\*([^*]+)\*\*',
                section_text,
                re.DOTALL
            )
            
            if accounting_match:
                self.parameters['accounting_mode'] = {
                    'type': 'choice',
                    'description': 'Portfolio accounting method',
                    'choices': ['cash-only', 'mark-to-market', 'frozen-notional'],
                    'category': 'portfolio'
                }
            
            # Extract position sizing
            sizing_match = re.search(
                r'### 4\.2 Position Sizing Strategy.*?(\d+)\.\s*\*\*([^*]+)\*\*',
                section_text,
                re.DOTALL
            )
            
            if sizing_match:
                self.parameters['position_sizing_strategy'] = {
                    'type': 'choice',
                    'description': 'Position sizing method',
                    'choices': ['fixed-percent', 'fixed-notional', 'volatility-adjusted'],
                    'category': 'portfolio'
                }
    
    def _extract_filter_parameters(self, content: str):
        """Extract filter and eligibility parameters."""
        filter_section = re.search(
            r'## 5\) Filters & Eligibility.*?(?=##)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if filter_section:
            section_text = filter_section.group(0)
            
            # Extract run boundaries (dates)
            boundaries_match = re.search(
                r'\*\*Run Boundaries\*\*:\s*`([^`]+)`',
                section_text,
                re.IGNORECASE
            )
            
            if boundaries_match:
                self.parameters['start_date'] = {
                    'type': 'date',
                    'description': 'Backtest start date',
                    'example': '2021-01-01',
                    'category': 'dates'
                }
                self.parameters['end_date'] = {
                    'type': 'date', 
                    'description': 'Backtest end date',
                    'example': '2023-12-31',
                    'category': 'dates'
                }
    
    def _extract_market_universe(self, content: str):
        """Extract market and universe configuration."""
        # Look for Market/Universe definition
        market_match = re.search(
            r'(?:\*\*Market/Universe\*\*|\*\*Universe\*\*):\s*`([^`]+)`',
            content,
            re.IGNORECASE
        )
        
        if market_match:
            self.market_config['universe'] = market_match.group(1).strip()
        
        # Look for timeframe
        timeframe_match = re.search(
            r'\*\*Timeframe\*\*:\s*`([^`]+)`',
            content,
            re.IGNORECASE
        )
        
        if timeframe_match:
            self.market_config['timeframe'] = timeframe_match.group(1).strip()
    
    def _parse_parameter_definitions(self, params_text: str, category: str):
        """Parse parameter definitions from parameter text."""
        
        # Common parameter patterns
        patterns = [
            # RSI(14) -> rsi_period: 14
            (r'(\w+)\((\d+)\)', r'\\1_period', 'integer'),
            # SMA(20) -> sma_period: 20  
            (r'SMA\((\d+)\)', 'sma_period', 'integer'),
            # ATR(10) -> atr_period: 10
            (r'ATR\((\d+)\)', 'atr_period', 'integer'),
            # threshold values
            (r'threshold[s]?[:\s]+([0-9.]+)', 'threshold', 'float'),
            # percentage values
            (r'([0-9.]+)%', 'percentage_value', 'float'),
        ]
        
        for pattern, param_name, param_type in patterns:
            matches = re.finditer(pattern, params_text, re.IGNORECASE)
            for match in matches:
                if isinstance(param_name, str):
                    name = param_name
                else:
                    name = match.expand(param_name) + '_period'
                
                self.parameters[name] = {
                    'type': param_type,
                    'description': f'{category.title()} parameter from strategy template',
                    'example': match.group(1) if match.lastindex >= 1 else match.group(0),
                    'category': category
                }


class ParameterConfigGenerator:
    """Generates parameter_config.md from extracted parameters."""
    
    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.metadata = extracted_data.get('metadata', {})
        self.parameters = extracted_data.get('parameters', {})
        self.market_config = extracted_data.get('market_config', {})
    
    def generate_config(self, output_path: str):
        """Generate the parameter configuration file."""
        
        config_content = self._build_config_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"Generated parameter configuration: {output_path}")
        return output_path
    
    def _build_config_content(self) -> str:
        """Build the complete configuration file content."""
        
        lines = []
        
        # Header
        lines.extend(self._build_header())
        
        # Market Configuration
        lines.extend(self._build_market_section())
        
        # Date Range
        lines.extend(self._build_date_section())
        
        # Strategy Parameters by category
        categories = self._group_parameters_by_category()
        
        for category, params in categories.items():
            lines.extend(self._build_parameter_section(category, params))
        
        # Footer
        lines.extend(self._build_footer())
        
        return '\n'.join(lines)
    
    def _build_header(self) -> List[str]:
        """Build configuration file header."""
        strategy_name = self.metadata.get('strategy_name', 'Trading Strategy')
        
        return [
            f"# {strategy_name} - Parameter Configuration",
            "",
            "<!-- Auto-generated parameter configuration template -->",
            f"<!-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->",
            "",
            "## Instructions",
            "Fill in all required parameters below. Remove the [REQUIRED] markers when you provide values.",
            "All parameters must have values before running `/run` command.",
            "",
            "---",
            ""
        ]
    
    def _build_market_section(self) -> List[str]:
        """Build market configuration section."""
        universe = self.market_config.get('universe', '[REQUIRED: e.g., binance_usdt, crypto_majors]')
        timeframe = self.market_config.get('timeframe', '[REQUIRED: e.g., 1h, 4h, 1d]')
        
        return [
            "## Market Configuration",
            f"universe: {universe}",
            f"timeframe: {timeframe}",
            ""
        ]
    
    def _build_date_section(self) -> List[str]:
        """Build date range section."""
        
        return [
            "## Date Range",
            "start_date: [REQUIRED: YYYY-MM-DD, e.g., 2021-01-01]",
            "end_date: [REQUIRED: YYYY-MM-DD, e.g., 2023-12-31]",
            ""
        ]
    
    def _group_parameters_by_category(self) -> Dict[str, Dict[str, Any]]:
        """Group parameters by category."""
        categories = {}
        
        for param_name, param_info in self.parameters.items():
            category = param_info.get('category', 'strategy').title()
            
            if category not in categories:
                categories[category] = {}
            
            categories[category][param_name] = param_info
        
        return categories
    
    def _build_parameter_section(self, category: str, params: Dict[str, Any]) -> List[str]:
        """Build parameter section for a category."""
        
        lines = [f"## {category} Parameters"]
        
        for param_name, param_info in params.items():
            param_type = param_info.get('type', 'string')
            description = param_info.get('description', 'Parameter from strategy template')
            example = param_info.get('example', 'value')
            
            if param_type == 'choice':
                choices = param_info.get('choices', [])
                choices_str = ', '.join(choices)
                lines.append(f"{param_name}: [REQUIRED: choose from {choices_str}] # {description}")
            else:
                lines.append(f"{param_name}: [REQUIRED: {param_type}, e.g., {example}] # {description}")
        
        lines.append("")
        return lines
    
    def _build_footer(self) -> List[str]:
        """Build configuration file footer."""
        
        return [
            "---",
            "",
            "## Validation",
            "Before running, ensure:",
            "- [ ] All [REQUIRED] parameters have values",
            "- [ ] Date range is valid (start_date < end_date)",  
            "- [ ] Universe and timeframe are available in data sources",
            "- [ ] Parameter values are within valid ranges",
            "",
            "## Usage",
            "Once completed, run: `/run`",
            "The system will validate this configuration and execute the backtest.",
        ]


def main():
    """Main entry point for parameter config generation."""
    
    parser = argparse.ArgumentParser(description='Generate parameter configuration from strategy template')
    parser.add_argument(
        '--template-path',
        default='docs/STRAT_TEMPLATE.md',
        help='Path to strategy template file (default: docs/STRAT_TEMPLATE.md)'
    )
    parser.add_argument(
        '--output',
        default='parameter_config.md', 
        help='Output path for parameter configuration (default: parameter_config.md)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate template, do not generate config'
    )
    
    args = parser.parse_args()
    
    # Check if template exists
    if not Path(args.template_path).exists():
        print(f"Error: Strategy template not found: {args.template_path}")
        sys.exit(1)
    
    try:
        # Extract parameters from template
        extractor = ParameterExtractor()
        extracted_data = extractor.extract_from_template(args.template_path)
        
        print(f"Extracted {len(extracted_data['parameters'])} parameters from template")
        
        if args.validate_only:
            print("Template validation completed successfully")
            return
        
        # Generate configuration file
        generator = ParameterConfigGenerator(extracted_data)
        generator.generate_config(args.output)
        
        print(f"\nParameter configuration generated successfully!")
        print(f"Next steps:")
        print(f"1. Edit {args.output} and fill in all [REQUIRED] parameters")
        print(f"2. Run: /run")
        
    except Exception as e:
        print(f"Error generating parameter configuration: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()