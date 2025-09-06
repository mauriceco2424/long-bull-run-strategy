# Execute Complete Single-Run Workflow

---
description: Execute full single-run pipeline: run → analyze → evaluate with PDF report
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to execute the complete single-run workflow by chaining the three single-run commands in sequence: `/run` → `/analyze-run` → `/evaluate-run`.

## Complete Single-Run Pipeline

This command executes the full single-run workflow automatically:

1. **`/run`** - Execute single backtest using parameter_config.md
2. **`/analyze-run`** - Process run data into metrics and visualizations  
3. **`/evaluate-run`** - Evaluate performance and generate PDF report

## Prerequisites
- **Engine Built**: `/build-engine` must have been completed successfully
- **Parameter Configuration**: `parameter_config.md` must exist with complete parameter specification
- **System Resources**: Sufficient memory and disk space for complete workflow

## Workflow Execution

### Phase 1: Single Backtest Execution
- Execute `/run` command with parameter_config.md
- Generate run artifacts in `/data/runs/{run_id}/`
- Validate successful completion before proceeding

### Phase 2: Run Analysis
- Execute `/analyze-run` on the generated run
- Process data into comprehensive metrics and visualizations
- Generate professional charts and validation reports

### Phase 3: Performance Evaluation
- Execute `/evaluate-run` on the analyzed run
- Generate strategic performance evaluation
- Create professional LaTeX PDF report

## Progress Reporting
- **Unified Pipeline Progress**: `Single-run workflow... ████████░░░░ 60% (Phase 2/3)`
- **Phase Indicators**: Clear indication of current workflow phase
- **Individual Command Progress**: Each command reports its own detailed progress
- **Overall ETA**: Combined time estimate for complete workflow

## Expected Outputs
**Complete Single-Run Results:**
- **Run Directory**: `/data/runs/{run_id}/` with all artifacts
  - Raw backtest data (trades, events, series)
  - Processed metrics and performance statistics
  - Professional visualizations ready for presentation
- **PDF Report**: Professional strategy evaluation report
- **Registry Entry**: Run recorded in `/docs/runs/run_registry.csv`
- **Evaluation Summary**: Strategic insights and recommendations

## Error Handling & Recovery
- **Phase Failure Recovery**: If any phase fails, detailed error reporting with specific failure point
- **Partial Results**: Preserve completed phases if later phases fail
- **Automatic Cleanup**: Clean up incomplete artifacts on critical failures
- **Manual Recovery**: Clear guidance on how to resume from specific failure points

## Success Criteria
- All three workflow phases complete successfully
- Professional PDF report generated and validated
- Run properly registered with complete metadata
- No critical validation errors in any phase
- Strategic evaluation provides actionable insights

## Use Cases
**Perfect for:**
- **Complete Strategy Testing**: Full end-to-end evaluation of parameter configuration
- **Automated Workflows**: Single command for complete strategy assessment
- **Quick Strategy Validation**: Fast path from parameters to final report
- **Production Runs**: Consistent, repeatable evaluation process

**When to Use Individual Commands Instead:**
- **Debugging**: When you need to inspect intermediate outputs
- **Iterative Development**: When making incremental changes
- **Custom Analysis**: When you need non-standard analysis approaches

## Command Execution
Execute the complete single-run workflow chain with automatic error handling and progress reporting across all three phases.

Please execute the full single-run pipeline: `/run` → `/analyze-run` → `/evaluate-run`