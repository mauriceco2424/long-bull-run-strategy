#!/usr/bin/env python3
"""
Trading Strategy Specification Validator

Validates that a strategy specification (SMR.md) meets all STRAT_TEMPLATE.md requirements.
Ensures the strategy is ready for engine building.

Usage: python validate_strategy.py [--test]
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'  
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ValidationResult:
    def __init__(self, passed: bool, message: str, details: str = "", section: str = ""):
        self.passed = passed
        self.message = message
        self.details = details
        self.section = section


class ComplexityAssessor:
    """Assesses strategy complexity based on multiple factors"""
    
    def __init__(self):
        self.scores = {}
        self.total_score = 0
        self.complexity_level = "SIMPLE"
        self.time_targets = {}
        
    def assess_technical_indicators(self, content: str) -> int:
        """Score technical indicators complexity (0-3 points)"""
        # Extract entry and exit logic sections
        entry_match = re.search(r'## 2\) Entry Logic(.*?)(?=##|$)', content, re.DOTALL)
        exit_match = re.search(r'## 3\) Exit Logic(.*?)(?=##|$)', content, re.DOTALL)
        
        indicators = []
        if entry_match:
            entry_text = entry_match.group(1)
            # Look for common indicators
            if re.search(r'RSI', entry_text, re.IGNORECASE):
                indicators.append('RSI')
            if re.search(r'SMA|MA|Moving Average', entry_text, re.IGNORECASE):
                indicators.append('MA')
            if re.search(r'EMA|Exponential', entry_text, re.IGNORECASE):
                indicators.append('EMA')
            if re.search(r'MACD', entry_text, re.IGNORECASE):
                indicators.append('MACD')
            if re.search(r'Bollinger|BB', entry_text, re.IGNORECASE):
                indicators.append('BB')
            if re.search(r'Stochastic', entry_text, re.IGNORECASE):
                indicators.append('Stochastic')
                
        if exit_match:
            exit_text = exit_match.group(1)
            # Check exit for additional indicators not in entry
            if 'RSI' not in indicators and re.search(r'RSI', exit_text, re.IGNORECASE):
                indicators.append('RSI')
                
        # Score based on indicator count
        if len(indicators) == 0:
            return 0  # No indicators
        elif len(indicators) == 1:
            return 1  # Single indicator
        elif len(indicators) <= 3:
            return 2  # Multiple indicators
        else:
            return 3  # Complex multi-indicator
            
    def assess_entry_logic(self, content: str) -> int:
        """Score entry logic complexity (0-3 points)"""
        entry_match = re.search(r'\*\*Mechanic / Condition\*\*:\s*`([^`]+)`', content)
        if not entry_match:
            return 0
            
        condition = entry_match.group(1)
        
        # Count logical operators
        and_count = len(re.findall(r'\bAND\b|\&\&', condition, re.IGNORECASE))
        or_count = len(re.findall(r'\bOR\b|\|\|', condition, re.IGNORECASE))
        
        # Check for nested conditions or functions
        has_nested = '(' in condition and ')' in condition
        
        # Score based on complexity
        if and_count == 0 and or_count == 0:
            return 0  # Single condition
        elif and_count + or_count == 1 and not has_nested:
            return 1  # Two conditions with single operator
        elif and_count + or_count <= 2:
            return 2  # Multiple conditions
        else:
            return 3  # Complex multi-condition logic
            
    def assess_exit_logic(self, content: str) -> int:
        """Score exit logic complexity (0-3 points)"""
        # Find exit section
        exit_match = re.search(r'## 3\) Exit Logic(.*?)(?=##|$)', content, re.DOTALL)
        if not exit_match:
            return 0
            
        exit_section = exit_match.group(1)
        
        # Look for exit condition
        condition_match = re.search(r'\*\*Mechanic / Condition\*\*:\s*`([^`]+)`', exit_section)
        if not condition_match:
            return 0
            
        condition = condition_match.group(1)
        
        # Count different exit types
        exit_types = 0
        if re.search(r'stop.?loss|SL', condition, re.IGNORECASE):
            exit_types += 1
        if re.search(r'take.?profit|TP|target', condition, re.IGNORECASE):
            exit_types += 1
        if re.search(r'trail|dynamic', condition, re.IGNORECASE):
            exit_types += 1
        if re.search(r'time.?based|days?|hours?|bars?', condition, re.IGNORECASE):
            exit_types += 1
        if re.search(r'RSI|MA|indicator', condition, re.IGNORECASE):
            exit_types += 1
            
        # Also count logical operators
        or_count = len(re.findall(r'\bOR\b|\|\|', condition, re.IGNORECASE))
        
        # Score based on complexity
        if exit_types == 0:
            return 0
        elif exit_types == 1 and or_count == 0:
            return 0  # Single exit type
        elif exit_types <= 2 or or_count == 1:
            return 1  # Two exit types or conditions
        elif exit_types == 3:
            return 2  # Multiple exit types
        else:
            return 3  # Complex multi-exit logic
            
    def assess_parameters(self, content: str) -> int:
        """Score parameter complexity (0-3 points)"""
        # Find parameters section
        params_match = re.search(r'## 7\) Implementation Requirements(.*?)(?=##|$)', content, re.DOTALL)
        if not params_match:
            return 0
            
        params_section = params_match.group(1)
        
        # Count parameter definitions
        param_matches = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*', params_section)
        param_count = len(param_matches)
        
        # Score based on parameter count
        if param_count <= 2:
            return 0  # Very few parameters
        elif param_count <= 5:
            return 1  # Moderate parameters
        elif param_count <= 10:
            return 2  # Many parameters
        else:
            return 3  # Complex parameterization
            
    def assess_portfolio_management(self, content: str) -> int:
        """Score portfolio management complexity (0-3 points)"""
        # Find position management section
        pos_match = re.search(r'## 4\) Position Management(.*?)(?=## 5\)|$)', content, re.DOTALL)
        if not pos_match:
            return 0
            
        position = pos_match.group(1)
        
        # Check sizing strategy
        if re.search(r'Fixed % of Equity.*?→', position):
            base_score = 0  # Simple fixed %
        elif re.search(r'Fixed Dollar Amount.*?→', position):
            base_score = 0  # Simple fixed $
        elif re.search(r'Risk-Based Sizing.*?→', position):
            base_score = 2  # Risk-based is complex
        elif re.search(r'Custom Sizing Logic.*?→', position):
            base_score = 3  # Custom is most complex
        else:
            base_score = 0
            
        # Check for additional complexity
        if re.search(r'pyramid|scale|add to position', position, re.IGNORECASE):
            base_score = min(3, base_score + 1)
        if re.search(r'rebalance|weight|allocation', position, re.IGNORECASE):
            base_score = min(3, base_score + 1)
            
        return base_score
        
    def assess_market_scope(self, content: str) -> int:
        """Score market scope complexity (0-3 points)"""
        # Look for universe definition
        universe_indicators = [
            r'universe|symbols?|assets?|pairs?|tickers?',
            r'BTC|ETH|USD|EUR',  # Currency pairs
            r'screening|filter|scan',  # Dynamic universe
            r'sector|industry|market.?cap'  # Broad universe
        ]
        
        mentions = 0
        for pattern in universe_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                mentions += 1
                
        # Check for specific symbol lists
        symbol_list_match = re.findall(r'["\'`]\s*([A-Z]{3,}[/-][A-Z]{3,})\s*["\'`]', content)
        symbol_count = len(set(symbol_list_match))
        
        # Score based on scope
        if symbol_count > 0:
            if symbol_count < 5:
                return 0  # Few symbols
            elif symbol_count < 20:
                return 1  # Moderate universe
            else:
                return 2  # Large universe
        elif mentions >= 3:
            return 2  # Likely broad universe
        else:
            return 0  # Minimal scope
            
    def calculate_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate overall complexity score and level"""
        # Assess each dimension
        self.scores['technical_indicators'] = self.assess_technical_indicators(content)
        self.scores['entry_logic'] = self.assess_entry_logic(content)
        self.scores['exit_logic'] = self.assess_exit_logic(content)
        self.scores['parameters'] = self.assess_parameters(content)
        self.scores['portfolio_management'] = self.assess_portfolio_management(content)
        self.scores['market_scope'] = self.assess_market_scope(content)
        
        # Calculate total score
        self.total_score = sum(self.scores.values())
        
        # Determine complexity level and time targets
        if self.total_score <= 5:
            self.complexity_level = "SIMPLE"
            self.time_targets = {
                'planning': '60 seconds',
                'building': '90 seconds',
                'total': '2.5 minutes'
            }
        elif self.total_score <= 10:
            self.complexity_level = "MODERATE"
            self.time_targets = {
                'planning': '2-3 minutes',
                'building': '3-5 minutes',
                'total': '5-8 minutes'
            }
        elif self.total_score <= 15:
            self.complexity_level = "COMPLEX"
            self.time_targets = {
                'planning': '5-10 minutes',
                'building': '10-20 minutes',
                'total': '15-30 minutes'
            }
        else:
            self.complexity_level = "ADVANCED"
            self.time_targets = {
                'planning': '15+ minutes',
                'building': '30+ minutes',
                'total': '45-60 minutes'
            }
            
        return {
            'scores': self.scores,
            'total_score': self.total_score,
            'complexity_level': self.complexity_level,
            'time_targets': self.time_targets
        }


class StrategyValidator:
    """Validates trading strategy specification documents"""
    
    def __init__(self, test_mode: bool = False):
        self.root_dir = Path.cwd()
        self.test_mode = test_mode
        self.results: List[ValidationResult] = []
        self.timing_data: Dict[str, float] = {}
        self.start_time = time.time()
        
        # Determine which SMR to validate
        if test_mode:
            self.smr_path = self.root_dir / 'docs' / 'test' / 'test_SMR.md'
            self.strategy_name = "Test Strategy (RSI Mean Reversion)"
        else:
            self.smr_path = self.root_dir / 'docs' / 'SMR.md'
            self.strategy_name = "Main Strategy"
            
    def log(self, message: str, color: str = Colors.BLUE):
        """Print colored log message with timing"""
        elapsed = time.time() - self.start_time
        print(f"{color}[{elapsed:.2f}s] {message}{Colors.END}")
        
    def success(self, message: str):
        """Print success message"""
        elapsed = time.time() - self.start_time
        print(f"{Colors.GREEN}[{elapsed:.2f}s] [PASS] {message}{Colors.END}")
        
    def error(self, message: str):
        """Print error message"""  
        elapsed = time.time() - self.start_time
        print(f"{Colors.RED}[{elapsed:.2f}s] [FAIL] {message}{Colors.END}")
        
    def warning(self, message: str):
        """Print warning message"""
        elapsed = time.time() - self.start_time
        print(f"{Colors.YELLOW}[{elapsed:.2f}s] [WARN] {message}{Colors.END}")
        
    def track_timing(self, operation: str, duration: float):
        """Track timing for performance analysis"""
        self.timing_data[operation] = duration
        
    def load_strategy_spec(self) -> Tuple[bool, str]:
        """Load and parse the strategy specification"""
        start = time.time()
        self.log(f"Loading strategy specification from {self.smr_path.name}...")
        
        if not self.smr_path.exists():
            self.track_timing("load_spec", time.time() - start)
            return False, f"Strategy specification not found at {self.smr_path}"
            
        try:
            with open(self.smr_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.track_timing("load_spec", time.time() - start)
            return True, content
        except Exception as e:
            self.track_timing("load_spec", time.time() - start)
            return False, f"Failed to read strategy specification: {str(e)}"
            
    def validate_section_presence(self, content: str) -> ValidationResult:
        """Validate all required sections are present"""
        start = time.time()
        self.log("Validating section presence...")
        
        required_sections = [
            ("## 1) Strategy Overview", "Strategy Overview"),
            ("## 1a) Strategy Description", "Strategy Description"),
            ("## 2) Entry Logic", "Entry Logic"),
            ("## 3) Exit Logic", "Exit Logic"),
            ("## 4) Position Management", "Position Management"),
            ("### 4.1 Portfolio Accounting Mode", "Portfolio Accounting Mode"),
            ("### 4.2 Position Sizing Strategy", "Position Sizing Strategy"),
            ("## 5) Filters & Eligibility", "Filters & Eligibility"),
            ("## 6) Conflict Handling", "Conflict Handling"),
            ("## Checklist", "Checklist")
        ]
        
        missing_sections = []
        for section_header, section_name in required_sections:
            if section_header not in content:
                missing_sections.append(section_name)
                
        self.track_timing("section_presence", time.time() - start)
        
        if missing_sections:
            return ValidationResult(
                False,
                f"Missing required sections: {', '.join(missing_sections)}",
                "All sections from STRAT_TEMPLATE.md must be present",
                "Structure"
            )
            
        return ValidationResult(True, "All required sections present", "", "Structure")
        
    def validate_overview_section(self, content: str) -> ValidationResult:
        """Validate Strategy Overview section completeness"""
        start = time.time()
        self.log("Validating Strategy Overview section...")
        
        # Extract overview section
        overview_match = re.search(r'## 1\) Strategy Overview(.*?)(?=##|$)', content, re.DOTALL)
        if not overview_match:
            self.track_timing("overview", time.time() - start)
            return ValidationResult(False, "Strategy Overview section not found", "", "Overview")
            
        overview = overview_match.group(1)
        
        # Check required fields
        required_fields = [
            (r'\*\*Name\*\*:\s*`([^`]+)`', "Name"),
            (r'\*\*Market/Universe\*\*:\s*`([^`]+)`', "Market/Universe"),
            (r'\*\*Asset Selection\*\*:\s*`([^`]+)`', "Asset Selection"),
            (r'\*\*Timeframe\*\*:\s*`([^`]+)`', "Timeframe"),
            (r'\*\*Scope\*\*:\s*`([^`]+)`', "Scope")
        ]
        
        missing_fields = []
        empty_fields = []
        
        for pattern, field_name in required_fields:
            match = re.search(pattern, overview)
            if not match:
                missing_fields.append(field_name)
            elif match.group(1).strip() in ['', 'TBD', 'TODO', '...']:
                empty_fields.append(field_name)
                
        self.track_timing("overview", time.time() - start)
        
        if missing_fields:
            return ValidationResult(
                False,
                f"Missing overview fields: {', '.join(missing_fields)}",
                "All overview fields must be specified",
                "Overview"
            )
            
        if empty_fields:
            return ValidationResult(
                False,
                f"Empty or placeholder overview fields: {', '.join(empty_fields)}",
                "All fields must have actual values, not placeholders",
                "Overview"
            )
            
        return ValidationResult(True, "Strategy Overview section complete", "", "Overview")
        
    def validate_narrative_description(self, content: str) -> ValidationResult:
        """Validate Strategy Description narrative"""
        start = time.time()
        self.log("Validating Strategy Description narrative...")
        
        # Extract description section
        desc_match = re.search(r'## 1a\) Strategy Description.*?\n(.*?)(?=##|---)', content, re.DOTALL)
        if not desc_match:
            self.track_timing("narrative", time.time() - start)
            return ValidationResult(False, "Strategy Description section not found", "", "Narrative")
            
        description = desc_match.group(1).strip()
        
        # Check for placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', 'INSERT', '...']
        has_placeholder = any(p in description.upper() for p in placeholders)
        
        if has_placeholder:
            self.track_timing("narrative", time.time() - start)
            return ValidationResult(
                False,
                "Strategy Description contains placeholder text",
                "Must provide complete narrative description",
                "Narrative"
            )
            
        # Check minimum length (at least 100 characters for meaningful description)
        if len(description) < 100:
            self.track_timing("narrative", time.time() - start)
            return ValidationResult(
                False,
                f"Strategy Description too short ({len(description)} chars)",
                "Must provide detailed narrative (minimum 100 characters)",
                "Narrative"
            )
            
        self.track_timing("narrative", time.time() - start)
        return ValidationResult(True, "Strategy Description narrative complete", "", "Narrative")
        
    def validate_entry_logic(self, content: str) -> ValidationResult:
        """Validate Entry Logic section"""
        start = time.time()
        self.log("Validating Entry Logic section...")
        
        # Extract entry logic section
        entry_match = re.search(r'## 2\) Entry Logic(.*?)(?=##|$)', content, re.DOTALL)
        if not entry_match:
            self.track_timing("entry_logic", time.time() - start)
            return ValidationResult(False, "Entry Logic section not found", "", "Entry")
            
        entry = entry_match.group(1)
        
        # Check required fields
        required_patterns = [
            (r'\*\*Information / Markers Used\*\*:\s*`([^`]+)`', "Information/Markers"),
            (r'\*\*Parameters\*\*:\s*`([^`]+)`', "Parameters"),
            (r'\*\*Mechanic / Condition\*\*:\s*`([^`]+)`', "Mechanic/Condition"),
            (r'\*\*Trigger Evaluation Time\*\*:\s*`([^`]+)`', "Trigger Time"),
            (r'\*\*Execution Rule\*\*:\s*`([^`]+)`', "Execution Rule")
        ]
        
        missing_fields = []
        empty_fields = []
        
        for pattern, field_name in required_patterns:
            match = re.search(pattern, entry)
            if not match:
                missing_fields.append(field_name)
            elif match.group(1).strip() in ['', 'TBD', 'TODO', '...']:
                empty_fields.append(field_name)
                
        self.track_timing("entry_logic", time.time() - start)
        
        if missing_fields:
            return ValidationResult(
                False,
                f"Missing entry logic fields: {', '.join(missing_fields)}",
                "All entry logic fields must be specified",
                "Entry"
            )
            
        if empty_fields:
            return ValidationResult(
                False,
                f"Empty entry logic fields: {', '.join(empty_fields)}",
                "All fields must have actual values",
                "Entry"
            )
            
        return ValidationResult(True, "Entry Logic section complete", "", "Entry")
        
    def validate_exit_logic(self, content: str) -> ValidationResult:
        """Validate Exit Logic section"""
        start = time.time()
        self.log("Validating Exit Logic section...")
        
        # Extract exit logic section
        exit_match = re.search(r'## 3\) Exit Logic(.*?)(?=##|$)', content, re.DOTALL)
        if not exit_match:
            self.track_timing("exit_logic", time.time() - start)
            return ValidationResult(False, "Exit Logic section not found", "", "Exit")
            
        exit_section = exit_match.group(1)
        
        # Check required fields
        required_patterns = [
            (r'\*\*Information / Markers Used\*\*:\s*`([^`]+)`', "Information/Markers"),
            (r'\*\*Parameters\*\*:\s*`([^`]+)`', "Parameters"),
            (r'\*\*Mechanic / Condition\*\*:\s*`([^`]+)`', "Mechanic/Condition"),
            (r'\*\*Collision Handling\*\*:\s*`([^`]+)`', "Collision Handling"),
            (r'\*\*Execution Rule\*\*:\s*`([^`]+)`', "Execution Rule")
        ]
        
        missing_fields = []
        empty_fields = []
        
        for pattern, field_name in required_patterns:
            match = re.search(pattern, exit_section)
            if not match:
                missing_fields.append(field_name)
            elif match.group(1).strip() in ['', 'TBD', 'TODO', '...']:
                empty_fields.append(field_name)
                
        self.track_timing("exit_logic", time.time() - start)
        
        if missing_fields:
            return ValidationResult(
                False,
                f"Missing exit logic fields: {', '.join(missing_fields)}",
                "All exit logic fields must be specified",
                "Exit"
            )
            
        if empty_fields:
            return ValidationResult(
                False,
                f"Empty exit logic fields: {', '.join(empty_fields)}",
                "All fields must have actual values",
                "Exit"
            )
            
        return ValidationResult(True, "Exit Logic section complete", "", "Exit")
        
    def validate_position_management(self, content: str) -> ValidationResult:
        """Validate Position Management section"""
        start = time.time()
        self.log("Validating Position Management section...")
        
        # Extract position management section
        pos_match = re.search(r'## 4\) Position Management(.*?)(?=## 5\)|$)', content, re.DOTALL)
        if not pos_match:
            self.track_timing("position_mgmt", time.time() - start)
            return ValidationResult(False, "Position Management section not found", "", "Position")
            
        position = pos_match.group(1)
        
        # Check accounting mode selection (one option should be marked)
        accounting_modes = [
            r'1\.\s*\*\*PnL Only\*\*',
            r'2\.\s*\*\*Mark-to-market\*\*'
        ]
        
        accounting_selected = any(re.search(mode, position) for mode in accounting_modes)
        
        if not accounting_selected:
            self.track_timing("position_mgmt", time.time() - start)
            return ValidationResult(
                False,
                "No Portfolio Accounting Mode selected",
                "Must choose either PnL Only or Mark-to-market",
                "Position"
            )
            
        # Check sizing strategy selection
        sizing_strategies = [
            r'1\.\s*\*\*Fixed % of Equity\*\*',
            r'2\.\s*\*\*Fixed Dollar Amount\*\*',
            r'3\.\s*\*\*Risk-Based Sizing\*\*',
            r'4\.\s*\*\*Custom Sizing Logic\*\*'
        ]
        
        sizing_selected = any(re.search(strat, position) for strat in sizing_strategies)
        
        if not sizing_selected:
            self.track_timing("position_mgmt", time.time() - start)
            return ValidationResult(
                False,
                "No Position Sizing Strategy selected",
                "Must choose a sizing strategy",
                "Position"
            )
            
        # Check for position size specification
        if not re.search(r'\*\*Position Size\*\*:\s*`([^`]+)`', position):
            self.track_timing("position_mgmt", time.time() - start)
            return ValidationResult(
                False,
                "Position Size not specified",
                "Must specify position size parameters",
                "Position"
            )
            
        self.track_timing("position_mgmt", time.time() - start)
        return ValidationResult(True, "Position Management section complete", "", "Position")
        
    def validate_filters(self, content: str) -> ValidationResult:
        """Validate Filters & Eligibility section"""
        start = time.time()
        self.log("Validating Filters & Eligibility section...")
        
        # Extract filters section
        filters_match = re.search(r'## 5\) Filters & Eligibility(.*?)(?=##|$)', content, re.DOTALL)
        if not filters_match:
            self.track_timing("filters", time.time() - start)
            return ValidationResult(False, "Filters & Eligibility section not found", "", "Filters")
            
        filters = filters_match.group(1)
        
        # Check required fields
        required_patterns = [
            (r'\*\*Data Requirements\*\*:\s*`([^`]+)`', "Data Requirements"),
            (r'\*\*Tradability Filters\*\*:\s*`([^`]+)`', "Tradability Filters"),
            (r'\*\*Run Boundaries\*\*:\s*`([^`]+)`', "Run Boundaries")
        ]
        
        missing_fields = []
        empty_fields = []
        
        for pattern, field_name in required_patterns:
            match = re.search(pattern, filters)
            if not match:
                missing_fields.append(field_name)
            elif match.group(1).strip() in ['', 'TBD', 'TODO', '...']:
                empty_fields.append(field_name)
                
        self.track_timing("filters", time.time() - start)
        
        if missing_fields:
            return ValidationResult(
                False,
                f"Missing filter fields: {', '.join(missing_fields)}",
                "All filter fields must be specified",
                "Filters"
            )
            
        if empty_fields:
            return ValidationResult(
                False,
                f"Empty filter fields: {', '.join(empty_fields)}",
                "All fields must have actual values",
                "Filters"
            )
            
        return ValidationResult(True, "Filters & Eligibility section complete", "", "Filters")
        
    def validate_conflict_handling(self, content: str) -> ValidationResult:
        """Validate Conflict Handling section"""
        start = time.time()
        self.log("Validating Conflict Handling section...")
        
        # Extract conflict handling section
        conflict_match = re.search(r'## 6\) Conflict Handling(.*?)(?=##|$)', content, re.DOTALL)
        if not conflict_match:
            self.track_timing("conflicts", time.time() - start)
            return ValidationResult(False, "Conflict Handling section not found", "", "Conflicts")
            
        conflicts = conflict_match.group(1)
        
        # Check for buy vs sell conflict handling
        if not re.search(r'\*\*Buy vs Sell same bar\*\*:\s*`([^`]+)`', conflicts):
            self.track_timing("conflicts", time.time() - start)
            return ValidationResult(
                False,
                "Buy vs Sell conflict handling not specified",
                "Must specify how to handle simultaneous buy/sell signals",
                "Conflicts"
            )
            
        # Check for exit collision handling
        if not re.search(r'\*\*Exit Collisions.*?\*\*:\s*`([^`]+)`', conflicts):
            self.track_timing("conflicts", time.time() - start)
            return ValidationResult(
                False,
                "Exit collision handling not specified",
                "Must specify priority for multiple exit conditions",
                "Conflicts"
            )
            
        self.track_timing("conflicts", time.time() - start)
        return ValidationResult(True, "Conflict Handling section complete", "", "Conflicts")
        
    def validate_checklist(self, content: str) -> ValidationResult:
        """Validate that all checklist items are marked complete"""
        start = time.time()
        self.log("Validating checklist completion...")
        
        # Extract checklist section
        checklist_match = re.search(r'## Checklist(.*?)(?=$)', content, re.DOTALL)
        if not checklist_match:
            self.track_timing("checklist", time.time() - start)
            return ValidationResult(False, "Checklist section not found", "", "Checklist")
            
        checklist = checklist_match.group(1)
        
        # Find all checklist items
        all_items = re.findall(r'- \[([ x])\] (.+)', checklist)
        
        if not all_items:
            self.track_timing("checklist", time.time() - start)
            return ValidationResult(
                False,
                "No checklist items found",
                "Checklist must contain validation items",
                "Checklist"
            )
            
        # Check for incomplete items
        incomplete_items = [item[1] for item in all_items if item[0] != 'x']
        
        if incomplete_items:
            self.track_timing("checklist", time.time() - start)
            return ValidationResult(
                False,
                f"Incomplete checklist items: {len(incomplete_items)}/{len(all_items)}",
                f"Incomplete: {', '.join(incomplete_items[:3])}{'...' if len(incomplete_items) > 3 else ''}",
                "Checklist"
            )
            
        self.track_timing("checklist", time.time() - start)
        return ValidationResult(
            True, 
            f"All {len(all_items)} checklist items marked complete",
            "",
            "Checklist"
        )
        
    def validate_parameter_completeness(self, content: str) -> ValidationResult:
        """Validate that all parameters have concrete values"""
        start = time.time()
        self.log("Validating parameter completeness...")
        
        # Extract all parameter specifications
        param_pattern = r'\*\*Parameters?\*\*:\s*`([^`]+)`'
        all_params = re.findall(param_pattern, content)
        
        if not all_params:
            self.track_timing("parameters", time.time() - start)
            return ValidationResult(
                False,
                "No parameters found in specification",
                "Strategy must define parameters",
                "Parameters"
            )
            
        # Check for placeholder values
        placeholder_params = []
        for param in all_params:
            if any(p in param.upper() for p in ['TBD', 'TODO', '...', 'PLACEHOLDER']):
                placeholder_params.append(param)
                
        if placeholder_params:
            self.track_timing("parameters", time.time() - start)
            return ValidationResult(
                False,
                f"Parameters with placeholder values: {len(placeholder_params)}",
                f"Fix: {', '.join(placeholder_params[:2])}{'...' if len(placeholder_params) > 2 else ''}",
                "Parameters"
            )
            
        self.track_timing("parameters", time.time() - start)
        return ValidationResult(
            True,
            f"All {len(all_params)} parameter definitions complete",
            "",
            "Parameters"
        )
        
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        self.log(f"{Colors.BOLD}Strategy Specification Validation{Colors.END}")
        self.log(f"Validating: {self.strategy_name}")
        self.log("=" * 60)
        
        # Load strategy specification
        success, content = self.load_strategy_spec()
        if not success:
            self.error(content)
            return False
            
        self.success(f"Loaded {len(content)} characters from {self.smr_path.name}")
        
        # Run validations
        validations = [
            lambda: self.validate_section_presence(content),
            lambda: self.validate_overview_section(content),
            lambda: self.validate_narrative_description(content),
            lambda: self.validate_entry_logic(content),
            lambda: self.validate_exit_logic(content),
            lambda: self.validate_position_management(content),
            lambda: self.validate_filters(content),
            lambda: self.validate_conflict_handling(content),
            lambda: self.validate_checklist(content),
            lambda: self.validate_parameter_completeness(content)
        ]
        
        all_passed = True
        section_results = {}
        
        for validation in validations:
            result = validation()
            self.results.append(result)
            
            if result.section:
                section_results[result.section] = result.passed
                
            if result.passed:
                self.success(result.message)
            else:
                self.error(result.message)
                if result.details:
                    print(f"  {Colors.YELLOW}→ {result.details}{Colors.END}")
                all_passed = False
                
        self.log("=" * 60)
        
        # Performance summary
        total_time = time.time() - self.start_time
        self.log(f"{Colors.BOLD}Performance Summary:{Colors.END}")
        self.log(f"Total validation time: {total_time:.3f}s")
        
        if self.timing_data:
            slowest = max(self.timing_data.items(), key=lambda x: x[1])
            self.log(f"Slowest operation: {slowest[0]} ({slowest[1]:.3f}s)")
            
        # Results summary
        if all_passed:
            self.success(f"{Colors.BOLD}[CHECK] Strategy specification validation PASSED!{Colors.END}")
            
            # Run complexity assessment
            self.log("\n" + "=" * 60)
            self.log(f"{Colors.BOLD}Complexity Assessment{Colors.END}")
            self.log("=" * 60)
            
            assessor = ComplexityAssessor()
            complexity_result = assessor.calculate_complexity(content)
            
            # Display scoring breakdown
            self.log(f"\n{Colors.BOLD}Scoring Breakdown:{Colors.END}")
            for dimension, score in complexity_result['scores'].items():
                dimension_display = dimension.replace('_', ' ').title()
                self.log(f"  • {dimension_display}: {score} points")
            
            self.log(f"\n{Colors.BOLD}Total Score:{Colors.END} {complexity_result['total_score']} points")
            
            # Display complexity level with color coding
            level = complexity_result['complexity_level']
            if level == "SIMPLE":
                level_color = Colors.GREEN
            elif level == "MODERATE":
                level_color = Colors.YELLOW
            elif level == "COMPLEX":
                level_color = Colors.YELLOW
            else:  # ADVANCED
                level_color = Colors.RED
                
            self.log(f"{Colors.BOLD}Complexity Level:{Colors.END} {level_color}{level}{Colors.END}")
            
            # Display time targets
            self.log(f"\n{Colors.BOLD}Time Targets:{Colors.END}")
            self.log(f"  • Planning Phase: {complexity_result['time_targets']['planning']}")
            self.log(f"  • Building Phase: {complexity_result['time_targets']['building']}")
            self.log(f"  • Total Estimated: {complexity_result['time_targets']['total']}")
            
            self.log("\n" + "=" * 60)
            self.log(f"\n{Colors.GREEN}Strategy '{self.strategy_name}' is ready for engine building.{Colors.END}")
            self.log("\nNext steps:")
            self.log("1. Run: /plan-strategy to create development plan")
            self.log("2. Run: /build-engine to generate the backtest engine")
            self.log("3. Complete parameter_config.md with your values")
        else:
            failed_sections = [s for s, p in section_results.items() if not p]
            self.error(f"{Colors.BOLD}[X] Strategy validation FAILED{Colors.END}")
            self.log(f"\n{Colors.RED}Failed sections: {', '.join(failed_sections)}{Colors.END}")
            self.log("\nPlease complete all sections in the strategy specification")
            self.log("Refer to docs/guides/STRAT_TEMPLATE.md for requirements")
            
        # UX observations
        self.log(f"\n{Colors.BOLD}UX Observations:{Colors.END}")
        if total_time > 1.0:
            self.warning(f"Validation took {total_time:.1f}s - consider optimization for better UX")
        else:
            self.success(f"Fast validation ({total_time:.3f}s) - good user experience")
            
        return all_passed


def main():
    """Main validation function"""
    # Check for test mode flag
    test_mode = '--test' in sys.argv
    
    validator = StrategyValidator(test_mode=test_mode)
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()