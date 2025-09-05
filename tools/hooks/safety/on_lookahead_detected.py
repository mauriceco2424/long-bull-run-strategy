#!/usr/bin/env python3
"""
on_lookahead_detected hook - P0 blocking
Critical safety hook - immediately halt pipeline on lookahead violations
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from ..lib.hook_context import HookContext, HookResult
from ..lib.anomaly_logger import log_anomaly


def execute(ctx: HookContext, evidence: Dict[str, Any] = None) -> HookResult:
    """
    Handle detection of lookahead bias in trading strategy
    
    This is a critical safety violation that must immediately halt the pipeline.
    Lookahead bias can lead to unrealistic backtest results and false confidence.
    
    Args:
        evidence: Dictionary containing evidence of lookahead violation
    """
    
    ctx.ensure_hook_dir()
    
    try:
        # Default evidence if not provided
        if evidence is None:
            evidence = {
                "violation_type": "unknown",
                "location": "not specified",
                "description": "Lookahead violation detected",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Ensure required fields exist
        evidence.setdefault('violation_type', 'unknown')
        evidence.setdefault('location', 'not specified')
        evidence.setdefault('description', 'Lookahead violation detected')
        evidence.setdefault('timestamp', datetime.utcnow().isoformat())
        evidence.setdefault('severity', 'critical')
        
        # Log to anomaly registry
        log_anomaly(
            ctx=ctx,
            severity="P0",
            component="analyzer",
            code="LOOKAHEAD_VIOLATION",
            message=f"Lookahead violation: {evidence.get('description')} at {evidence.get('location')}",
            path_hint=evidence.get('location')
        )
        
        # Generate detailed violation report
        violation_report = {
            "run_id": ctx.run_id,
            "phase": ctx.phase,
            "detection_time": ctx.timestamp.isoformat() if ctx.timestamp else None,
            "config_hash": ctx.config_hash,
            "universe": ctx.universe,
            "date_range": f"{ctx.date_start} to {ctx.date_end}",
            "evidence": evidence,
            "impact_assessment": _assess_lookahead_impact(evidence),
            "recommended_actions": _get_lookahead_remediation_steps(evidence)
        }
        
        # Write violation to multiple locations for visibility
        
        # 1. Run-specific violation file
        violation_file = os.path.join(ctx.run_path, "LOOKAHEAD_VIOLATION.json")
        with open(violation_file, 'w') as f:
            json.dump(violation_report, f, indent=2)
        
        # 2. Global violation registry
        violation_registry = os.path.join("docs", "runs", "lookahead_violations.jsonl")
        os.makedirs(os.path.dirname(violation_registry), exist_ok=True)
        
        registry_entry = {
            **violation_report,
            "logged_at": datetime.utcnow().isoformat()
        }
        
        with open(violation_registry, 'a') as f:
            f.write(json.dumps(registry_entry) + '\n')
        
        # 3. Critical alerts log
        alert_log = os.path.join("docs", "runs", "critical_alerts.jsonl")
        alert_entry = {
            "alert_type": "LOOKAHEAD_VIOLATION",
            "run_id": ctx.run_id,
            "severity": "CRITICAL",
            "message": f"Lookahead violation detected: {evidence.get('description')}",
            "evidence_location": violation_file,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_immediate_attention": True
        }
        
        with open(alert_log, 'a') as f:
            f.write(json.dumps(alert_entry) + '\n')
        
        # 4. Console alert (immediate visibility)
        print("\n" + "="*80)
        print("🚨 CRITICAL ALERT: LOOKAHEAD VIOLATION DETECTED 🚨")
        print("="*80)
        print(f"Run ID: {ctx.run_id}")
        print(f"Phase: {ctx.phase}")
        print(f"Violation Type: {evidence.get('violation_type')}")
        print(f"Location: {evidence.get('location')}")
        print(f"Description: {evidence.get('description')}")
        print(f"Detection Time: {evidence.get('timestamp')}")
        print("-" * 80)
        print("⚠️  PIPELINE HALTED - BACKTEST RESULTS ARE INVALID")
        print("⚠️  DO NOT PROCEED UNTIL VIOLATION IS FIXED")
        print(f"📋 Detailed report: {violation_file}")
        print("="*80 + "\n")
        
        # 5. Mark run as invalid
        run_status = {
            "status": "INVALID_LOOKAHEAD",
            "marked_at": datetime.utcnow().isoformat(),
            "violation_evidence": evidence,
            "can_proceed": False,
            "requires_fix": True
        }
        
        status_file = os.path.join(ctx.run_path, "run_status.json")
        with open(status_file, 'w') as f:
            json.dump(run_status, f, indent=2)
        
        # Write hook log
        log_data = {
            "hook": "on_lookahead_detected",
            "status": "violation_logged",
            "violation_type": evidence.get('violation_type'),
            "location": evidence.get('location'),
            "severity": "critical",
            "pipeline_halted": True,
            "files_written": [
                violation_file,
                violation_registry,
                alert_log,
                status_file
            ],
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Return critical failure
        return HookResult(
            success=False,
            message=f"CRITICAL: Lookahead violation detected - {evidence.get('description')}",
            priority="P0",
            should_halt=True,
            details={
                "violation_type": evidence.get('violation_type'),
                "location": evidence.get('location'),
                "evidence": evidence,
                "violation_file": violation_file,
                "impact": violation_report["impact_assessment"],
                "remediation": violation_report["recommended_actions"]
            }
        )
        
    except Exception as e:
        # Even if logging fails, we must halt the pipeline
        emergency_log = {
            "emergency": "LOOKAHEAD_DETECTION_HOOK_FAILED",
            "run_id": ctx.run_id,
            "original_evidence": evidence,
            "hook_error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            emergency_file = os.path.join(ctx.run_path, "EMERGENCY_LOOKAHEAD_ALERT.json")
            with open(emergency_file, 'w') as f:
                json.dump(emergency_log, f, indent=2)
        except:
            pass
        
        return HookResult(
            success=False,
            message=f"CRITICAL: Lookahead detected but hook failed: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"hook_error": str(e), "original_evidence": evidence}
        )


def _assess_lookahead_impact(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Assess the potential impact of the lookahead violation"""
    
    violation_type = evidence.get('violation_type', '').lower()
    
    impact_levels = {
        'future_price_access': 'SEVERE - Results completely unrealistic',
        'signal_timing': 'HIGH - Entry/exit timing compromised', 
        'feature_calculation': 'HIGH - Feature integrity compromised',
        'data_leakage': 'SEVERE - Information from future leaked',
        'execution_timing': 'MEDIUM - Execution assumptions violated',
        'unknown': 'HIGH - Unknown scope requires investigation'
    }
    
    impact_level = 'HIGH'
    for violation_key, level in impact_levels.items():
        if violation_key in violation_type:
            impact_level = level
            break
    
    return {
        "impact_level": impact_level,
        "reliability_compromised": True,
        "results_validity": "INVALID",
        "recommended_action": "HALT_AND_FIX",
        "rerun_required": True,
        "confidence_in_results": 0.0
    }


def _get_lookahead_remediation_steps(evidence: Dict[str, Any]) -> List[str]:
    """Generate specific remediation steps based on violation type"""
    
    violation_type = evidence.get('violation_type', '').lower()
    location = evidence.get('location', '')
    
    base_steps = [
        "1. IMMEDIATELY HALT pipeline execution",
        "2. Review and fix the code/logic causing lookahead",
        "3. Add unit tests to prevent similar violations",
        "4. Rerun backtest after fixes are implemented",
        "5. Verify no other lookahead violations exist"
    ]
    
    specific_steps = []
    
    if 'future_price' in violation_type:
        specific_steps.extend([
            "• Audit all price data access patterns",
            "• Ensure features only use data t and earlier",
            "• Check for shifted/forward-looking data alignment"
        ])
    
    if 'signal_timing' in violation_type:
        specific_steps.extend([
            "• Review signal generation timing logic",
            "• Ensure signals generate at time t for action at t+1",
            "• Audit order execution timing assumptions"
        ])
    
    if 'feature_calculation' in violation_type:
        specific_steps.extend([
            "• Audit feature calculation windows",
            "• Check for rolling window edge cases",
            "• Verify feature availability timing"
        ])
    
    if location:
        specific_steps.append(f"• Focus investigation on: {location}")
    
    return base_steps + specific_steps


if __name__ == "__main__":
    # Test hook with sample violation
    test_ctx = HookContext(
        run_id="test_lookahead",
        run_path="./test_run",
        phase="analyzer",
        universe="binance:BTCUSDT",
        date_start="2024-01-01",
        date_end="2024-01-31",
        config_hash="test123",
        hook_name="on_lookahead_detected"
    )
    
    test_evidence = {
        "violation_type": "future_price_access",
        "location": "feature_engine.py:line_245",
        "description": "Price data from t+1 used in feature calculation at time t",
        "code_snippet": "price_tomorrow = data.iloc[i+1]['close']  # VIOLATION",
        "severity": "critical"
    }
    
    result = execute(test_ctx, test_evidence)
    print(f"Result: {result.success}")
    print(f"Should halt: {result.should_halt}")
    print(f"Message: {result.message}")