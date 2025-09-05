#!/usr/bin/env python3
"""
after_registry_append hook - P2 nonblocking
Observability and notifications after registry update
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Provide observability and optional notifications after registry append
    
    Actions:
    - Console summary of run completion
    - Optional notifications (Telegram/Slack if configured)
    - Update lightweight status files
    - Release registry lock
    - Log completion metrics
    """
    
    ctx.ensure_hook_dir()
    actions = []
    
    try:
        # 1. Release registry lock (cleanup)
        lock_file = os.path.join("docs", "runs", "registry.lock")
        if os.path.exists(lock_file):
            try:
                # Verify this is our lock before removing
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data.get('run_id') == ctx.run_id:
                    os.remove(lock_file)
                    actions.append("Registry lock released")
                else:
                    actions.append(f"Lock belongs to different run: {lock_data.get('run_id')}")
            except (json.JSONDecodeError, OSError):
                # Force remove stale lock
                os.remove(lock_file)
                actions.append("Stale registry lock removed")
        else:
            actions.append("No registry lock to release")
        
        # 2. Generate console summary
        try:
            summary = _generate_run_summary(ctx)
            actions.append("Console summary generated")
            
            # Print to console (this is observability)
            print("\n" + "="*60)
            print("TRADING RUN COMPLETED")
            print("="*60)
            print(summary)
            print("="*60 + "\n")
            
        except Exception as e:
            actions.append(f"Console summary failed: {str(e)}")
        
        # 3. Update lightweight status file
        try:
            status_file = os.path.join("docs", "runs", "latest_status.json")
            status_data = {
                "latest_run_id": ctx.run_id,
                "completion_time": ctx.timestamp.isoformat() if ctx.timestamp else None,
                "phase": ctx.phase,
                "universe": ctx.universe,
                "date_range": f"{ctx.date_start} to {ctx.date_end}",
                "config_hash": ctx.config_hash[:8] if ctx.config_hash else "unknown"
            }
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
            actions.append(f"Status file updated: {status_file}")
            
        except Exception as e:
            actions.append(f"Status file update failed: {str(e)}")
        
        # 4. Optional notifications (if configured)
        notifications_sent = 0
        try:
            notifications_config = _load_notifications_config()
            
            if notifications_config:
                # Telegram notification
                if notifications_config.get('telegram', {}).get('enabled'):
                    if _send_telegram_notification(ctx, summary if 'summary' in locals() else "Run completed"):
                        notifications_sent += 1
                        actions.append("Telegram notification sent")
                    else:
                        actions.append("Telegram notification failed")
                
                # Slack notification  
                if notifications_config.get('slack', {}).get('enabled'):
                    if _send_slack_notification(ctx, summary if 'summary' in locals() else "Run completed"):
                        notifications_sent += 1
                        actions.append("Slack notification sent")
                    else:
                        actions.append("Slack notification failed")
            else:
                actions.append("No notification config found")
                
        except Exception as e:
            actions.append(f"Notifications failed: {str(e)}")
        
        # 5. Log completion metrics
        try:
            completion_log = {
                "run_id": ctx.run_id,
                "completed_at": ctx.timestamp.isoformat() if ctx.timestamp else None,
                "phase": ctx.phase,
                "actions_completed": len(actions),
                "notifications_sent": notifications_sent,
                "universe": ctx.universe,
                "config_hash": ctx.config_hash
            }
            
            completion_file = os.path.join("docs", "runs", "completion_log.jsonl")
            with open(completion_file, 'a') as f:
                f.write(json.dumps(completion_log) + '\n')
                
            actions.append("Completion logged")
            
        except Exception as e:
            actions.append(f"Completion logging failed: {str(e)}")
        
        # Write hook log
        log_data = {
            "hook": "after_registry_append",
            "status": "success",
            "actions_completed": len(actions),
            "notifications_sent": notifications_sent,
            "actions": actions,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return HookResult(
            success=True,
            message=f"Observability completed ({len(actions)} actions, {notifications_sent} notifications)",
            priority="P2",
            details={
                "actions": actions,
                "notifications_sent": notifications_sent
            }
        )
        
    except Exception as e:
        # This is P2 nonblocking, so we log but don't halt
        return HookResult(
            success=False,
            message=f"Observability partially failed: {str(e)}",
            priority="P2",
            details={
                "exception": str(e),
                "type": type(e).__name__,
                "actions_completed": len(actions) if 'actions' in locals() else 0
            }
        )


def _generate_run_summary(ctx: HookContext) -> str:
    """Generate a human-readable run summary"""
    summary_lines = [
        f"Run ID: {ctx.run_id}",
        f"Universe: {ctx.universe}",
        f"Date Range: {ctx.date_start} to {ctx.date_end}",
        f"Phase: {ctx.phase}",
        f"Config Hash: {ctx.config_hash[:8]}..." if ctx.config_hash else "Config Hash: unknown"
    ]
    
    # Try to load metrics for summary
    try:
        metrics_path = ctx.metrics_path or os.path.join(ctx.run_path, 'metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            if 'total_return' in metrics:
                summary_lines.append(f"Total Return: {metrics['total_return']:.2%}")
            if 'sharpe_ratio' in metrics:
                summary_lines.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            if 'total_trades' in metrics:
                summary_lines.append(f"Total Trades: {metrics['total_trades']}")
                
    except Exception:
        summary_lines.append("Metrics: unavailable")
    
    return "\n".join(summary_lines)


def _load_notifications_config() -> dict:
    """Load notifications configuration if it exists"""
    config_file = os.path.join("tools", "hooks", "config", "notifications.yaml")
    
    if not os.path.exists(config_file):
        return {}
    
    try:
        import yaml
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        # YAML not available, try JSON fallback
        json_config = config_file.replace('.yaml', '.json')
        if os.path.exists(json_config):
            with open(json_config, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return {}


def _send_telegram_notification(ctx: HookContext, message: str) -> bool:
    """Send notification via Telegram (placeholder implementation)"""
    # TODO: Implement actual Telegram bot notification
    # This would require bot token and chat ID from config
    return False


def _send_slack_notification(ctx: HookContext, message: str) -> bool:
    """Send notification via Slack (placeholder implementation)"""  
    # TODO: Implement actual Slack webhook notification
    # This would require webhook URL from config
    return False


if __name__ == "__main__":
    # Test hook with dummy context
    test_ctx = HookContext(
        run_id="test_run_123",
        run_path="./test_run",
        phase="registry", 
        universe="binance:BTCUSDT,ETHUSDT",
        date_start="2024-01-01",
        date_end="2024-01-31",
        config_hash="abc123def456",
        hook_name="after_registry_append"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Actions: {len(result.details.get('actions', []))}")
        print(f"Notifications: {result.details.get('notifications_sent', 0)}")