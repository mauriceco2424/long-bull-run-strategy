# Generate Trading Strategy Visualizations

---
description: Generate or improve run visualizations following best practices
argument-hint: [run_id plot_type]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-analyzer** agent to generate high-quality visualizations for trading strategy runs, following OHLCV visualization best practices and creating professional figures suitable for analysis and presentation.

## Visualization Parameters
$ARGUMENTS (run_id and optional plot_type: equity|symbols|trades|performance|all)

## Visualization Framework

### 1. Data Preparation & Analysis
**Data Loading:**
- Load run artifacts from `/data/runs/{run_id}/`
- Parse metrics.json for performance data
- Extract trades.csv for transaction analysis
- Process events.csv for signal timing
- Import series.csv for time series data
- Validate data completeness and integrity

**Data Processing:**
- Align timestamps across all data sources
- Calculate additional derived metrics
- Group trades by symbols and time periods
- Process event sequences for visualization
- Prepare color coding and intensity mappings

### 2. Main Equity Visualization
**Primary Equity Curve:**
- **Time Series Plot**: Clean, professional equity curve
- **Trade Bars**: Grouped by symbol with color intensity
  - Blues/greens for profitable trades (intensity = number of trades)
  - Reds/oranges for losing trades (intensity = number of trades)
  - Bar height represents PnL magnitude
  - Transparency shows confidence/trade count

**Side Panel Information:**
- Configuration hash and run metadata
- Headline performance statistics:
  - CAGR, Sortino, Sharpe ratios
  - Maximum drawdown and recovery
  - Number of trades and win rate
  - Average trade duration
  - Total exposure metrics

**Design Standards:**
- Professional color palette
- Clear axis labels and units
- Grid lines for readability
- Consistent font sizing
- Publication-quality resolution (300 DPI)
- Both PNG and SVG format outputs

### 3. Monitoring Subplot
**Narrow Time Series Panel:**
- **Monitored Count**: Line plot showing symbols under consideration
- **Open Trades Count**: Overlay showing active positions
- **Dual Y-axis**: If scales differ significantly
- **Color Coordination**: Match main plot color scheme
- **Trend Indicators**: Moving averages or trend lines if helpful

**Design Elements:**
- Compact vertical space usage
- Clear legend and labeling
- Synchronized time axis with main plot
- Gridlines for reference
- Professional styling consistency

### 4. Per-Symbol Analysis Charts
**Individual Symbol Visualizations:**
- **Candlestick Charts**: OHLCV data with proper scaling
- **Volume Bars**: Bottom panel with appropriate scaling
- **Event Overlays**: Vertical lines with color coding:
  - Grey: Filter pass events
  - Black: Buy signal generation
  - Blue: Take-profit signal
  - Green: Take-profit execution
  - Orange: Stop-loss signal
  - Red: Stop-loss execution

**Position Indicators:**
- **Open Trade Spans**: Shaded areas for position duration
- **Stacked Opacity**: Handle overlapping positions
- **Position Size Indication**: Line thickness or shading intensity
- **Entry/Exit Markers**: Clear price level indicators

**Event Timeline:**
- **Bottom Event Bar**: Monthly time axis with labels
- **Event Density**: Visual representation of signal frequency
- **Pattern Recognition**: Highlight recurring patterns or clusters

### 5. Performance Analysis Visualizations
**Risk-Return Analysis:**
- **Scatter Plots**: Risk vs return for different periods
- **Efficient Frontier**: If comparing multiple configurations
- **Rolling Performance**: Time-varying metrics
- **Drawdown Analysis**: Underwater curves and recovery periods

**Trade Analysis Charts:**
- **PnL Distribution**: Histogram of trade returns
- **Win/Loss Analysis**: Comparative analysis by time/symbol
- **Duration Analysis**: Trade holding period distributions
- **Size Analysis**: Position size vs performance correlation

### 6. Comparative Visualizations (Multi-Run)
**Performance Comparison:**
- **Equity Curve Overlays**: Multiple strategies on same chart
- **Performance Metrics**: Radar charts or bar comparisons
- **Risk-Return Scatter**: Efficient frontier analysis
- **Rolling Correlation**: Strategy correlation over time

## Visualization Best Practices Research

### Industry Standards Research
**OHLCV Visualization Standards:**
- Research current best practices from financial industry
- Review academic literature on financial data visualization
- Study professional trading platform designs
- Analyze Bloomberg, TradingView, and similar platforms
- Document color schemes and layout standards

**Accessibility and Clarity:**
- Color-blind friendly palettes
- High contrast for readability
- Consistent styling across all plots
- Clear legends and annotations
- Appropriate font sizes for different output media

### Technical Implementation
**Plotting Libraries:**
- Research matplotlib, plotly, bokeh capabilities
- Evaluate interactive vs static visualization trade-offs
- Consider performance for large datasets
- Assess customization flexibility
- Review export format support

**Professional Quality Standards:**
- 300 DPI resolution for publication
- Vector formats (SVG) for scalability
- Consistent branding and styling
- Print-friendly color schemes
- Professional typography

## Visualization Execution Protocol

### Phase 1: Research & Planning
1. **Best Practices Research**: Study current OHLCV visualization standards
2. **Data Assessment**: Analyze available data for visualization potential
3. **Layout Planning**: Design optimal chart layouts and arrangements
4. **Color Scheme Selection**: Choose professional, accessible color palettes
5. **Output Format Planning**: Determine required formats and resolutions

### Phase 2: Data Preparation
1. **Data Loading**: Import all relevant run artifacts
2. **Data Validation**: Check completeness and quality
3. **Processing Pipeline**: Clean and prepare data for visualization
4. **Derived Metrics**: Calculate additional visualization metrics
5. **Time Alignment**: Synchronize all time series data

### Phase 3: Visualization Generation
1. **Main Equity Plot**: Create primary performance visualization
2. **Monitoring Subplot**: Generate position and activity overlay
3. **Per-Symbol Charts**: Create individual symbol analysis
4. **Performance Analytics**: Generate risk-return and trade analysis
5. **Quality Assurance**: Validate all plots for accuracy and clarity

### Phase 4: Output Generation & Validation
1. **Multi-Format Export**: Generate PNG, SVG, and other required formats
2. **Resolution Validation**: Ensure publication-quality output
3. **Accessibility Check**: Verify color-blind accessibility
4. **Layout Validation**: Confirm professional appearance
5. **File Organization**: Save to appropriate `/figs/` directory

### Phase 5: Documentation & Research Updates
1. **Visualization Documentation**: Document plot specifications and rationale
2. **Best Practices Update**: Update visualization standards based on research
3. **Template Creation**: Generate reusable visualization templates
4. **Research Report**: Document findings and improvements made

## Expected Outputs

### High-Quality Visualizations
- **Main Equity Figure**: Professional equity curve with trade bars and stats panel
- **Monitoring Subplot**: Clean position and activity time series
- **Per-Symbol Charts**: Comprehensive symbol-level analysis with events
- **Performance Analytics**: Risk-return and trade distribution analysis
- **Multi-Format Files**: PNG (300 DPI), SVG, and other formats as needed

### Research Documentation
- **Best Practices Report**: Findings from OHLCV visualization research
- **Template Library**: Reusable chart templates and styling
- **Standards Documentation**: Updated visualization guidelines
- **Implementation Notes**: Technical details and lessons learned

### Quality Assurance
- **Visual Validation**: All charts reviewed for accuracy and clarity
- **Accessibility Confirmation**: Color-blind friendly verification
- **Professional Standards**: Publication-quality output validation
- **Consistency Check**: Styling consistency across all visualizations

The visualization process ensures professional, accurate, and insightful visual analysis of trading strategy performance while maintaining the highest standards of clarity and accessibility.