"""
Centralized Logging Configuration

Provides quiet mode for agent operations to prevent screen output spam.
"""

import logging
import os
from typing import Optional

# Global quiet mode setting - DEFAULT TO TRUE (silent by default)
QUIET_MODE = os.getenv('TRADING_QUIET_MODE', 'true').lower() == 'true'


def setup_logging(
    name: str = None, 
    level: Optional[str] = None,
    quiet_mode: Optional[bool] = None
) -> logging.Logger:
    """
    Setup logging with quiet mode enabled by default.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level override ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        quiet_mode: Override global quiet mode setting
        
    Returns:
        Configured logger
    """
    # Load persistent quiet mode state
    from pathlib import Path
    import json
    state_file = Path("cloud/state/quiet_mode.json")
    persistent_quiet = True  # Default to True
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                persistent_quiet = json.load(f).get("enabled", True)
        except:
            persistent_quiet = True
    
    # Determine quiet mode (check persistent state first)
    if quiet_mode is None:
        quiet_mode = persistent_quiet if state_file.exists() else QUIET_MODE
    
    # Determine log level - ONLY ERRORS by default
    if quiet_mode:
        # In quiet mode, only show ERRORS (not even warnings to reduce noise)
        default_level = 'ERROR'
    else:
        # Normal mode shows info and above
        default_level = 'INFO'
    
    if level is None:
        level = os.getenv('TRADING_LOG_LEVEL', default_level)
    
    # Configure logging - suppress most output
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(levelname)s: %(message)s',  # Simplified format
        force=True  # Override any previous basicConfig calls
    )
    
    # Create logger
    logger = logging.getLogger(name or __name__)
    
    return logger


def enable_quiet_mode():
    """Enable quiet mode globally."""
    global QUIET_MODE
    QUIET_MODE = True
    os.environ['TRADING_QUIET_MODE'] = 'true'
    
    # Update existing loggers
    logging.getLogger().setLevel(logging.WARNING)


def disable_quiet_mode():
    """Disable quiet mode globally."""
    global QUIET_MODE
    QUIET_MODE = False
    os.environ['TRADING_QUIET_MODE'] = 'false'
    
    # Update existing loggers
    logging.getLogger().setLevel(logging.INFO)


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled (loads from persistent state)."""
    # Load persistent state if available
    from pathlib import Path
    import json
    state_file = Path("cloud/state/quiet_mode.json")
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                return json.load(f).get("enabled", True)  # Default to True
        except:
            return True  # Default to quiet on any error
    return QUIET_MODE


class QuietProgressTracker:
    """
    Ultra-minimal progress tracker that shows ONLY completion status.
    Silent during operation - only reports final results or critical errors.
    """
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.operation_description = ""
        self.operation_start_time = None
        self.operation_failed = False
    
    def start_operation(self, description: str, total_phases: int = 1):
        """Start operation - completely silent."""
        import time
        self.operation_description = description
        self.operation_start_time = time.time()
        self.operation_failed = False
        # COMPLETELY SILENT - no output at all
    
    def start_phase(self, description: str, weight: float = 1.0):
        """Start phase - completely silent."""
        pass
    
    def update_progress(self, progress: float, details: str = ""):
        """Update progress - completely silent."""
        pass
    
    def complete_phase(self):
        """Complete phase - completely silent."""
        pass
    
    def complete_operation(self, show_success: bool = False):
        """Complete operation - only show output if explicitly requested or if not in quiet mode."""
        import time
        if self.operation_start_time:
            duration = time.time() - self.operation_start_time
            duration_str = f"{duration:.1f}s" if duration < 60 else f"{int(duration//60)}m {int(duration%60)}s"
            
            # Only show success if explicitly requested or not in quiet mode
            if show_success and not QUIET_MODE:
                self.logger.info(f"✓ {self.operation_description} completed in {duration_str}")
        
    def report_failure(self, error_message: str):
        """Report failure - always show errors regardless of quiet mode."""
        self.operation_failed = True
        self.logger.error(f"✗ {self.operation_description} failed: {error_message}")
        
    def get_status(self):
        """Get status - always available regardless of quiet mode."""
        return {
            'operation_description': self.operation_description,
            'quiet_mode': QUIET_MODE,
            'failed': self.operation_failed
        }