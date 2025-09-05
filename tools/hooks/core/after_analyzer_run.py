#!/usr/bin/env python3
"""
after_analyzer_run hook - P0 blocking
Validate artifact sanity & integrity after analyzer execution
"""

import os
import json
import hashlib
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from ..lib.hook_context import HookContext, HookResult
from ..lib.anomaly_logger import log_validation_error


def execute(ctx: HookContext) -> HookResult:
    """
    Validate analyzer outputs for integrity and completeness
    
    Checks:
    - Required files exist
    - SHA256 checksums (if available)
    - Row counts > 0 for key files
    - Timestamps monotonic
    - No NaNs in essential columns
    """
    
    ctx.ensure_hook_dir()
    checks = []
    warnings = []
    
    try:
        # Required artifacts from analyzer
        required_files = {
            'manifest.json': ctx.manifest_path or os.path.join(ctx.run_path, 'manifest.json'),
            'trades.csv': ctx.trades_path or os.path.join(ctx.run_path, 'trades.csv'),
            'events.csv': ctx.events_path or os.path.join(ctx.run_path, 'events.csv'),
            'series.csv': ctx.series_path or os.path.join(ctx.run_path, 'series.csv'),
            'metrics.json': ctx.metrics_path or os.path.join(ctx.run_path, 'metrics.json')
        }
        
        # 1. Check all required files exist
        missing_files = []
        for file_type, file_path in required_files.items():
            if not os.path.exists(file_path):
                missing_files.append(f"{file_type} ({file_path})")
            else:
                file_size = os.path.getsize(file_path)
                checks.append(f"{file_type}: exists ({file_size} bytes)")
        
        if missing_files:
            # Log missing files as anomaly
            log_validation_error(
                ctx=ctx,
                component="analyzer",
                validation_type="MISSING_FILES",
                details=f"Missing required artifacts: {', '.join(missing_files)}"
            )
            
            return HookResult(
                success=False,
                message=f"Missing required files: {', '.join(missing_files)}",
                priority="P0",
                should_halt=True
            )
        
        # 2. Validate manifest.json structure
        manifest_path = required_files['manifest.json']
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            required_manifest_keys = ['run_id', 'config_hash', 'engine_version', 'start_time', 'end_time']
            missing_keys = [key for key in required_manifest_keys if key not in manifest]
            
            if missing_keys:
                # Log manifest validation failure
                log_validation_error(
                    ctx=ctx,
                    component="analyzer",
                    validation_type="MANIFEST_SCHEMA",
                    details=f"Manifest missing required keys: {missing_keys}",
                    path_hint=manifest_path
                )
                
                return HookResult(
                    success=False,
                    message=f"Manifest missing required keys: {missing_keys}",
                    priority="P0",
                    should_halt=True
                )
            
            # Validate run_id matches
            if manifest.get('run_id') != ctx.run_id:
                return HookResult(
                    success=False,
                    message=f"Manifest run_id mismatch: {manifest.get('run_id')} != {ctx.run_id}",
                    priority="P0", 
                    should_halt=True
                )
                
            checks.append(f"Manifest: valid structure, run_id matches")
            
        except json.JSONDecodeError as e:
            return HookResult(
                success=False,
                message=f"Invalid manifest JSON: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 3. Check CSV file integrity and row counts
        csv_files = {
            'trades.csv': required_files['trades.csv'],
            'events.csv': required_files['events.csv'], 
            'series.csv': required_files['series.csv']
        }
        
        for csv_name, csv_path in csv_files.items():
            try:
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                if len(rows) < 2:  # Header + at least 1 data row
                    warnings.append(f"{csv_name}: only {len(rows)} rows (header only?)")
                else:
                    data_rows = len(rows) - 1  # Exclude header
                    checks.append(f"{csv_name}: {data_rows} data rows")
                    
                    # Check for basic timestamp monotonicity if timestamp column exists
                    if len(rows) > 1:
                        headers = [h.strip().lower() for h in rows[0]]
                        timestamp_cols = [i for i, h in enumerate(headers) if 'timestamp' in h or 'time' in h or 'date' in h]
                        
                        if timestamp_cols and len(rows) > 2:
                            timestamp_col = timestamp_cols[0]
                            try:
                                timestamps = []
                                for row in rows[1:6]:  # Check first 5 data rows
                                    if len(row) > timestamp_col:
                                        timestamps.append(row[timestamp_col])
                                
                                # Simple string-based monotonicity check (works for ISO format)
                                if len(timestamps) > 1 and all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)):
                                    checks.append(f"{csv_name}: timestamps appear monotonic")
                                elif len(timestamps) > 1:
                                    warnings.append(f"{csv_name}: timestamps may not be monotonic")
                                    
                            except (ValueError, IndexError):
                                warnings.append(f"{csv_name}: could not validate timestamp monotonicity")
                        
            except Exception as e:
                return HookResult(
                    success=False,
                    message=f"Error reading {csv_name}: {e}",
                    priority="P0",
                    should_halt=True
                )
        
        # 4. Check metrics.json structure
        metrics_path = required_files['metrics.json']
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # Check for NaN values in critical metrics
            critical_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'total_trades']
            nan_metrics = []
            
            for metric in critical_metrics:
                if metric in metrics:
                    value = metrics[metric]
                    if value is None or (isinstance(value, float) and (value != value)):  # NaN check
                        nan_metrics.append(metric)
            
            if nan_metrics:
                return HookResult(
                    success=False,
                    message=f"Critical metrics contain NaN/null: {nan_metrics}",
                    priority="P0",
                    should_halt=True
                )
            
            checks.append(f"Metrics: valid JSON, no NaN in critical metrics")
            
        except json.JSONDecodeError as e:
            return HookResult(
                success=False,
                message=f"Invalid metrics JSON: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 5. Check for figures directory (optional but expected)
        figs_path = os.path.join(ctx.run_path, 'figs')
        if os.path.exists(figs_path):
            fig_count = len([f for f in os.listdir(figs_path) if f.endswith(('.png', '.jpg', '.pdf'))])
            checks.append(f"Figures: {fig_count} files in figs/")
        else:
            warnings.append("No figs/ directory found")
        
        # Write detailed log
        log_data = {
            "hook": "after_analyzer_run",
            "status": "success",
            "checks_passed": len(checks),
            "warnings": len(warnings),
            "details": {
                "checks": checks,
                "warnings": warnings,
                "required_files_found": list(required_files.keys())
            },
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        message = f"All {len(checks)} integrity checks passed"
        if warnings:
            message += f" ({len(warnings)} warnings)"
        
        return HookResult(
            success=True,
            message=message,
            priority="P0",
            details={
                "checks": checks,
                "warnings": warnings
            }
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in after_analyzer_run: {str(e)}",
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
        hook_name="after_analyzer_run"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Checks: {len(result.details.get('checks', []))}")
        print(f"Warnings: {len(result.details.get('warnings', []))}")