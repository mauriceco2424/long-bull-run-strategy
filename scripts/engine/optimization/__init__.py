"""
Optimization Package

Advanced optimization infrastructure for parameter sweeps and strategy tuning.
"""

from .reference_engine import ReferenceEngine, ReferenceRunResult, OptimizationContext

__all__ = ["ReferenceEngine", "ReferenceRunResult", "OptimizationContext"]