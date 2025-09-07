"""
Reference Run Optimization System

Provides baseline comparison functionality for parameter optimization.
Enables incremental testing and smart symbol universe management.
"""

import logging
import json
import pickle
from typing import Dict, Any, List, Set, Optional, Tuple
from datetime import datetime
import pandas as pd
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass 
class ReferenceRunResult:
    """Results from a reference parameter run."""
    run_id: str
    parameters: Dict[str, Any]
    active_symbols: Set[str]  # Symbols that generated any signals
    performance_metrics: Dict[str, float]
    signal_counts: Dict[str, int]  # symbol -> signal count
    execution_time_ms: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['active_symbols'] = list(result['active_symbols'])
        result['timestamp'] = result['timestamp'].isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferenceRunResult':
        """Create from dictionary."""
        data['active_symbols'] = set(data['active_symbols'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class OptimizationContext:
    """Context information for optimization runs."""
    base_parameters: Dict[str, Any]
    parameter_ranges: Dict[str, Tuple[Any, Any]]
    optimization_target: str  # 'sharpe_ratio', 'total_return', etc.
    universe_reduction_enabled: bool
    max_universe_reduction_pct: float


class ReferenceEngine:
    """
    Reference Run Optimization System for parameter sweeps.
    
    Key Features:
    - Baseline parameter run storage and analysis
    - Symbol universe reduction based on reference activity
    - Incremental optimization: only test symbols that showed activity
    - Performance comparison and parameter sensitivity analysis
    - Universal application: works with any strategy's parameter types
    
    Usage Examples:
    - Store RSI(30) as reference, then optimize RSI(25, 35, 40) only on active symbols
    - Use momentum(10) baseline to test momentum(5, 15, 20) with reduced universe
    - Any strategy can benefit from reference-based universe reduction
    """
    
    def __init__(self, cache_dir: str = "data/optimization"):
        """
        Initialize reference engine.
        
        Args:
            cache_dir: Directory for storing reference run data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Reference run storage
        self.reference_runs: Dict[str, ReferenceRunResult] = {}
        self.current_context: Optional[OptimizationContext] = None
        
        # Performance tracking
        self.optimization_stats = {
            'reference_runs_stored': 0,
            'universe_reductions_applied': 0,
            'symbols_eliminated': 0,
            'optimization_speedup_factor': 1.0
        }
        
        # Load existing reference runs
        self._load_reference_runs()
        
        self.logger.info("ReferenceEngine initialized for parameter optimization")
    
    def set_optimization_context(self, context: OptimizationContext) -> None:
        """
        Set context for the current optimization study.
        
        Args:
            context: Optimization context with base parameters and ranges
            
        Example:
            context = OptimizationContext(
                base_parameters={'rsi_period': 30, 'volume_threshold': 1000000},
                parameter_ranges={'rsi_period': (20, 40), 'volume_threshold': (500000, 2000000)},
                optimization_target='sharpe_ratio',
                universe_reduction_enabled=True,
                max_universe_reduction_pct=0.5
            )
            engine.set_optimization_context(context)
        """
        self.current_context = context
        self.logger.info(f"Set optimization context for target: {context.optimization_target}")
    
    def store_reference_run(self, 
                           run_id: str,
                           parameters: Dict[str, Any],
                           backtest_results: Dict[str, Any]) -> ReferenceRunResult:
        """
        Store results from a reference parameter run.
        
        Args:
            run_id: Unique identifier for the run
            parameters: Parameter values used in the run
            backtest_results: Results from backtest execution
            
        Returns:
            ReferenceRunResult object
            
        Example:
            reference = engine.store_reference_run(
                "baseline_rsi_30",
                {'rsi_period': 30, 'sma_period': 20},
                backtest_results
            )
        """
        # Extract active symbols and performance metrics
        active_symbols = self._extract_active_symbols(backtest_results)
        performance_metrics = self._extract_performance_metrics(backtest_results)
        signal_counts = self._extract_signal_counts(backtest_results)
        
        reference_result = ReferenceRunResult(
            run_id=run_id,
            parameters=parameters,
            active_symbols=active_symbols,
            performance_metrics=performance_metrics,
            signal_counts=signal_counts,
            execution_time_ms=backtest_results.get('execution_time_ms', 0),
            timestamp=datetime.now()
        )
        
        # Store in memory and persist
        self.reference_runs[run_id] = reference_result
        self._persist_reference_run(reference_result)
        
        self.optimization_stats['reference_runs_stored'] += 1
        
        self.logger.info(f"Stored reference run {run_id}: {len(active_symbols)} active symbols")
        
        return reference_result
    
    def get_optimized_universe(self, 
                             full_universe: List[str],
                             current_parameters: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """
        Get optimized symbol universe based on reference runs.
        
        Args:
            full_universe: Complete list of symbols to consider
            current_parameters: Parameter values for current optimization step
            
        Returns:
            Tuple of (optimized_symbol_list, optimization_metadata)
            
        Example:
            # Full universe has 500 symbols, but only 50 were active in reference
            optimized_symbols, metadata = engine.get_optimized_universe(
                all_symbols, {'rsi_period': 25}
            )
            # Returns ~50-100 symbols for much faster execution
        """
        if not self.current_context or not self.current_context.universe_reduction_enabled:
            return full_universe, {'reduction_applied': False, 'reason': 'disabled'}
        
        # Find most relevant reference run
        best_reference = self._find_best_reference_run(current_parameters)
        
        if not best_reference:
            return full_universe, {'reduction_applied': False, 'reason': 'no_reference'}
        
        # Get active symbols from reference
        reference_active = best_reference.active_symbols
        
        if not reference_active:
            return full_universe, {'reduction_applied': False, 'reason': 'no_active_symbols'}
        
        # Apply universe reduction logic
        optimized_universe = self._apply_universe_reduction(
            full_universe, reference_active, current_parameters, best_reference.parameters
        )
        
        reduction_pct = (len(full_universe) - len(optimized_universe)) / len(full_universe)
        speedup_factor = len(full_universe) / max(1, len(optimized_universe))
        
        self.optimization_stats['universe_reductions_applied'] += 1
        self.optimization_stats['symbols_eliminated'] += len(full_universe) - len(optimized_universe)
        self.optimization_stats['optimization_speedup_factor'] = speedup_factor
        
        metadata = {
            'reduction_applied': True,
            'reference_run': best_reference.run_id,
            'original_universe_size': len(full_universe),
            'reduced_universe_size': len(optimized_universe),
            'reduction_pct': round(reduction_pct * 100, 2),
            'estimated_speedup': round(speedup_factor, 2),
            'reference_active_symbols': len(reference_active)
        }
        
        self.logger.info(f"Universe reduction: {len(full_universe)} → {len(optimized_universe)} symbols "
                        f"({metadata['reduction_pct']}% reduction, {metadata['estimated_speedup']}x speedup)")
        
        return optimized_universe, metadata
    
    def analyze_parameter_sensitivity(self, 
                                    parameter_results: List[Tuple[Dict[str, Any], Dict[str, float]]]) -> Dict[str, Any]:
        """
        Analyze parameter sensitivity based on results.
        
        Args:
            parameter_results: List of (parameters, performance_metrics) tuples
            
        Returns:
            Sensitivity analysis results
            
        Example:
            results = [
                ({'rsi_period': 20}, {'sharpe_ratio': 1.2, 'total_return': 0.15}),
                ({'rsi_period': 30}, {'sharpe_ratio': 1.5, 'total_return': 0.18}),
                ({'rsi_period': 40}, {'sharpe_ratio': 1.1, 'total_return': 0.12})
            ]
            sensitivity = engine.analyze_parameter_sensitivity(results)
        """
        if not parameter_results or not self.current_context:
            return {}
        
        target_metric = self.current_context.optimization_target
        sensitivity_analysis = {
            'parameter_effects': {},
            'optimal_values': {},
            'stability_metrics': {},
            'recommendations': []
        }
        
        # Group results by parameter
        param_effects = {}
        for params, metrics in parameter_results:
            target_value = metrics.get(target_metric, 0)
            
            for param_name, param_value in params.items():
                if param_name not in param_effects:
                    param_effects[param_name] = []
                param_effects[param_name].append((param_value, target_value))
        
        # Analyze each parameter's effect
        for param_name, value_performance_pairs in param_effects.items():
            if len(value_performance_pairs) > 1:
                # Sort by parameter value
                sorted_pairs = sorted(value_performance_pairs, key=lambda x: x[0])
                
                param_values = [x[0] for x in sorted_pairs]
                performance_values = [x[1] for x in sorted_pairs]
                
                # Find optimal value
                best_idx = performance_values.index(max(performance_values))
                optimal_value = param_values[best_idx]
                optimal_performance = performance_values[best_idx]
                
                # Calculate sensitivity metrics
                performance_range = max(performance_values) - min(performance_values)
                param_range = max(param_values) - min(param_values)
                
                sensitivity = performance_range / param_range if param_range > 0 else 0
                
                sensitivity_analysis['parameter_effects'][param_name] = {
                    'values_tested': param_values,
                    'performance_values': performance_values,
                    'sensitivity_score': round(sensitivity, 4),
                    'performance_range': round(performance_range, 4)
                }
                
                sensitivity_analysis['optimal_values'][param_name] = {
                    'value': optimal_value,
                    'performance': round(optimal_performance, 4)
                }
                
                # Stability analysis
                performance_std = pd.Series(performance_values).std()
                stability_score = 1.0 / (1.0 + performance_std)  # Higher is more stable
                
                sensitivity_analysis['stability_metrics'][param_name] = {
                    'performance_std': round(performance_std, 4),
                    'stability_score': round(stability_score, 4)
                }
        
        # Generate recommendations
        recommendations = []
        for param_name, effects in sensitivity_analysis['parameter_effects'].items():
            if effects['sensitivity_score'] > 0.01:  # Significant effect
                optimal = sensitivity_analysis['optimal_values'][param_name]
                recommendations.append(
                    f"{param_name}: Optimal value {optimal['value']} "
                    f"(performance: {optimal['performance']})"
                )
            else:
                recommendations.append(
                    f"{param_name}: Low sensitivity, current value acceptable"
                )
        
        sensitivity_analysis['recommendations'] = recommendations
        
        return sensitivity_analysis
    
    def _extract_active_symbols(self, backtest_results: Dict[str, Any]) -> Set[str]:
        """Extract symbols that were active during the backtest."""
        active_symbols = set()
        
        # Check trades for active symbols
        if 'trades' in backtest_results:
            for trade in backtest_results['trades']:
                if isinstance(trade, dict) and 'symbol' in trade:
                    active_symbols.add(trade['symbol'])
        
        # Check events for additional active symbols
        if 'events' in backtest_results:
            for event in backtest_results['events']:
                if isinstance(event, dict) and 'data' in event:
                    event_data = event['data']
                    if isinstance(event_data, dict) and 'symbol' in event_data:
                        active_symbols.add(event_data['symbol'])
        
        return active_symbols
    
    def _extract_performance_metrics(self, backtest_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract key performance metrics from backtest results."""
        metrics = {}
        
        # Basic metrics
        if 'final_equity' in backtest_results:
            initial_equity = backtest_results.get('initial_equity', 100000)
            metrics['total_return'] = (backtest_results['final_equity'] - initial_equity) / initial_equity
        
        metrics['total_trades'] = backtest_results.get('total_trades', 0)
        
        # If portfolio state includes additional metrics
        portfolio_state = backtest_results.get('portfolio_final_state', {})
        if isinstance(portfolio_state, dict):
            for key in ['sharpe_ratio', 'max_drawdown', 'win_rate', 'profit_factor']:
                if key in portfolio_state:
                    metrics[key] = portfolio_state[key]
        
        return metrics
    
    def _extract_signal_counts(self, backtest_results: Dict[str, Any]) -> Dict[str, int]:
        """Extract signal counts per symbol."""
        signal_counts = {}
        
        if 'events' in backtest_results:
            for event in backtest_results['events']:
                if (isinstance(event, dict) and 
                    event.get('type') == 'signal_generated' and
                    'data' in event):
                    
                    event_data = event['data']
                    if isinstance(event_data, dict) and 'symbol' in event_data:
                        symbol = event_data['symbol']
                        signal_counts[symbol] = signal_counts.get(symbol, 0) + 1
        
        return signal_counts
    
    def _find_best_reference_run(self, current_parameters: Dict[str, Any]) -> Optional[ReferenceRunResult]:
        """Find the most relevant reference run for current parameters."""
        if not self.reference_runs:
            return None
        
        # For now, use the most recent reference run
        # Future enhancement: find most similar parameters
        return max(self.reference_runs.values(), key=lambda x: x.timestamp)
    
    def _apply_universe_reduction(self, 
                                full_universe: List[str],
                                reference_active: Set[str],
                                current_params: Dict[str, Any],
                                reference_params: Dict[str, Any]) -> List[str]:
        """
        Apply universe reduction logic based on reference run and parameter changes.
        
        Strategy:
        1. Always include symbols that were active in reference
        2. Add symbols that might become active due to parameter changes
        3. Respect maximum reduction percentage limit
        """
        # Start with reference active symbols
        optimized_universe = set(reference_active)
        
        # Determine if parameters are more or less restrictive
        is_more_restrictive = self._is_parameter_set_more_restrictive(current_params, reference_params)
        
        if is_more_restrictive:
            # More restrictive parameters: use only reference active symbols
            pass
        else:
            # Less restrictive parameters: add potentially active symbols
            
            # Add a percentage of the remaining universe
            remaining_symbols = set(full_universe) - reference_active
            expansion_count = min(
                len(remaining_symbols),
                int(len(reference_active) * 0.5)  # Add up to 50% more symbols
            )
            
            # Add symbols with highest volume/activity (simplified heuristic)
            additional_symbols = list(remaining_symbols)[:expansion_count]
            optimized_universe.update(additional_symbols)
        
        # Ensure we don't exceed maximum reduction limit
        max_reduction = self.current_context.max_universe_reduction_pct
        min_universe_size = int(len(full_universe) * (1 - max_reduction))
        
        if len(optimized_universe) < min_universe_size:
            # Add more symbols to meet minimum size requirement
            remaining = set(full_universe) - optimized_universe
            additional_needed = min_universe_size - len(optimized_universe)
            optimized_universe.update(list(remaining)[:additional_needed])
        
        return list(optimized_universe)
    
    def _is_parameter_set_more_restrictive(self, 
                                         current: Dict[str, Any], 
                                         reference: Dict[str, Any]) -> bool:
        """
        Determine if current parameters are more restrictive than reference.
        
        Universal heuristics that work with any strategy:
        - Higher thresholds for RSI, volume, price filters are more restrictive
        - Longer periods for moving averages can be more restrictive
        - Lower volatility limits are more restrictive
        """
        restrictive_changes = 0
        total_changes = 0
        
        for param_name, current_value in current.items():
            if param_name in reference:
                reference_value = reference[param_name]
                
                if isinstance(current_value, (int, float)) and isinstance(reference_value, (int, float)):
                    total_changes += 1
                    
                    # Heuristic-based restrictiveness detection
                    if ('rsi' in param_name.lower() or 
                        'volume' in param_name.lower() or
                        'price' in param_name.lower()):
                        # Higher thresholds are more restrictive
                        if current_value > reference_value:
                            restrictive_changes += 1
                    
                    elif ('volatility' in param_name.lower() or
                          'drawdown' in param_name.lower()):
                        # Lower limits are more restrictive
                        if current_value < reference_value:
                            restrictive_changes += 1
        
        return restrictive_changes > total_changes / 2 if total_changes > 0 else False
    
    def _persist_reference_run(self, reference: ReferenceRunResult) -> None:
        """Persist reference run to disk."""
        file_path = self.cache_dir / f"reference_{reference.run_id}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(reference.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to persist reference run {reference.run_id}: {str(e)}")
    
    def _load_reference_runs(self) -> None:
        """Load persisted reference runs."""
        pattern = "reference_*.json"
        for file_path in self.cache_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    reference = ReferenceRunResult.from_dict(data)
                    self.reference_runs[reference.run_id] = reference
            except Exception as e:
                self.logger.warning(f"Failed to load reference run from {file_path}: {str(e)}")
        
        self.logger.info(f"Loaded {len(self.reference_runs)} reference runs")
    
    def clear_cache(self, older_than_days: Optional[int] = None) -> None:
        """
        Clear reference run cache.
        
        Args:
            older_than_days: Clear runs older than N days, or None for all
        """
        if older_than_days is None:
            # Clear all
            self.reference_runs.clear()
            for file_path in self.cache_dir.glob("reference_*.json"):
                file_path.unlink()
            self.logger.info("Cleared all reference runs")
        else:
            # Clear old runs
            cutoff_date = datetime.now() - pd.Timedelta(days=older_than_days)
            to_remove = []
            
            for run_id, reference in self.reference_runs.items():
                if reference.timestamp < cutoff_date:
                    to_remove.append(run_id)
            
            for run_id in to_remove:
                del self.reference_runs[run_id]
                file_path = self.cache_dir / f"reference_{run_id}.json"
                if file_path.exists():
                    file_path.unlink()
            
            self.logger.info(f"Cleared {len(to_remove)} old reference runs")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization performance statistics."""
        return {
            **self.optimization_stats,
            'reference_runs_stored': len(self.reference_runs),
            'cache_size_mb': sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (1024 * 1024)
        }
    
    def get_reference_runs_summary(self) -> Dict[str, Any]:
        """Get summary of stored reference runs."""
        if not self.reference_runs:
            return {'total_runs': 0}
        
        summary = {
            'total_runs': len(self.reference_runs),
            'runs': []
        }
        
        for run_id, reference in self.reference_runs.items():
            run_info = {
                'run_id': run_id,
                'parameters': reference.parameters,
                'active_symbols_count': len(reference.active_symbols),
                'total_signals': sum(reference.signal_counts.values()),
                'timestamp': reference.timestamp.isoformat(),
                'performance_metrics': reference.performance_metrics
            }
            summary['runs'].append(run_info)
        
        # Sort by timestamp (most recent first)
        summary['runs'] = sorted(summary['runs'], 
                               key=lambda x: x['timestamp'], reverse=True)
        
        return summary