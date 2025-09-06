# Create Trading Strategy Report

---
description: Generate professional LaTeX PDF report (alias for evaluate-run)
argument-hint: [run_id]
model: claude-3-5-sonnet-20241022
---

This is an **alias command** for `/evaluate-run` with a focus on report generation.

## Report Generation Focus
- **Run ID**: $ARGUMENTS (defaults to most recent run if not specified)

## Command Purpose
This command provides a clearer name when the primary goal is generating a professional PDF report rather than performing evaluation analysis. It executes exactly the same workflow as `/evaluate-run` but emphasizes the report generation aspect.

## What This Command Does
**Identical to `/evaluate-run`**: Performs comprehensive performance evaluation, strategic interpretation, and generates professional LaTeX PDF report.

### Primary Outputs
- **Professional LaTeX PDF Report**: Complete strategy analysis for stakeholders
- **Strategic insights and recommendations**: Business-ready analysis
- **Publication-ready document**: Professional formatting suitable for presentations

### Report Contents
- Executive summary with key findings
- Strategy methodology and parameters  
- Performance analysis with professional visualizations
- Risk assessment and strategic insights
- Evidence-based recommendations for next steps

## Usage Context
Use `/create-report` when:
- You want to emphasize report generation over evaluation analysis
- Creating documentation for stakeholders or presentations
- The primary goal is producing a professional PDF document
- You need a business-ready summary of strategy performance

Use `/evaluate-run` when:
- You want to emphasize the evaluation and analysis process
- The focus is on strategic assessment and decision-making
- You need comprehensive performance evaluation with recommendations

## Implementation
This command redirects to `/evaluate-run` with identical functionality, providing users with semantic clarity about their primary objective while maintaining the same comprehensive evaluation and reporting workflow.

**Note**: Both commands produce the same outputs - comprehensive evaluation AND professional PDF report. The choice between them is purely semantic based on what aspect you want to emphasize.