#!/usr/bin/env python3
"""
before_analyzer_run hook - P0 blocking
Guard resources & preconditions before analyzer execution
"""

import os
import shutil
import json
from pathlib import Path
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Validate preconditions before analyzer run
    
    Checks:
    - Free disk space (min 2GB)
    - Available RAM (min 2GB) 
    - Cache availability (if offline mode)
    - Config hash present
    - Universe resolvable
    - Time range sanity
    """
    
    ctx.ensure_hook_dir()
    checks = []
    
    try:
        # 1. Check free disk space (minimum 2GB)
        free_space = shutil.disk_usage(ctx.run_path).free
        free_gb = free_space / (1024**3)
        if free_gb < 2.0:
            return HookResult(
                success=False,
                message=f"Insufficient disk space: {free_gb:.1f}GB < 2.0GB required",
                priority="P0",
                should_halt=True
            )
        checks.append(f"Disk space: {free_gb:.1f}GB available")
        
        # 2. Check available RAM (approximate via /proc/meminfo or system)
        try:
            import psutil
            available_ram = psutil.virtual_memory().available / (1024**3)
            if available_ram < 2.0:
                return HookResult(
                    success=False,
                    message=f"Insufficient RAM: {available_ram:.1f}GB < 2.0GB required", 
                    priority="P0",
                    should_halt=True
                )
            checks.append(f"RAM: {available_ram:.1f}GB available")
        except ImportError:
            checks.append("RAM: psutil not available, skipping check")
        
        # 3. Config hash validation
        if not ctx.config_hash:
            return HookResult(
                success=False,
                message="Config hash not provided in context",
                priority="P0", 
                should_halt=True
            )
        checks.append(f"Config hash: {ctx.config_hash[:8]}...")
        
        # 4. Universe validation
        if not ctx.universe:
            return HookResult(
                success=False,
                message="Universe not specified in context",
                priority="P0",
                should_halt=True  
            )
        checks.append(f"Universe: {ctx.universe}")
        
        # 5. Date range sanity check
        if not ctx.date_start or not ctx.date_end:
            return HookResult(
                success=False,
                message="Date range not specified (date_start/date_end missing)",
                priority="P0",
                should_halt=True
            )
            
        try:
            from datetime import datetime
            start_date = datetime.strptime(ctx.date_start, '%Y-%m-%d')
            end_date = datetime.strptime(ctx.date_end, '%Y-%m-%d')
            
            if end_date <= start_date:
                return HookResult(
                    success=False,
                    message=f"Invalid date range: {ctx.date_start} to {ctx.date_end}",
                    priority="P0",
                    should_halt=True
                )
                
            # Check if range is reasonable (not too long for performance)
            days = (end_date - start_date).days
            if days > 365 * 3:  # 3 years max
                return HookResult(
                    success=False,
                    message=f"Date range too long: {days} days > 1095 days max",
                    priority="P0", 
                    should_halt=True
                )
            checks.append(f"Date range: {days} days ({ctx.date_start} to {ctx.date_end})")
            
        except ValueError as e:
            return HookResult(
                success=False,
                message=f"Invalid date format: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 6. Cache availability check (if offline mode)
        if ctx.offline:
            # TODO: Implement cache availability check when cache system exists
            checks.append("Cache: offline mode, cache availability not yet implemented")
        
        # 7. Ensure run directory exists and is writable
        os.makedirs(ctx.run_path, exist_ok=True)
        test_file = os.path.join(ctx.run_path, "write_test.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            checks.append(f"Run path: {ctx.run_path} (writable)")
        except (OSError, PermissionError) as e:
            return HookResult(
                success=False,
                message=f"Run path not writable: {ctx.run_path} - {e}",
                priority="P0",
                should_halt=True
            )
        
        # Write success log
        log_data = {
            "hook": "before_analyzer_run",
            "status": "success",
            "checks_passed": len(checks),
            "details": checks,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return HookResult(
            success=True,
            message=f"All {len(checks)} precondition checks passed",
            priority="P0",
            details={"checks": checks}
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in before_analyzer_run: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


if __name__ == "__main__":
    # Test hook with dummy context
    test_ctx = HookContext(
        run_id="test_run",
        run_path="./test_run",
        phase="analyzer",
        config_hash="abc123",
        universe="binance:BTCUSDT,ETHUSDT",
        date_start="2024-01-01", 
        date_end="2024-01-31",
        hook_name="before_analyzer_run"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Details: {result.details}")