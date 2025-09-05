# Synchronize Master Documentation

---
description: Update EMR/SMR from latest notices and ensure docs freshness
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-orchestrator** agent to synchronize the master documentation (EMR/SMR) with the latest notices (ECN/SER/SDCN) and ensure all changelogs are properly updated.

## Documentation Synchronization Tasks

### 1. Notice Processing
**ECN (Engine Change Notice) Integration:**
- Scan `/docs/notices/ECN/` for unprocessed notices
- Apply engine changes to EMR (Engine Master Report)
- Update interface specifications and performance benchmarks
- Document hardware optimization settings and requirements
- Validate all ECN changes are semantically consistent

**SDCN (Strategy Definition Change Notice) Integration:**
- Process `/docs/notices/SDCN/` for strategy specification updates
- Apply changes to SMR (Strategy Master Report)
- Update parameter ranges, feature definitions, and logic specifications
- Ensure backward compatibility or document breaking changes
- Validate strategy definition completeness

### 2. Version Management
**Semantic Versioning Protocol:**
- Bump EMR version for engine changes: `emr-vX.Y.Z`
  - Major (X): Breaking interface changes or architectural shifts
  - Minor (Y): New features, optimizations, or performance improvements
  - Patch (Z): Bug fixes, documentation updates, minor tweaks

- Bump SMR version for strategy changes: `smr-vA.B.C`
  - Major (A): Fundamental strategy logic changes
  - Minor (B): New features, parameters, or mechanisms
  - Patch (C): Parameter tuning, minor logic adjustments

### 3. Changelog Updates
**ECL (Engine Changelog) Maintenance:**
- Append new entries for each processed ECN
- Include version number, timestamp, and change summary
- Document performance impact and hardware requirements
- Link to specific ECN files for detailed information
- Maintain chronological order (newest first)

**SCL (Strategy Changelog) Maintenance:**
- Append entries for each processed SDCN
- Include version changes and impact assessment
- Document parameter modifications and logic updates
- Reference evaluation reports that motivated changes
- Preserve complete audit trail

### 4. Cross-Reference Validation
**Consistency Checks:**
- Verify EMR and ECL version alignment
- Confirm SMR and SCL version consistency
- Check that all referenced notices exist and are complete
- Validate timestamp consistency across documents
- Ensure no orphaned or missing references

### 5. Git Integration
**Change Management:**
- Stage all documentation updates for commit
- Generate descriptive commit messages with version info
- Tag releases when major versions change
- Push updates to maintain team synchronization
- Preserve complete history for audit purposes

### 6. Quality Validation
**Documentation Quality Gates:**
- Verify all notices have been properly processed
- Check for completeness in version numbering
- Validate changelog format and consistency
- Ensure all cross-references are valid
- Confirm documentation freshness timestamps

### 7. State Persistence
**Pipeline State Updates:**
- Update `cloud/state/` files with new version information
- Record sync completion timestamps
- Clear "docs stale" flags in task tracking
- Update run registry version columns for future runs
- Persist sync status for pipeline coordination

## Synchronization Protocol

### Pre-Sync Validation
1. Check for uncommitted changes in documentation
2. Verify no active processes are modifying docs
3. Create backup of current documentation state
4. Validate notice file integrity and completeness

### Sync Execution
1. Process notices in chronological order
2. Apply changes atomically to prevent partial updates
3. Validate each change before committing to master docs
4. Update versions using semantic versioning rules
5. Append changelog entries with complete information

### Post-Sync Validation
1. Verify all notices have been processed
2. Check version consistency across all documents
3. Validate changelog completeness and ordering
4. Confirm git commits and tags are properly created
5. Update pipeline state and clear blocking flags

## Expected Outputs
- Updated EMR with latest engine specifications
- Updated SMR with current strategy definitions
- Complete ECL/SCL changelogs with new entries
- Properly bumped version numbers using semver
- Git commits with descriptive messages
- Version tags for major releases
- Updated pipeline state with sync completion status

This synchronization ensures the "docs fresh gate" passes and allows pipeline operations to proceed with confidence in documentation accuracy.