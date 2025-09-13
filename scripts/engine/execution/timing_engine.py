"""
Simple Timing Engine for Trade Execution

Handles execution timing logic for backtests.
"""

from typing import Any, Dict
from datetime import datetime


class TimingEngine:
    """Simple timing engine for backtest execution."""
    
    def __init__(self, execution_mode: str = "next_bar_open"):
        self.execution_mode = execution_mode
    
    def get_execution_time(self, signal_time: datetime, current_bar: Dict[str, Any]) -> datetime:
        """Get the execution time for a trade signal."""
        if self.execution_mode == "next_bar_open":
            # Execute at next bar open (simple implementation)
            return signal_time
        else:
            return signal_time
    
    def can_execute_now(self, signal_time: datetime, current_time: datetime) -> bool:
        """Check if a signal can be executed at the current time."""
        return current_time >= signal_time