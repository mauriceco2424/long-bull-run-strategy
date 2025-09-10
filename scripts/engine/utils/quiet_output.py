"""
Quiet Output Management

Provides comprehensive output suppression for external commands while preserving
error detection and critical failure visibility.
"""

import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import logging

# Import quiet mode detection
try:
    from .logging_config import is_quiet_mode
except ImportError:
    # Fallback for direct execution
    from logging_config import is_quiet_mode


class QuietSubprocess:
    """
    Wrapper for subprocess operations with intelligent quiet mode handling.
    
    Suppresses stdout/stderr in quiet mode while preserving:
    - Exit codes and error detection
    - Critical error visibility
    - Command execution reliability
    """
    
    @staticmethod
    def run(
        command: Union[str, List[str]], 
        capture_output: bool = False,
        text: bool = True,
        check: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        Run subprocess with quiet mode awareness.
        
        Args:
            command: Command to execute
            capture_output: Capture stdout/stderr (overrides quiet mode)
            text: Return string output instead of bytes
            check: Raise exception on non-zero exit
            cwd: Working directory
            env: Environment variables
            **kwargs: Additional subprocess arguments
            
        Returns:
            CompletedProcess with results
            
        Raises:
            subprocess.CalledProcessError: If check=True and command fails
        """
        quiet_mode = is_quiet_mode()
        
        # If capturing output or not in quiet mode, run normally
        if capture_output or not quiet_mode:
            return subprocess.run(
                command, 
                capture_output=capture_output,
                text=text,
                check=check,
                cwd=cwd,
                env=env,
                **kwargs
            )
        
        # In quiet mode: redirect output to null device
        with QuietContext():
            try:
                result = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    text=text,
                    cwd=cwd,
                    env=env,
                    **kwargs
                )
                
                # Check for errors and show them even in quiet mode
                if check and result.returncode != 0:
                    # Re-run to capture error for display
                    error_result = subprocess.run(
                        command,
                        capture_output=True,
                        text=text,
                        cwd=cwd,
                        env=env,
                        **kwargs
                    )
                    
                    # Show error even in quiet mode
                    logger = logging.getLogger(__name__)
                    logger.error(f"Command failed: {command}")
                    if error_result.stderr:
                        logger.error(f"Error output: {error_result.stderr}")
                    
                    raise subprocess.CalledProcessError(
                        result.returncode, 
                        command, 
                        stdout=error_result.stdout,
                        stderr=error_result.stderr
                    )
                
                return result
                
            except FileNotFoundError as e:
                # Show command not found errors even in quiet mode
                logger = logging.getLogger(__name__)
                logger.error(f"Command not found: {command}")
                raise e


@contextmanager
def QuietContext():
    """
    Context manager for suppressing all output during operations.
    
    Usage:
        with QuietContext():
            # All print statements and stdout operations are suppressed
            subprocess.run(['git', 'clone', 'repo'])
    """
    if not is_quiet_mode():
        # Not in quiet mode - no suppression
        yield
        return
    
    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        # Redirect to null device
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
    finally:
        # Restore original streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def quiet_print(*args, force: bool = False, **kwargs):
    """
    Print function that respects quiet mode.
    
    Args:
        *args: Arguments to print
        force: Show output even in quiet mode (for critical messages)
        **kwargs: Additional print arguments
    """
    if force or not is_quiet_mode():
        print(*args, **kwargs)


def run_quiet_command(
    command: Union[str, List[str]],
    description: Optional[str] = None,
    show_errors: bool = True,
    cwd: Optional[Union[str, Path]] = None
) -> subprocess.CompletedProcess:
    """
    High-level wrapper for running commands quietly.
    
    Args:
        command: Command to run
        description: Human-readable description for logging
        show_errors: Show error output even in quiet mode
        cwd: Working directory
        
    Returns:
        CompletedProcess result
        
    Raises:
        subprocess.CalledProcessError: On command failure
    """
    logger = logging.getLogger(__name__)
    
    # Log command start (only if not in quiet mode or if it's a critical operation)
    if description and not is_quiet_mode():
        logger.info(f"Running: {description}")
    
    try:
        result = QuietSubprocess.run(
            command,
            check=True,
            cwd=cwd
        )
        
        # Log success (only if not in quiet mode)
        if description and not is_quiet_mode():
            logger.info(f"Completed: {description}")
            
        return result
        
    except subprocess.CalledProcessError as e:
        if show_errors:
            # Always show errors, even in quiet mode
            error_msg = f"Command failed: {description or command}"
            logger.error(error_msg)
            
        raise e
    except FileNotFoundError:
        if show_errors:
            # Always show missing command errors
            error_msg = f"Command not found: {command}"
            logger.error(error_msg)
        raise


# Convenience functions for common operations
def git_quiet(*args, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run git command quietly."""
    return run_quiet_command(
        ['git'] + list(args),
        description=f"git {' '.join(args)}",
        cwd=cwd
    )


def gh_quiet(*args, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run GitHub CLI command quietly."""
    return run_quiet_command(
        ['gh'] + list(args),
        description=f"gh {' '.join(args)}",
        cwd=cwd
    )


def pip_quiet(*args) -> subprocess.CompletedProcess:
    """Run pip command quietly."""
    return run_quiet_command(
        [sys.executable, '-m', 'pip'] + list(args),
        description=f"pip {' '.join(args)}"
    )