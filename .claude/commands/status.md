# Trading Pipeline Status Check

---
description: Check current pipeline state and provide actionable next steps
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-orchestrator** agent to assess the current pipeline state, check all quality gates, and provide a comprehensive status update with specific next steps.

## Status Assessment Areas

### 1. Documentation Freshness Review
**EMR/SMR Synchronization:**
- Check if latest ECNs have been applied to EMR
- Verify latest SDCNs are reflected in SMR
- Confirm ECL/SCL changelogs are up to date
- Validate version numbers are properly bumped
- Review timestamp consistency across documents

### 2. Quality Gates Status
**Gate Validation Checklist:**

- **Docs Fresh Gate**: 
  - ✓ Latest ECN/SDCN applied
  - ✓ EMR/SMR versions bumped
  - ✓ ECL/SCL appended

- **Pre-run Gates**:
  - ✓ Unit tests passing
  - ✓ Golden-set parity verified
  - ✓ Small-integration tests pass
  - ✓ Validators operational
  - ✓ No conflicting runs detected

- **Post-run Gates**:
  - ✓ Artifacts complete
  - ✓ Run registry updated
  - ✓ Anomalies properly escalated

### 3. Active Run Status
**Current Execution State:**
- Check for running backtests and their progress
- Identify any failed or stalled runs
- Review resource utilization and conflicts
- Assess queue status and priority ordering
- Validate run_id uniqueness and directory availability

### 4. Resource & Dependency Check
**System Readiness:**
- Verify system resource availability (RAM, disk space, CPU)
- Check data source connectivity and cache status
- Validate configuration files and dependencies
- Assess hardware profile and optimization settings
- Review lockfile status and potential deadlocks

### 5. Task Tracking Review
**Pipeline Coordination:**
- Review active tasks in `cloud/tasks/`
- Check state persistence in `cloud/state/`
- Validate DAG progression and milestone status
- Identify blocked or overdue tasks
- Assess owner assignments and responsibilities

### 6. Version Control & Documentation
**Change Management:**
- Review pending changes in EMR/SMR
- Check for uncommitted documentation updates
- Validate notice generation (ECN/SER/SDCN)
- Assess version tagging and release readiness
- Review changelog completeness

## Status Report Format

### Executive Summary
- **Pipeline State**: [READY/BLOCKED/RUNNING/FAILED]
- **Current Phase**: [BUILD/RUN/ANALYZE/EVALUATE/IDLE]
- **Priority Issues**: [Count and severity of blocking issues]
- **Next Action**: [Specific next step required]

### Detailed Findings
1. **Documentation Status**: 
   - EMR version: emr-vX.Y.Z (last updated: timestamp)
   - SMR version: smr-vA.B.C (last updated: timestamp)
   - Changelog status: [FRESH/STALE] 
   - Pending notices: [count and types]

2. **Quality Gates**: 
   - [PASS/FAIL] for each gate with specific issues
   - Blocking issues with severity and owner assignment

3. **Active Operations**:
   - Running tasks with progress and ETA
   - Resource utilization and conflicts
   - Queue status and priority ordering

4. **Immediate Actions Required**:
   - Prioritized list of specific tasks
   - Owner assignments for each action
   - Dependencies and prerequisites
   - Estimated completion timelines

### Recommendations
- **Immediate**: Actions needed now to unblock progress
- **Short-term**: Tasks for next development cycle
- **Long-term**: Strategic improvements and optimizations

## Output
The orchestrator will provide a structured status report with clear action items, owner assignments, and priority classification to ensure smooth pipeline operation and progression.