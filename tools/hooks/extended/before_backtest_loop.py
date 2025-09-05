#!/usr/bin/env python3
"""
before_backtest_loop hook - P0 blocking
Safety ceilings and validation before backtest execution begins
"""

import os
import json
from typing import Dict, Any
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Validate safety parameters and ceilings before backtest loop
    
    Checks:
    - Maximum concurrent positions limits
    - Position size limits (% of equity)
    - Total notional exposure limits
    - Portfolio heat limits (total risk)
    - Leverage constraints
    - Memory and performance safety checks
    """
    
    ctx.ensure_hook_dir()
    checks = []
    warnings = []
    
    try:
        # Load configuration to get safety limits
        config_data = _load_backtest_config(ctx)
        
        if not config_data:
            return HookResult(
                success=False,
                message="No backtest configuration found for safety validation",
                priority="P0",
                should_halt=True
            )
        
        # Extract safety parameters
        risk_mgmt = config_data.get('risk_management', {})
        execution = config_data.get('execution', {})
        universe_info = _get_universe_info(ctx)
        
        # 1. Maximum concurrent positions check
        max_positions = risk_mgmt.get('max_concurrent_positions', 'unlimited')
        symbol_count = universe_info.get('symbol_count', 0)
        
        if isinstance(max_positions, int):
            if max_positions > symbol_count:
                warnings.append(f"Max positions ({max_positions}) > universe size ({symbol_count})")
            elif max_positions > 100:
                warnings.append(f"Max positions very high: {max_positions}")
            elif max_positions < 1:
                return HookResult(
                    success=False,
                    message=f"Invalid max_concurrent_positions: {max_positions} (must be ≥ 1)",
                    priority="P0",
                    should_halt=True
                )
            checks.append(f"Max concurrent positions: {max_positions}")
        else:
            warnings.append("Max concurrent positions not specified (unlimited)")
        
        # 2. Position size limits
        max_position_pct = risk_mgmt.get('max_position_size_pct')
        if max_position_pct is not None:
            if max_position_pct <= 0 or max_position_pct > 100:
                return HookResult(
                    success=False,
                    message=f"Invalid max_position_size_pct: {max_position_pct}% (must be 0-100)",
                    priority="P0",
                    should_halt=True
                )
            elif max_position_pct > 20:
                warnings.append(f"High position size limit: {max_position_pct}% (>20% risky)")
            
            checks.append(f"Max position size: {max_position_pct}% of equity")
        else:
            warnings.append("Max position size not specified")
        
        # 3. Portfolio heat limits (total risk exposure)
        max_heat_pct = risk_mgmt.get('max_portfolio_heat_pct')
        if max_heat_pct is not None:
            if max_heat_pct <= 0 or max_heat_pct > 100:
                return HookResult(
                    success=False,
                    message=f"Invalid max_portfolio_heat_pct: {max_heat_pct}% (must be 0-100)",
                    priority="P0",
                    should_halt=True
                )
            elif max_heat_pct > 25:
                warnings.append(f"High portfolio heat limit: {max_heat_pct}% (>25% very risky)")
            
            checks.append(f"Max portfolio heat: {max_heat_pct}%")
            
            # Validate consistency: portfolio heat should be >= max position size
            if max_position_pct and max_heat_pct < max_position_pct:
                return HookResult(
                    success=False,
                    message=f"Portfolio heat ({max_heat_pct}%) < max position size ({max_position_pct}%)",
                    priority="P0",
                    should_halt=True
                )
        else:
            warnings.append("Max portfolio heat not specified")
        
        # 4. Leverage constraints
        max_leverage = execution.get('max_leverage', 1.0)
        if max_leverage < 1.0:
            return HookResult(
                success=False,
                message=f"Invalid max_leverage: {max_leverage} (must be ≥ 1.0)",
                priority="P0",
                should_halt=True
            )
        elif max_leverage > 10.0:
            warnings.append(f"High leverage: {max_leverage}x (>10x very risky)")
        
        checks.append(f"Max leverage: {max_leverage}x")
        
        # 5. Minimum notional constraints
        min_notional = execution.get('min_notional')
        if min_notional is not None:
            if min_notional <= 0:
                return HookResult(
                    success=False,
                    message=f"Invalid min_notional: {min_notional} (must be > 0)",
                    priority="P0",
                    should_halt=True
                )
            checks.append(f"Min notional: {min_notional}")
        else:
            warnings.append("Min notional not specified")
        
        # 6. Stop-loss/Take-profit method validation
        sl_method = risk_mgmt.get('stop_loss_method')
        tp_method = risk_mgmt.get('take_profit_method')
        
        if not sl_method or sl_method == 'TBD':
            warnings.append("Stop-loss method not specified")
        else:
            checks.append(f"Stop-loss method: {sl_method}")
        
        if not tp_method or tp_method == 'TBD':
            warnings.append("Take-profit method not specified")
        else:
            checks.append(f"Take-profit method: {tp_method}")
        
        # 7. Performance safety checks
        estimated_memory = _estimate_memory_usage(ctx, config_data)
        if estimated_memory > 8_000_000_000:  # 8GB
            warnings.append(f"High estimated memory usage: {estimated_memory / 1_000_000_000:.1f}GB")
        
        checks.append(f"Estimated memory: {estimated_memory / 1_000_000:.0f}MB")
        
        # 8. Time range sanity for performance
        date_range_days = _calculate_date_range_days(ctx)
        if date_range_days > 1095:  # 3 years
            warnings.append(f"Long backtest period: {date_range_days} days (may be slow)")
        elif date_range_days < 30:
            warnings.append(f"Short backtest period: {date_range_days} days (may not be statistically significant)")
        
        checks.append(f"Backtest period: {date_range_days} days")
        
        # Generate safety summary
        safety_summary = {
            "max_positions": max_positions,
            "max_position_size_pct": max_position_pct,
            "max_portfolio_heat_pct": max_heat_pct,
            "max_leverage": max_leverage,
            "min_notional": min_notional,
            "stop_loss_method": sl_method,
            "take_profit_method": tp_method,
            "estimated_memory_mb": estimated_memory / 1_000_000,
            "backtest_days": date_range_days
        }
        
        # Write safety summary
        safety_file = os.path.join(ctx.run_path, "safety_summary.json")
        with open(safety_file, 'w') as f:
            json.dump(safety_summary, f, indent=2)
        
        # Write hook log
        log_data = {
            "hook": "before_backtest_loop",
            "status": "success",
            "checks_passed": len(checks),
            "warnings": len(warnings),
            "safety_summary": safety_summary,
            "details": {
                "checks": checks,
                "warnings": warnings
            },
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        message = f"Safety validation passed ({len(checks)} checks)"
        if warnings:
            message += f" with {len(warnings)} warnings"
        
        return HookResult(
            success=True,
            message=message,
            priority="P0",
            details={
                "checks": checks,
                "warnings": warnings,
                "safety_summary": safety_summary
            }
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in before_backtest_loop: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


def _load_backtest_config(ctx: HookContext) -> Dict[str, Any]:
    """Load backtest configuration from various possible sources"""
    
    # Try to load from run-specific config
    config_paths = [
        os.path.join(ctx.run_path, "config.json"),
        os.path.join("configs", f"{ctx.run_id}.json"),
        os.path.join("configs", "base_config.json"),
        os.path.join("configs", "default_config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                continue
    
    return {}


def _get_universe_info(ctx: HookContext) -> Dict[str, Any]:
    """Get universe information from resolved universe file or context"""
    
    universe_file = os.path.join(ctx.run_path, "resolved_universe.json")
    if os.path.exists(universe_file):
        try:
            with open(universe_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Fallback: parse from context
    if ctx.universe and ':' in ctx.universe:
        _, symbols_str = ctx.universe.split(':', 1)
        symbol_count = len([s.strip() for s in symbols_str.split(',') if s.strip()])
        return {"symbol_count": symbol_count}
    
    return {"symbol_count": 0}


def _estimate_memory_usage(ctx: HookContext, config: Dict[str, Any]) -> int:
    """Estimate memory usage for the backtest"""
    
    universe_info = _get_universe_info(ctx)
    symbol_count = universe_info.get('symbol_count', 10)
    date_range_days = _calculate_date_range_days(ctx)
    
    # Rough estimates (bytes)
    base_overhead = 100_000_000  # 100MB base
    per_symbol_per_day = 1000    # 1KB per symbol per day (OHLCV + features)
    feature_overhead = symbol_count * 50000  # 50KB per symbol for features
    
    estimated = base_overhead + (symbol_count * date_range_days * per_symbol_per_day) + feature_overhead
    
    return int(estimated)


def _calculate_date_range_days(ctx: HookContext) -> int:
    """Calculate number of days in the backtest range"""
    
    if not ctx.date_start or not ctx.date_end:
        return 0
    
    try:
        from datetime import datetime
        start_date = datetime.strptime(ctx.date_start, '%Y-%m-%d')
        end_date = datetime.strptime(ctx.date_end, '%Y-%m-%d')
        return (end_date - start_date).days
    except ValueError:
        return 0


if __name__ == "__main__":
    # Test hook
    test_ctx = HookContext(
        run_id="test_safety",
        run_path="./test_run",
        phase="analyzer",
        universe="binance:BTCUSDT,ETHUSDT,ADAUSDT",
        date_start="2024-01-01",
        date_end="2024-03-31",
        hook_name="before_backtest_loop"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Checks: {len(result.details.get('checks', []))}")
        print(f"Warnings: {len(result.details.get('warnings', []))}")