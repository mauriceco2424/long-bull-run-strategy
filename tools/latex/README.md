# LaTeX Report Generation System

This system generates professional PDF reports from trading strategy evaluation results using LaTeX templates.

## Overview

The LaTeX report system consists of:
- **Template**: `templates/strategy_report.tex` - Professional report template
- **Generator**: `generate_report.py` - Python script to compile reports
- **Integration**: Used by the trading-evaluator agent for `/evaluate-run` command

## Features

- **Professional Formatting**: Scientific-quality LaTeX typesetting
- **Comprehensive Content**: Executive summary, methodology, performance analysis, risk assessment
- **Automatic Chart Integration**: Includes all visualizations from analyzer
- **Template-Based**: Easy to customize and extend
- **Metadata Integration**: Automatically includes run configuration and technical details

## Requirements

### System Dependencies
- **LaTeX Distribution**: TeX Live (Linux/Mac) or MiKTeX (Windows)
- **Python 3.7+** with required packages

### LaTeX Packages Required
The template uses standard LaTeX packages:
- `graphicx` - Image inclusion
- `booktabs` - Professional tables
- `geometry` - Page layout
- `hyperref` - PDF links
- `xcolor` - Colors for financial data
- `subcaption` - Multiple figures

## Usage

### Command Line
```bash
# Generate report for a specific run
python tools/latex/generate_report.py --run-id run_20240315_strategy_v1

# Specify custom output path
python tools/latex/generate_report.py --run-id run_20240315_strategy_v1 --output my_report.pdf

# Check if LaTeX is available
python tools/latex/generate_report.py --check-latex
```

### Integration with Evaluator
The trading-evaluator agent automatically uses this system during `/evaluate-run`:

1. **Data Collection**: Loads metrics, trades, and figures from analyzer
2. **Template Population**: Fills in performance data and configuration
3. **Analysis Integration**: Adds strategic insights and evaluation results
4. **PDF Compilation**: Generates final professional report

## Report Structure

### 1. Executive Summary
- Performance rating (EXCELLENT/GOOD/ACCEPTABLE/POOR/FAILED)
- Key findings from evaluation
- Strategic recommendations

### 2. Strategy Methodology  
- Strategy description from template
- Parameters used in this run
- Market configuration and date range

### 3. Performance Analysis
- Key metrics table (CAGR, Sortino, Sharpe, etc.)
- Equity curve visualization
- Trade analysis charts

### 4. Risk Assessment
- Drawdown analysis
- Risk metrics and volatility
- Risk-adjusted performance evaluation

### 5. Strategic Insights
- Market behavior analysis
- Strategy effectiveness evaluation
- Parameter sensitivity analysis
- Market regime performance

### 6. Statistical Validation
- Significance testing results
- Realism assessment (lookahead, liquidity, execution)
- Confidence intervals for key metrics

### 7. Per-Symbol Analysis
- Individual symbol performance
- Charts for top/worst performing symbols

### 8. Conclusions and Recommendations
- Overall assessment
- Optimization opportunities
- Implementation considerations
- Next steps

### 9. Appendix
- Technical configuration
- Methodology notes

## Customization

### Template Modification
Edit `templates/strategy_report.tex` to:
- Change report structure
- Add new sections
- Modify formatting and styling
- Include additional charts or tables

### Data Integration
Modify `generate_report.py` to:
- Add new data sources
- Change metric calculations
- Customize chart integration
- Add new template variables

## Template Variables

The template uses `{{variable_name}}` syntax for substitution:

### Basic Metadata
- `{{strategy_name}}` - Strategy name
- `{{generation_date}}` - Report generation date
- `{{run_id}}` - Unique run identifier

### Performance Metrics
- `{{cagr}}` - Compound Annual Growth Rate
- `{{sortino}}` - Sortino ratio
- `{{sharpe}}` - Sharpe ratio
- `{{max_dd}}` - Maximum drawdown
- `{{win_rate}}` - Win rate percentage

### Analysis Content
- `{{executive_summary_text}}` - Executive summary
- `{{strategy_effectiveness_analysis}}` - Strategic analysis
- `{{market_behavior_analysis}}` - Market behavior insights
- `{{overall_assessment}}` - Final assessment

### Chart Paths
- `{{equity_chart_path}}` - Main equity curve
- `{{trade_analysis_chart_path}}` - Trade analysis chart
- `{{symbol_chart_1_path}}` - Top symbol chart

## Integration Points

### With Trading-Evaluator
The evaluator agent:
1. Calls `generate_report.py` with run ID
2. Adds strategic analysis text to template
3. Includes performance evaluation results
4. Generates final PDF for stakeholders

### With Trading-Analyzer  
The analyzer provides:
- Professional visualizations (PNG/SVG)
- Comprehensive metrics data
- Trade and event data
- Technical artifacts

## Error Handling

### Common Issues
- **LaTeX not installed**: System will provide installation instructions
- **Missing figures**: Uses fallback charts or placeholders
- **Compilation errors**: Displays LaTeX log for debugging
- **Template errors**: Clear error messages for troubleshooting

### Debugging
1. **Check LaTeX availability**: `--check-latex` flag
2. **Review log files**: Compilation errors show LaTeX logs
3. **Validate input data**: Ensure all required files exist
4. **Test template**: Verify template syntax and variables

## Best Practices

### For Template Development
- Test with sample data regularly
- Use consistent formatting throughout
- Include meaningful figure captions
- Maintain professional typography

### For Data Integration
- Validate all data before template substitution
- Handle missing data gracefully
- Use appropriate number formatting
- Include data quality checks

### For Report Quality
- Ensure all charts are high-resolution
- Verify all template variables are populated
- Include proper methodology documentation
- Test PDF output on different viewers

This system ensures that every strategy evaluation produces a professional, publication-ready report suitable for stakeholder review and decision-making.