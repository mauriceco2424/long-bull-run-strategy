#!/usr/bin/env python3
"""
before_evaluator hook - P0 blocking
Ensure evaluator has what it needs and check for red flags from analyzer
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Validate readiness for evaluator and check for red flags
    
    Checks:
    - Required input files exist and are accessible
    - Manifest indicates successful analyzer completion
    - No critical red flags in events (lookahead, liquidity violations, accounting errors)
    - Metrics file contains required fields for evaluation
    """
    
    ctx.ensure_hook_dir()
    checks = []
    red_flags = []
    
    try:
        # Required inputs for evaluator
        required_paths = {
            'manifest': ctx.manifest_path or os.path.join(ctx.run_path, 'manifest.json'),
            'metrics': ctx.metrics_path or os.path.join(ctx.run_path, 'metrics.json'),
            'trades': ctx.trades_path or os.path.join(ctx.run_path, 'trades.csv'),
            'events': ctx.events_path or os.path.join(ctx.run_path, 'events.csv'),
            'series': ctx.series_path or os.path.join(ctx.run_path, 'series.csv')
        }
        
        # 1. Verify all required files exist and are readable
        for file_type, file_path in required_paths.items():
            if not os.path.exists(file_path):
                return HookResult(
                    success=False,
                    message=f"Required {file_type} file missing: {file_path}",
                    priority="P0",
                    should_halt=True
                )
            
            try:
                with open(file_path, 'r') as f:
                    f.read(1)  # Test readability
                checks.append(f"{file_type}: accessible")
            except (OSError, PermissionError) as e:
                return HookResult(
                    success=False,
                    message=f"Cannot read {file_type} file: {e}",
                    priority="P0", 
                    should_halt=True
                )
        
        # 2. Check manifest for analyzer completion status
        manifest_path = required_paths['manifest']
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check if analyzer completed successfully
            status = manifest.get('status', 'unknown')
            if status not in ['completed', 'success']:
                red_flags.append(f"Analyzer status: {status} (expected: completed/success)")
            else:
                checks.append(f"Analyzer status: {status}")
            
            # Check for any analyzer errors/warnings
            if 'errors' in manifest and manifest['errors']:
                red_flags.append(f"Analyzer reported {len(manifest['errors'])} errors")
            
            if 'warnings' in manifest and len(manifest.get('warnings', [])) > 10:
                red_flags.append(f"Analyzer reported {len(manifest['warnings'])} warnings (>10)")
                
        except (json.JSONDecodeError, KeyError) as e:
            return HookResult(
                success=False,
                message=f"Invalid or incomplete manifest: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 3. Scan events.csv for critical red flags
        events_path = required_paths['events']
        try:
            red_flag_events = []
            with open(events_path, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i > 1000:  # Limit scan to first 1000 events for performance
                        break
                    
                    event_type = row.get('event_type', '').lower()
                    
                    # Check for lookahead violations
                    if 'lookahead' in event_type or 'future_data' in event_type:
                        red_flag_events.append(f"Row {i+2}: {event_type}")
                    
                    # Check for liquidity violations  
                    if 'liquidity_violation' in event_type or 'impossible_fill' in event_type:
                        red_flag_events.append(f"Row {i+2}: {event_type}")
                    
                    # Check for accounting errors
                    if 'accounting_error' in event_type or 'balance_mismatch' in event_type:
                        red_flag_events.append(f"Row {i+2}: {event_type}")
            
            if red_flag_events:
                if len(red_flag_events) > 5:
                    return HookResult(
                        success=False,
                        message=f"Too many critical events detected: {len(red_flag_events)} violations",
                        priority="P0",
                        should_halt=True
                    )
                else:
                    red_flags.extend(red_flag_events)
            else:
                checks.append("Events: no critical violations detected in first 1000 rows")
                
        except Exception as e:
            return HookResult(
                success=False,
                message=f"Error scanning events for red flags: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 4. Validate metrics.json has required fields for evaluation
        metrics_path = required_paths['metrics']
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            required_metrics = [
                'total_return', 'sharpe_ratio', 'sortino_ratio', 
                'max_drawdown', 'total_trades', 'win_rate'
            ]
            
            missing_metrics = [metric for metric in required_metrics if metric not in metrics]
            if missing_metrics:
                return HookResult(
                    success=False,
                    message=f"Metrics missing required fields: {missing_metrics}",
                    priority="P0",
                    should_halt=True
                )
            
            # Check for suspicious metric values that might indicate problems
            suspicious = []
            
            # Unrealistically high Sortino ratio
            sortino = metrics.get('sortino_ratio', 0)
            if isinstance(sortino, (int, float)) and sortino > 5.0:
                suspicious.append(f"Sortino ratio: {sortino:.2f} (>5.0 suspicious)")
            
            # Zero drawdown with significant trading
            total_trades = metrics.get('total_trades', 0)
            max_dd = metrics.get('max_drawdown', 0)
            if total_trades > 10 and max_dd == 0:
                suspicious.append(f"Zero drawdown with {total_trades} trades (suspicious)")
            
            # Win rate outside realistic bounds
            win_rate = metrics.get('win_rate', 0)
            if isinstance(win_rate, (int, float)):
                if win_rate > 0.95 or win_rate < 0.05:
                    suspicious.append(f"Win rate: {win_rate:.2%} (outside 5%-95% bounds)")
            
            if suspicious:
                red_flags.extend(suspicious)
            
            checks.append(f"Metrics: all required fields present")
            
        except (json.JSONDecodeError, TypeError) as e:
            return HookResult(
                success=False,
                message=f"Error validating metrics: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 5. Check file sizes are reasonable (not empty, not too large)
        for file_type, file_path in required_paths.items():
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                return HookResult(
                    success=False,
                    message=f"{file_type} file is empty: {file_path}",
                    priority="P0",
                    should_halt=True
                )
            
            # Warn if files are suspiciously large (>100MB)
            if file_size > 100 * 1024 * 1024:
                red_flags.append(f"{file_type}: large file ({file_size/1024/1024:.1f}MB)")
        
        # Evaluate overall readiness
        if red_flags:
            # If we have red flags but they're not critical, continue with warning
            critical_flags = [flag for flag in red_flags if any(word in flag.lower() 
                            for word in ['lookahead', 'accounting_error', 'impossible_fill'])]
            
            if critical_flags:
                return HookResult(
                    success=False,
                    message=f"Critical red flags detected: {len(critical_flags)} violations",
                    priority="P0",
                    should_halt=True,
                    details={"critical_flags": critical_flags, "all_flags": red_flags}
                )
        
        # Write log
        log_data = {
            "hook": "before_evaluator",
            "status": "success",
            "checks_passed": len(checks),
            "red_flags": len(red_flags),
            "details": {
                "checks": checks,
                "red_flags": red_flags,
                "files_verified": list(required_paths.keys())
            },
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        message = f"Evaluator readiness validated ({len(checks)} checks passed)"
        if red_flags:
            message += f", {len(red_flags)} warnings noted"
        
        return HookResult(
            success=True,
            message=message,
            priority="P0",
            details={
                "checks": checks,
                "red_flags": red_flags
            }
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in before_evaluator: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


if __name__ == "__main__":
    # Test hook with dummy context
    test_ctx = HookContext(
        run_id="test_run",
        run_path="./test_run",
        phase="evaluator",
        hook_name="before_evaluator"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Red flags: {len(result.details.get('red_flags', []))}")