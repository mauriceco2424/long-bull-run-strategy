#!/usr/bin/env python3
"""
on_accounting_mismatch hook - P0 blocking
Critical safety hook - halt on accounting identity violations
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from ..lib.hook_context import HookContext, HookResult
from ..lib.anomaly_logger import log_anomaly


def execute(ctx: HookContext, mismatch_data: Dict[str, Any] = None) -> HookResult:
    """
    Handle accounting identity violations: Equity_{t+1} ≠ Equity_t + realizedPnL - fees
    
    This is a critical violation indicating bugs in position management,
    fee calculations, or equity tracking.
    """
    
    ctx.ensure_hook_dir()
    
    try:
        if mismatch_data is None:
            mismatch_data = {
                "expected_equity": "unknown",
                "actual_equity": "unknown", 
                "difference": "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Calculate severity based on mismatch size
        severity = _assess_accounting_severity(mismatch_data)
        
        # Log to anomaly registry
        log_anomaly(
            ctx=ctx,
            severity="P0",  # All accounting mismatches are critical
            component="analyzer",
            code="ACCOUNTING_MISMATCH",
            message=f"Accounting identity violation: expected {mismatch_data.get('expected_equity')}, got {mismatch_data.get('actual_equity')}, diff {mismatch_data.get('difference')}",
            path_hint=ctx.trades_path or ctx.series_path
        )
        
        # Generate violation report
        violation_report = {
            "run_id": ctx.run_id,
            "phase": ctx.phase,
            "detection_time": ctx.timestamp.isoformat() if ctx.timestamp else None,
            "violation_type": "accounting_mismatch",
            "severity": severity,
            "mismatch_data": mismatch_data,
            "config_hash": ctx.config_hash,
            "accounting_check": _perform_detailed_accounting_check(ctx, mismatch_data),
            "recommended_fixes": _get_accounting_fixes(mismatch_data)
        }
        
        # Write to violation files
        violation_file = os.path.join(ctx.run_path, "ACCOUNTING_VIOLATION.json")
        with open(violation_file, 'w') as f:
            json.dump(violation_report, f, indent=2)
        
        # Global registry
        registry_file = os.path.join("docs", "runs", "accounting_violations.jsonl")
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        
        with open(registry_file, 'a') as f:
            f.write(json.dumps(violation_report) + '\n')
        
        # Console alert
        print("\n" + "="*80)
        print("🚨 CRITICAL ALERT: ACCOUNTING MISMATCH DETECTED 🚨")
        print("="*80)
        print(f"Run ID: {ctx.run_id}")
        print(f"Expected Equity: {mismatch_data.get('expected_equity')}")
        print(f"Actual Equity: {mismatch_data.get('actual_equity')}")
        print(f"Difference: {mismatch_data.get('difference')}")
        print(f"Severity: {severity}")
        print("⚠️  ACCOUNTING IDENTITY VIOLATED - BACKTEST INVALID")
        print(f"📋 Report: {violation_file}")
        print("="*80 + "\n")
        
        return HookResult(
            success=False,
            message=f"CRITICAL: Accounting mismatch - {mismatch_data.get('difference', 'unknown')} difference",
            priority="P0",
            should_halt=True,
            details=violation_report
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"CRITICAL: Accounting mismatch detected but hook failed: {str(e)}",
            priority="P0", 
            should_halt=True
        )


def _assess_accounting_severity(mismatch_data: Dict[str, Any]) -> str:
    """Determine severity of accounting mismatch"""
    
    difference = mismatch_data.get('difference')
    if isinstance(difference, (int, float)):
        abs_diff = abs(difference)
        if abs_diff < 0.01:
            return "LOW"  # Rounding errors
        elif abs_diff < 1.0:
            return "MEDIUM" 
        else:
            return "HIGH"
    return "HIGH"  # Unknown = assume worst case


def _perform_detailed_accounting_check(ctx: HookContext, mismatch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform detailed accounting audit"""
    
    return {
        "identity_check": "FAILED",
        "possible_causes": [
            "Fee calculation error",
            "Position tracking bug",
            "Realized PnL calculation error",
            "Cash balance tracking issue",
            "Order execution accounting bug"
        ],
        "requires_investigation": True
    }


def _get_accounting_fixes(mismatch_data: Dict[str, Any]) -> List[str]:
    """Generate specific fix recommendations"""
    
    return [
        "1. HALT all trading operations immediately",
        "2. Audit fee calculation logic",
        "3. Verify position tracking accuracy",
        "4. Check realized PnL calculations",
        "5. Review cash balance updates",
        "6. Add accounting identity unit tests",
        "7. Implement continuous accounting validation"
    ]


if __name__ == "__main__":
    test_ctx = HookContext(
        run_id="test_accounting",
        run_path="./test_run", 
        phase="analyzer",
        hook_name="on_accounting_mismatch"
    )
    
    test_mismatch = {
        "expected_equity": 100000.0,
        "actual_equity": 99995.50,
        "difference": -4.50,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    result = execute(test_ctx, test_mismatch)
    print(f"Result: {result.success}")
    print(f"Should halt: {result.should_halt}")