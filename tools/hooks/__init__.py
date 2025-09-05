"""
Trading Pipeline Hooks Package

Provides hook execution system for the trading pipeline with the following components:

- Core hooks (minimal essential hooks for pipeline integrity)
- Hook context and result structures
- Hook runner with timeout, configuration, and error handling
- Configuration system for enabling/disabling hooks

Usage:
    from tools.hooks import HookRunner, HookContext
    
    runner = HookRunner()
    ctx = HookContext(run_id="test", run_path="/data/runs/test", phase="analyzer")
    result = runner.run_hook("before_analyzer_run", ctx)
"""

from .lib.hook_context import HookContext, HookResult
from .lib.hook_runner import HookRunner

__version__ = "1.0.0"
__all__ = ["HookContext", "HookResult", "HookRunner"]