# Plan Trading Strategy Development

---
description: Create comprehensive project plan and coordinate development cycle
argument-hint: [strategy_description] [--test]
model: opus
---

I need to use the **trading-orchestrator** agent to plan and coordinate a new trading strategy development cycle based on the validated strategy template.

**Strategy Source Selection:**
- **Default**: Plans development for `docs/SMR.md` (main strategy)
- **Test Mode**: If `--test` flag provided, plans development for `docs/test/test_SMR.md` (test strategy)

## Strategy Description
$ARGUMENTS

## Project Planning Tasks

### 1. **Complexity-Aware Development Plan Creation**
- **Read complexity assessment** from `/validate-strategy` output to determine planning depth
- **Complexity-Aware Planning Modes**:
  - **SIMPLE**: Streamlined template-based planning (research focus: implementation, target: 60s)
  - **MODERATE**: Standard comprehensive planning (current behavior, target: 90s) 
  - **COMPLEX**: Enhanced planning (extra research phase, risk analysis, target: 120s)
  - **ADVANCED**: Full comprehensive planning (extensive research, multiple validation rounds, target: 180s+)
- Create plan in `cloud/tasks/<task_id>.md` with complexity-appropriate depth:
  - Goals and KPIs focused on development milestones
  - Clear owners (Builder/Analyzer/Evaluator assignments)
  - Dependencies and prerequisites  
  - Quality gates and checkpoints (complexity-adjusted)
  - Milestones and checkpoints
  - Priority classification (P0/P1/P2/P3)
  - Ordered DAG of development tickets with inputs/outputs

### 2. **Prerequisites Verification**
- Confirm strategy template validation passed
- Check that all quality gates are ready
- **Strategy Source**: Use test strategy if `--test` flag provided, otherwise main strategy
- Verify EMR/SMR documentation is fresh and in sync
  - Latest ECN applied to EMR
  - Latest SDCN applied to SMR
  - ECL/SCL changelogs are current
- Ensure no conflicting runs are in progress
- Validate system resources and dependencies

### 3. **Task Coordination Setup**
- Generate unique task_id for this development cycle
- Set up state persistence in `cloud/state/<task_id>.json`
- Initialize DAG status tracking
- Create milestone checkpoints
- Set up progress monitoring framework

### 4. **Documentation Coordination**
- Ensure EMR (Engine Master Report) reflects current engine state
- Verify SMR (Strategy Master Report) will be updated from template
- Check that changelogs (ECL/SCL) are up to date
- Prepare for version bumps when changes occur
- Plan documentation handoff workflow

### 5. **Development Workflow Orchestration**
- Determine engine changes needed based on strategy requirements
- Plan data requirements and universe selection strategy
- Schedule analysis and evaluation phases
- Set up quality gate checkpoints between phases
- Coordinate agent assignments and responsibilities

### 6. **Complexity-Aware Risk Assessment & Research**
- **Simple Strategies**: Focus on implementation risks and basic validation
- **Moderate Strategies**: Standard risk assessment with common failure modes
- **Complex Strategies**: Enhanced risk analysis with additional research phase on advanced patterns
- **Advanced Strategies**: Comprehensive risk modeling with extensive research and multiple validation rounds
- Identify complexity-appropriate development risks and blockers
- Plan fallback strategies for failure modes specific to complexity level
- Set up monitoring and alert systems scaled to strategy sophistication
- Define escalation procedures for critical issues

## Expected Outputs
- Comprehensive development plan in `cloud/tasks/<task_id>.md`
- State tracking file in `cloud/state/<task_id>.json`
- Clear go/no-go decision for proceeding to `/build-engine`
- Development milestones and checkpoints
- Risk assessment with mitigation strategies
- Next steps with assigned owners

## Quality Gates Verified
- Strategy template validation completed successfully
- System prerequisites validated
- Documentation freshness confirmed
- Resource availability confirmed
- No conflicting operations in progress

Please use the trading-orchestrator agent to execute this comprehensive planning process and set up the development coordination framework for the validated strategy.