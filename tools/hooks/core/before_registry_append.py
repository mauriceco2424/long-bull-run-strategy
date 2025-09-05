#!/usr/bin/env python3
"""
before_registry_append hook - P0 blocking
Ensure CSV/lock integrity before appending to run registry
"""

import os
import csv
import json
import time
import fcntl
from pathlib import Path
from typing import List, Dict
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Validate registry integrity and acquire lock before appending
    
    Checks:
    - Registry file exists and is accessible
    - CSV headers are correct
    - No duplicate run_id already exists
    - Acquire exclusive lock for write operation
    """
    
    ctx.ensure_hook_dir()
    checks = []
    
    try:
        # Registry file paths
        registry_file = os.path.join("docs", "runs", "run_registry.csv")
        lock_file = os.path.join("docs", "runs", "registry.lock")
        
        # Ensure registry directory exists
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        
        # 1. Check if registry file exists, create with headers if not
        if not os.path.exists(registry_file):
            headers = [
                'run_id', 'config_hash', 'engine_version', 'universe', 
                'date_start', 'date_end', 'seed', 'status', 'total_return',
                'sharpe_ratio', 'max_drawdown', 'total_trades', 'start_time',
                'end_time', 'duration_minutes', 'notes'
            ]
            
            with open(registry_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            checks.append("Registry: created new file with headers")
        else:
            checks.append("Registry: file exists")
        
        # 2. Validate CSV structure and headers
        try:
            with open(registry_file, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Read header row
                
                expected_headers = [
                    'run_id', 'config_hash', 'engine_version', 'universe',
                    'date_start', 'date_end', 'seed', 'status', 'total_return',
                    'sharpe_ratio', 'max_drawdown', 'total_trades', 'start_time',
                    'end_time', 'duration_minutes', 'notes'
                ]
                
                # Check if we have at least the essential headers
                essential_headers = ['run_id', 'config_hash', 'status']
                missing_essential = [h for h in essential_headers if h not in headers]
                
                if missing_essential:
                    return HookResult(
                        success=False,
                        message=f"Registry missing essential headers: {missing_essential}",
                        priority="P0",
                        should_halt=True
                    )
                
                checks.append(f"Registry: valid headers ({len(headers)} columns)")
                
                # 3. Check for duplicate run_id
                duplicate_found = False
                row_count = 0
                for row in reader:
                    row_count += 1
                    if len(row) > 0 and row[0] == ctx.run_id:  # Assuming run_id is first column
                        duplicate_found = True
                        break
                
                if duplicate_found:
                    return HookResult(
                        success=False,
                        message=f"Duplicate run_id found in registry: {ctx.run_id}",
                        priority="P0",
                        should_halt=True
                    )
                
                checks.append(f"Registry: no duplicate run_id found ({row_count} existing records)")
                
        except (OSError, csv.Error) as e:
            return HookResult(
                success=False,
                message=f"Error reading registry file: {e}",
                priority="P0",
                should_halt=True
            )
        
        # 4. Acquire exclusive lock
        lock_acquired = False
        max_retries = 300  # 5 minutes with 1-second intervals
        retry_count = 0
        
        while not lock_acquired and retry_count < max_retries:
            try:
                # Try to create lock file exclusively
                lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                
                # Write lock info
                lock_info = {
                    "run_id": ctx.run_id,
                    "phase": ctx.phase,
                    "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None,
                    "pid": os.getpid()
                }
                
                os.write(lock_fd, json.dumps(lock_info, indent=2).encode())
                os.close(lock_fd)
                
                lock_acquired = True
                checks.append(f"Lock: acquired after {retry_count} retries")
                
                # Store lock file path for cleanup
                ctx.lock_file = lock_file
                
            except FileExistsError:
                # Lock exists, check if it's stale
                if os.path.exists(lock_file):
                    try:
                        lock_age = time.time() - os.path.getmtime(lock_file)
                        if lock_age > 600:  # 10 minutes - consider stale
                            os.remove(lock_file)
                            checks.append(f"Lock: removed stale lock (age: {lock_age:.1f}s)")
                            continue
                    except (OSError, FileNotFoundError):
                        pass
                
                retry_count += 1
                if retry_count % 30 == 0:  # Log every 30 seconds
                    checks.append(f"Lock: waiting... ({retry_count}/300 retries)")
                time.sleep(1)
            
            except OSError as e:
                return HookResult(
                    success=False,
                    message=f"Error acquiring registry lock: {e}",
                    priority="P0",
                    should_halt=True
                )
        
        if not lock_acquired:
            return HookResult(
                success=False,
                message=f"Failed to acquire registry lock after {max_retries} retries (5 minutes)",
                priority="P0", 
                should_halt=True
            )
        
        # 5. Validate we can write to the registry (test append)
        try:
            with open(registry_file, 'a') as f:
                # Just test that we can open for append, don't write anything yet
                pass
            checks.append("Registry: writable for append")
        except (OSError, PermissionError) as e:
            # Release lock before failing
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                except:
                    pass
            
            return HookResult(
                success=False,
                message=f"Registry file not writable: {e}",
                priority="P0",
                should_halt=True
            )
        
        # Write success log
        log_data = {
            "hook": "before_registry_append",
            "status": "success", 
            "lock_acquired": True,
            "lock_file": lock_file,
            "registry_file": registry_file,
            "checks": checks,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return HookResult(
            success=True,
            message=f"Registry ready for append (lock acquired, {len(checks)} checks passed)",
            priority="P0",
            details={
                "checks": checks,
                "lock_file": lock_file,
                "registry_file": registry_file
            }
        )
        
    except Exception as e:
        # Clean up lock if we created it
        lock_file = os.path.join("docs", "runs", "registry.lock")
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                if lock_data.get('run_id') == ctx.run_id:
                    os.remove(lock_file)
            except:
                pass
        
        return HookResult(
            success=False,
            message=f"Unexpected error in before_registry_append: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


if __name__ == "__main__":
    # Test hook with dummy context
    test_ctx = HookContext(
        run_id="test_run_123",
        run_path="./test_run",
        phase="registry",
        hook_name="before_registry_append"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    
    # Clean up test lock
    lock_file = os.path.join("docs", "runs", "registry.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print("Cleaned up test lock file")
        except:
            print("Could not clean up test lock file")