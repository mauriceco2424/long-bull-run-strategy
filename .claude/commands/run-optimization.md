# Execute Complete Optimization Workflow

---
description: Execute full optimization pipeline: optimize-run → analyze-optimization → evaluate-optimization with PDF report
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to execute the complete parameter optimization workflow by chaining the three optimization commands in sequence: `/optimize-run` → `/analyze-optimization` → `/evaluate-optimization`.

## Complete Optimization Pipeline

This command executes the full parameter optimization workflow automatically:

1. **`/optimize-run`** - Execute parameter sweep using optimization_config.json
2. **`/analyze-optimization`** - Process optimization study into parameter performance matrices
3. **`/evaluate-optimization`** - Evaluate parameter optimization and generate optimization study PDF report

## Prerequisites
- **Engine Built**: `/build-engine` must have been completed successfully
- **Optimization Configuration**: `optimization_config.json` must exist with complete parameter ranges and search specification
- **System Resources**: Sufficient memory and disk space for parameter sweep and analysis
- **Time Allocation**: Optimization studies can take significant time (hours for large parameter spaces)

## Workflow Execution

### Phase 1: Parameter Optimization Execution
- Execute `/optimize-run` command with optimization_config.json
- Run parameter sweep with chosen search method (grid/random/bayesian)
- Apply walk-forward validation and overfitting prevention
- Generate optimization study in `/data/optimization/{study_id}/`
- Create individual run directories for each parameter combination

### Phase 2: Optimization Analysis
- Execute `/analyze-optimization` on the completed optimization study
- Process all parameter combinations into comprehensive performance matrices
- Generate parameter robustness analysis and stability assessments
- Create professional optimization visualizations (3D surfaces, heatmaps)
- Apply statistical validation and significance testing

### Phase 3: Optimization Evaluation
- Execute `/evaluate-optimization` on the analyzed optimization study
- Evaluate parameter significance and detect overfitting
- Generate strategic parameter interpretation and insights
- Create professional LaTeX PDF optimization study report
- Provide specific parameter recommendations for different risk profiles

## Progress Reporting
- **Unified Pipeline Progress**: `Optimization workflow... ████████░░░░ 40% (Phase 1/3)`
- **Phase Indicators**: Clear indication of current workflow phase with detailed sub-progress
- **Parameter Sweep Progress**: Real-time tracking of parameter combinations completed
- **Overall ETA**: Combined time estimate for complete optimization workflow
- **Resource Monitoring**: Memory and disk usage tracking throughout

## Expected Outputs
**Complete Optimization Study Results:**
- **Optimization Directory**: `/data/optimization/{study_id}/` with all artifacts
  - Parameter performance matrices with statistical validation
  - Robustness analysis and stability assessments
  - Professional parameter landscape visualizations
  - Walk-forward validation results across time periods
- **Individual Runs**: Each parameter combination creates `/data/runs/{run_id}/`
- **PDF Optimization Report**: Professional parameter optimization study report
- **Parameter Recommendations**: Specific configurations for conservative/balanced/aggressive profiles
- **Registry Entry**: Study recorded in `/docs/optimization/optimization_registry.csv`

## Advanced Features
**Overfitting Prevention:**
- Statistical significance testing across all parameter combinations
- Walk-forward validation with multiple out-of-sample periods
- Parameter complexity limits and robustness requirements
- Data-snooping bias detection and warnings

**Search Method Support:**
- **Grid Search**: Exhaustive testing of all parameter combinations
- **Random Search**: Efficient sampling for large parameter spaces
- **Bayesian Optimization**: ML-guided search for optimal parameter regions

**Professional Reporting:**
- Parameter performance landscapes with optimal zones
- Statistical validation charts with confidence intervals
- Strategic parameter insights and market behavior analysis
- Implementation guidelines for parameter deployment

## Error Handling & Recovery
- **Phase Failure Recovery**: Detailed error reporting with specific optimization failure points
- **Partial Results**: Preserve completed parameter combinations if optimization study fails
- **Automatic Cleanup**: Clean up incomplete optimization artifacts on critical failures
- **Resume Capability**: Ability to resume interrupted optimization studies
- **Resource Exhaustion Handling**: Graceful handling of memory/disk space limitations

## Success Criteria
- Parameter optimization completes with sufficient successful combinations
- Statistical validation confirms parameter significance and rules out overfitting
- Professional optimization study PDF report generated successfully
- Parameter recommendations are actionable and risk-profile appropriate
- Optimization study properly registered with complete metadata

## Use Cases
**Perfect for:**
- **Complete Parameter Validation**: Full end-to-end parameter optimization study
- **Production Optimization**: Robust parameter selection for live trading
- **Research Studies**: Comprehensive analysis of parameter effectiveness
- **Automated Optimization**: Single command for complete parameter analysis

**When to Use Individual Commands Instead:**
- **Debugging Optimization**: When troubleshooting parameter sweep issues
- **Custom Analysis**: When you need specialized optimization analysis
- **Incremental Studies**: When building optimization studies incrementally
- **Performance Testing**: When testing optimization methodology changes

## Resource Requirements
- **Computation**: High CPU usage for parameter sweep execution
- **Memory**: Significant RAM for multiple concurrent parameter combinations
- **Storage**: Large disk space for optimization study artifacts
- **Time**: Can range from minutes to hours depending on parameter space size

## Command Execution
Execute the complete parameter optimization workflow chain with automatic error handling, overfitting prevention, and comprehensive progress reporting across all three phases.

Please execute the full optimization pipeline: `/optimize-run` → `/analyze-optimization` → `/evaluate-optimization`