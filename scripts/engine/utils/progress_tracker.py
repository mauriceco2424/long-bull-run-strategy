"""
Progress Tracker

Unified progress reporting with ETA estimation for all trading operations.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import threading


class ProgressTracker:
    """
    Unified progress tracking system for all trading operations.
    
    Features:
    - Unified progress bar format
    - ETA estimation
    - Phase management
    - Thread-safe updates
    - Memory of timing for better estimates
    """
    
    def __init__(self):
        """Initialize progress tracker."""
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Current state
        self.current_phase = None
        self.phase_start_time = None
        self.total_phases = 0
        self.completed_phases = 0
        
        # Progress within current phase
        self.phase_progress = 0.0
        self.phase_description = ""
        
        # Timing history for ETA estimation
        self.phase_timing_history = {}
        self.last_update_time = None
        self.update_interval = 1.0  # Minimum seconds between updates
        
        # Overall operation
        self.operation_start_time = None
        self.operation_description = ""
        
    def start_operation(self, description: str, total_phases: int = 1) -> None:
        """
        Start a new operation with progress tracking.
        
        Args:
            description: Description of the operation
            total_phases: Total number of phases in the operation
        """
        with self._lock:
            self.operation_description = description
            self.operation_start_time = time.time()
            self.total_phases = total_phases
            self.completed_phases = 0
            self.current_phase = None
            
            self.logger.info(f"Started operation: {description}")
    
    def start_phase(self, description: str, weight: float = 1.0) -> None:
        """
        Start a new phase within the current operation.
        
        Args:
            description: Phase description
            weight: Relative weight of this phase (for ETA calculation)
        """
        with self._lock:
            # Complete previous phase if exists
            if self.current_phase is not None:
                self.completed_phases += 1
            
            self.current_phase = description
            self.phase_description = description
            self.phase_start_time = time.time()
            self.phase_progress = 0.0
            
            self._display_progress()
            self.logger.debug(f"Started phase: {description}")
    
    def update_progress(self, progress: float, details: str = "") -> None:
        """
        Update progress within current phase.
        
        Args:
            progress: Progress as decimal (0.0 to 1.0)
            details: Optional progress details
        """
        with self._lock:
            # Rate limiting - don't update too frequently
            current_time = time.time()
            if (self.last_update_time is not None and 
                current_time - self.last_update_time < self.update_interval):
                return
            
            self.phase_progress = max(0.0, min(1.0, progress))
            self.last_update_time = current_time
            
            # Update display
            self._display_progress(details)
    
    def complete_phase(self) -> None:
        """Complete the current phase."""
        with self._lock:
            if self.current_phase is None:
                return
            
            # Record phase timing
            if self.phase_start_time:
                phase_duration = time.time() - self.phase_start_time
                self._record_phase_timing(self.current_phase, phase_duration)
            
            self.phase_progress = 1.0
            self._display_progress()
            
            self.logger.debug(f"Completed phase: {self.current_phase}")
    
    def complete_operation(self) -> None:
        """Complete the entire operation."""
        with self._lock:
            if self.operation_start_time:
                total_duration = time.time() - self.operation_start_time
                self.logger.info(f"Completed operation: {self.operation_description} "
                               f"in {self._format_duration(total_duration)}")
            
            self._reset_state()
    
    def get_eta_estimate(self) -> Optional[timedelta]:
        """Get estimated time to completion."""
        if not self.operation_start_time or not self.current_phase:
            return None
        
        elapsed = time.time() - self.operation_start_time
        
        # Calculate overall progress
        overall_progress = self._calculate_overall_progress()
        
        if overall_progress <= 0:
            return None
        
        # Estimate total time based on current progress
        estimated_total_time = elapsed / overall_progress
        remaining_time = estimated_total_time - elapsed
        
        return timedelta(seconds=max(0, remaining_time))
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress across all phases."""
        if self.total_phases == 0:
            return 0.0
        
        # Progress from completed phases
        completed_progress = self.completed_phases / self.total_phases
        
        # Progress from current phase
        if self.current_phase:
            current_phase_contribution = self.phase_progress / self.total_phases
            completed_progress += current_phase_contribution
        
        return min(1.0, completed_progress)
    
    def _display_progress(self, details: str = "") -> None:
        """Display progress bar to console/logger."""
        if not self.current_phase:
            return
        
        # Calculate overall progress
        overall_progress = self._calculate_overall_progress()
        
        # Create progress bar
        progress_bar = self._create_progress_bar(overall_progress)
        
        # Format description
        if details:
            description = f"{self.phase_description}: {details}"
        else:
            description = self.phase_description
        
        # Get ETA
        eta = self.get_eta_estimate()
        eta_str = f" (~{self._format_eta(eta)})" if eta else ""
        
        # Format progress message
        progress_msg = f"{description}... {progress_bar} {overall_progress:.0%}{eta_str}"
        
        # Use logger for output (can be configured to display on console)
        self.logger.info(progress_msg)
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create ASCII progress bar."""
        filled = int(progress * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def _format_eta(self, eta: Optional[timedelta]) -> str:
        """Format ETA for display."""
        if not eta:
            return "unknown"
        
        total_seconds = int(eta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes}m"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration for display."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _record_phase_timing(self, phase_name: str, duration: float) -> None:
        """Record timing data for phase for future ETA estimation."""
        if phase_name not in self.phase_timing_history:
            self.phase_timing_history[phase_name] = []
        
        self.phase_timing_history[phase_name].append(duration)
        
        # Keep only last 10 timings for each phase
        if len(self.phase_timing_history[phase_name]) > 10:
            self.phase_timing_history[phase_name] = self.phase_timing_history[phase_name][-10:]
    
    def _reset_state(self) -> None:
        """Reset tracker state."""
        self.current_phase = None
        self.phase_start_time = None
        self.phase_progress = 0.0
        self.phase_description = ""
        self.operation_start_time = None
        self.operation_description = ""
        self.completed_phases = 0
        self.total_phases = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status for monitoring."""
        with self._lock:
            status = {
                'operation_active': self.operation_start_time is not None,
                'operation_description': self.operation_description,
                'current_phase': self.current_phase,
                'phase_progress': self.phase_progress,
                'overall_progress': self._calculate_overall_progress(),
                'completed_phases': self.completed_phases,
                'total_phases': self.total_phases,
                'eta_seconds': None
            }
            
            eta = self.get_eta_estimate()
            if eta:
                status['eta_seconds'] = eta.total_seconds()
            
            if self.operation_start_time:
                status['elapsed_seconds'] = time.time() - self.operation_start_time
            
            return status