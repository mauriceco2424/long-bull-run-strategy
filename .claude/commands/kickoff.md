# Kickoff Trading Strategy Development

---
description: Initialize a new trading strategy development cycle
argument-hint: [strategy_description]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-orchestrator** agent to kickoff a new trading strategy development cycle.

## Strategy Description
$ARGUMENTS

## Tasks to Complete

1. **Plan the Pipeline**
   - Create a comprehensive plan in `cloud/tasks/<task_id>.md` with:
     - Goals and KPIs with measurable success criteria
     - Clear owners (Builder/Analyzer/Evaluator assignments)
     - Dependencies and prerequisites
     - Quality gates and checkpoints
     - Milestones with timelines
     - Priority classification (P0/P1/P2/P3)
     - Ordered DAG of tickets with inputs/outputs

2. **Verify Prerequisites**
   - Check that all quality gates are ready
   - Verify EMR/SMR documentation is fresh and in sync
   - Ensure no conflicting runs are in progress
   - Validate system resources and dependencies

3. **Initialize Task Tracking**
   - Generate unique task_id
   - Set up state persistence in `cloud/state/<task_id>.json`
   - Initialize DAG status tracking
   - Create milestone checkpoints

4. **Documentation Setup**
   - Ensure EMR (Engine Master Report) is current
   - Verify SMR (Strategy Master Report) reflects latest requirements
   - Check that changelogs (ECL/SCL) are up to date
   - Prepare for version bumps when changes occur

5. **Coordinate Next Steps**
   - Determine if this requires engine changes (Builder)
   - Plan data requirements and universe selection
   - Schedule analysis and evaluation phases
   - Set up quality gate checkpoints

Please use the trading-orchestrator agent to execute this kickoff process systematically, ensuring all gates are properly configured before allowing pipeline progression.