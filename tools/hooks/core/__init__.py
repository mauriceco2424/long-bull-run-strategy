"""
Core hooks - Essential hooks for pipeline integrity

These hooks implement the minimal set required for safe pipeline operation:

- before_analyzer_run: Resource and precondition validation
- after_analyzer_run: Artifact integrity verification  
- before_evaluator: Readiness check and red flag detection
- after_evaluator: Decision processing (halt/rerun/pass)
- before_registry_append: CSV lock and duplicate checking
- after_registry_append: Observability and notifications

All core hooks are P0 (blocking) except after_registry_append (P2).
"""

# Core hooks are not imported here to avoid loading all modules
# They are loaded dynamically by the HookRunner when needed

__all__ = [
    "before_analyzer_run",
    "after_analyzer_run", 
    "before_evaluator",
    "after_evaluator",
    "before_registry_append",
    "after_registry_append"
]