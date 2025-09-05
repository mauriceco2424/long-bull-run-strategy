#!/usr/bin/env python3
"""
after_evaluator hook - P1 blocking  
Act on evaluator decision (halt/rerun/pass)
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, Any
from ..lib.hook_context import HookContext, HookResult


def _append_to_decision_registry(ctx: HookContext, decision: str, decision_data: dict = None) -> None:
    """Append evaluator decision to the decision registry CSV"""
    decision_registry_path = os.path.join("docs", "runs", "decision_registry.csv")
    
    # Extract data from decision_data if provided
    mtc_method = decision_data.get('mtc_method', 'none') if decision_data else 'none'
    p_alpha = decision_data.get('p_alpha', 0.05) if decision_data else 0.05
    baseline_id = decision_data.get('baseline_id') if decision_data else None
    delta_sortino = decision_data.get('delta_sortino') if decision_data else None
    delta_maxdd = decision_data.get('delta_maxdd') if decision_data else None
    rationale_path = decision_data.get('rationale_path') if decision_data else None
    evaluator_version = decision_data.get('evaluator_version', 'v1.0') if decision_data else 'v1.0'
    
    # Create CSV row
    row = [
        ctx.run_id,
        ctx.timestamp.isoformat() if ctx.timestamp else '',
        decision,
        mtc_method,
        p_alpha,
        baseline_id or '',
        delta_sortino or '',
        delta_maxdd or '',
        rationale_path or '',
        evaluator_version
    ]
    
    # Append to CSV (create directory if needed)
    os.makedirs(os.path.dirname(decision_registry_path), exist_ok=True)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(decision_registry_path)
    
    with open(decision_registry_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header if file doesn't exist
            writer.writerow(['run_id', 'evaluated_at', 'decision', 'mtc_method', 'p_alpha', 
                           'baseline_id', 'delta_sortino', 'delta_maxdd', 'rationale_path', 'evaluator_version'])
        writer.writerow(row)


def execute(ctx: HookContext) -> HookResult:
    """
    Process evaluator decision and take appropriate action
    
    Decision handling:
    - halt: Raise P0 alert, block pipeline
    - rerun: Schedule follow-up run, continue with caution
    - pass: Continue to next phase
    """
    
    ctx.ensure_hook_dir() 
    actions = []
    
    try:
        # Look for evaluator decision file
        decision_file = os.path.join(ctx.run_path, 'evaluator_decision.json')
        
        if not os.path.exists(decision_file):
            # Check if evaluator completed by looking for standard outputs
            ser_file = os.path.join(ctx.run_path, 'SER.md')  # Strategy Evaluation Report
            if os.path.exists(ser_file):
                actions.append("Found SER.md, assuming evaluator completed successfully")
                decision = "pass"  # Default decision if no explicit decision file
            else:
                return HookResult(
                    success=False,
                    message="No evaluator decision found and no SER.md generated",
                    priority="P1",
                    should_rerun=True
                )
        else:
            # Read evaluator decision
            try:
                with open(decision_file, 'r') as f:
                    decision_data = json.load(f)
                
                decision = decision_data.get('decision', 'unknown').lower()
                confidence = decision_data.get('confidence', 'medium')
                reasoning = decision_data.get('reasoning', '')
                
                actions.append(f"Evaluator decision: {decision} (confidence: {confidence})")
                if reasoning:
                    actions.append(f"Reasoning: {reasoning[:100]}...")
                
            except (json.JSONDecodeError, KeyError) as e:
                return HookResult(
                    success=False,
                    message=f"Invalid evaluator decision format: {e}",
                    priority="P1",
                    should_rerun=True
                )
        
        # Act on the decision
        if decision == "halt":
            # Critical issues found - halt pipeline
            actions.append("HALT decision: blocking pipeline progression")
            
            # Log halt decision to special halt registry
            halt_log = {
                "run_id": ctx.run_id,
                "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None,
                "reason": reasoning if 'reasoning' in locals() else "Evaluator halt decision",
                "phase": ctx.phase,
                "config_hash": ctx.config_hash
            }
            
            halt_registry = os.path.join("docs", "runs", "halt_registry.jsonl")
            os.makedirs(os.path.dirname(halt_registry), exist_ok=True)
            
            with open(halt_registry, 'a') as f:
                f.write(json.dumps(halt_log) + '\n')
            
            # Log to decision registry
            _append_to_decision_registry(ctx, decision, decision_data if 'decision_data' in locals() else None)
            
            return HookResult(
                success=False,
                message=f"Evaluator HALT decision: {reasoning[:100] if 'reasoning' in locals() else 'Critical issues detected'}",
                priority="P0",  # Escalate to P0 for halt decisions
                should_halt=True,
                details={"decision": decision, "actions": actions}
            )
            
        elif decision == "rerun":
            # Issues found but not critical - schedule rerun
            actions.append("RERUN decision: flagging for follow-up execution")
            
            # Create rerun request
            rerun_request = {
                "original_run_id": ctx.run_id,
                "requested_at": ctx.timestamp.isoformat() if ctx.timestamp else None,
                "reason": reasoning if 'reasoning' in locals() else "Evaluator rerun recommendation",
                "config_hash": ctx.config_hash,
                "universe": ctx.universe,
                "date_range": f"{ctx.date_start} to {ctx.date_end}",
                "priority": "medium",
                "status": "pending"
            }
            
            rerun_queue = os.path.join("cloud", "state", "rerun_queue.jsonl")
            os.makedirs(os.path.dirname(rerun_queue), exist_ok=True)
            
            with open(rerun_queue, 'a') as f:
                f.write(json.dumps(rerun_request) + '\n')
            
            actions.append(f"Added rerun request to queue: {rerun_queue}")
            
            # Log to decision registry
            _append_to_decision_registry(ctx, decision, decision_data if 'decision_data' in locals() else None)
            
            return HookResult(
                success=True,  # Don't block current run
                message=f"Evaluator RERUN decision: follow-up scheduled",
                priority="P1",
                should_rerun=True,
                details={"decision": decision, "actions": actions, "rerun_queued": True}
            )
            
        elif decision == "pass":
            # All good - continue to next phase
            actions.append("PASS decision: proceeding to next phase")
            
            # Update run status to indicate evaluator approval
            status_update = {
                "run_id": ctx.run_id,
                "evaluator_status": "approved",
                "decision": decision,
                "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
            }
            
            status_file = os.path.join(ctx.run_path, "evaluator_status.json")
            with open(status_file, 'w') as f:
                json.dump(status_update, f, indent=2)
            
            # Log to decision registry
            _append_to_decision_registry(ctx, decision, decision_data if 'decision_data' in locals() else None)
            
            return HookResult(
                success=True,
                message="Evaluator PASS decision: approved for progression",
                priority="P1",
                details={"decision": decision, "actions": actions}
            )
            
        else:
            # Unknown decision
            actions.append(f"UNKNOWN decision: {decision}")
            
            # Log to decision registry (even unknown decisions should be tracked)
            _append_to_decision_registry(ctx, decision, decision_data if 'decision_data' in locals() else None)
            
            return HookResult(
                success=False,
                message=f"Unknown evaluator decision: {decision}",
                priority="P1",
                should_rerun=True,
                details={"decision": decision, "actions": actions}
            )
        
        # Write detailed log
        log_data = {
            "hook": "after_evaluator",
            "decision": decision,
            "actions": actions,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in after_evaluator: {str(e)}",
            priority="P1",
            should_rerun=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


if __name__ == "__main__":
    # Test hook with dummy context and decision file
    import tempfile
    import shutil
    
    test_dir = tempfile.mkdtemp()
    
    # Create test decision file
    decision = {
        "decision": "pass",
        "confidence": "high", 
        "reasoning": "All metrics within acceptable ranges, no red flags detected"
    }
    
    decision_file = os.path.join(test_dir, "evaluator_decision.json")
    with open(decision_file, 'w') as f:
        json.dump(decision, f)
    
    test_ctx = HookContext(
        run_id="test_run",
        run_path=test_dir,
        phase="evaluator",
        hook_name="after_evaluator"
    )
    
    try:
        result = execute(test_ctx)
        print(f"Result: {result.success}")
        print(f"Message: {result.message}")
        if result.details:
            print(f"Decision: {result.details.get('decision')}")
            print(f"Actions: {len(result.details.get('actions', []))}")
    finally:
        shutil.rmtree(test_dir)