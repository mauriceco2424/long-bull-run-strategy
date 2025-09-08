# Trading Strategy Visualization Best Practices

## Overview

This document outlines the professional visualization standards implemented in our trading strategy framework, based on research into scientific publishing and quantitative finance best practices.

## Key Principles

### 1. **Research-Based Design**
- **No Dual-Axis Confusion**: Avoid dual-axis charts that can mislead through scale manipulation
- **Visual Clarity First**: Prioritize clear visual communication over cramming metrics into plots  
- **Separation of Concerns**: Plots for visual insight, LaTeX reports for detailed metrics
- **Progressive Enhancement**: Basic → Enhanced → Advanced visualization levels

### 2. **Professional Quality Standards**
- **Vector Graphics Priority**: PDF format for LaTeX reports (scalable, crisp text)
- **Raster Fallback**: PNG at 300+ DPI for HTML reports when PDF unavailable
- **Colorblind-Friendly**: Accessible color palettes throughout
- **Publication-Ready**: Professional typography and layout

## Default Visualization Architecture

### 3-Panel Stacked Layout (Always Generated)

#### **Panel 1: Main Equity Chart (70% height)**
- Primary equity curve (thick line, prominent color)
- Benchmark comparison curve (thin line, muted color) 
- Smart time axis with auto-detected optimal spacing:
  - <90 days: daily ticks ("%m-%d")
  - <365 days: weekly ticks ("%m-%d") 
  - <1095 days: monthly ticks ("%Y-%m")
  - 3+ years: quarterly ticks ("%Y-%m")
- Subtle background shading for winning/losing periods
- Professional typography, no metric cramming

#### **Panel 2: Drawdown Analysis (20% height)**
- Inverted area chart showing % drawdown from peaks
- Red fill going down from 0% baseline
- Maximum drawdown period highlighting with annotations
- Same time axis as equity panel for perfect alignment

#### **Panel 3: Trade Activity Summary (10% height)**
- Daily/weekly trade frequency or win rate aggregation
- Clean bar chart design avoiding visual clutter
- Consistent styling with main chart theme

### Enhanced Visualization (Template-Configurable)

- **Per-Symbol OHLCV Charts**: Candlestick + volume with event overlays
- **Event Marker System**: 
  - Grey: filter pass, Black: buy signal
  - Blue: TP signal, Green: TP sell
  - Orange: SL signal, Red: SL sell
- **Trade Period Visualization**: Shaded spans for open positions
- **Professional Quality**: Vector PDF + 300 DPI PNG formats

## Template Configuration

### Strategy Template Integration

Templates can specify visualization preferences in Section 7:

```markdown
## 7) Visualization Configuration (Optional)

### 7.1 Visualization Level
- **Basic**: Default 3-panel layout (always generated)
- **Enhanced**: Basic + per-symbol candlestick charts  
- **Advanced**: Enhanced + custom strategy visualizations

### 7.2 Display Options  
- **Benchmark Symbol**: SPY | QQQ | BTC | custom (default: SPY)
- **Per-Symbol Analysis**: yes | no (default: no)
- **Trade Markers**: all | major | none (default: major)
- **Time Period Shading**: yes | no (default: yes)
```

## File Format Strategy

### LaTeX Reports (PDF Priority)
- **Primary**: PDF figures for vector graphics
- **Benefit**: Scalable, crisp text, perfect for scientific publishing
- **No DPI needed**: Vector format scales infinitely

### HTML Reports (PNG Fallback)  
- **Secondary**: PNG figures at 300+ DPI for web display
- **Benefit**: Universal compatibility, fast loading
- **Quality**: Publication-ready print quality

### Auto-Detection Logic
```python
image_ext = '.pdf' if latex_available else '.png'
```

## Implementation Details

### File Naming Convention
- Main chart: `strategy_performance.{pdf,png}`
- Symbol charts: `symbol_{symbol_name}.{pdf,png}`
- Both formats generated automatically

### Smart Time Axis Logic
```python
if total_days < 90: daily_ticks, format="%m-%d"
elif total_days < 365: weekly_ticks, format="%m-%d"  
elif total_days < 1095: monthly_ticks, format="%Y-%m"
else: quarterly_ticks, format="%Y-%m"
```

### Professional Styling
- Font: Arial/DejaVu Sans (sans-serif)
- DPI: 300 for PNG, vector for PDF
- Colors: Colorblind-friendly palette
- Layout: Tight, clean spacing

## Quality Gates

### Visual Standards Checklist
- [ ] No dual-axis charts (visual confusion)
- [ ] Vector PDF + raster PNG formats generated
- [ ] Colorblind-friendly color palette
- [ ] Professional typography and spacing
- [ ] Smart time axis scaling applied
- [ ] Clear visual hierarchy maintained

### Integration Standards  
- [ ] LaTeX template uses PDF figures
- [ ] HTML fallback uses PNG figures
- [ ] Consistent naming conventions
- [ ] Template configuration respected
- [ ] Professional report integration

## Research References

Based on analysis of scientific publishing best practices:

1. **Vector vs Raster**: "Vector formats like PDF are infinitely better than PNG for graphs, illustrations built by software"
2. **LaTeX Integration**: "When using pdfLaTeX, choose PDF as output format for easy document inclusion"  
3. **Dual-Axis Warning**: "Skip dual‑axis line charts. Two different scales on one graph mislead"
4. **Professional Quality**: "300-600 DPI for printing, higher is better but filesize increases"

## Future Enhancements

### When Real Data Available
- Performance optimization with large datasets
- Real-world edge case handling  
- Visual scaling with actual trade densities
- Benchmark data integration accuracy

### Advanced Features (Roadmap)
- Interactive HTML visualizations
- Real-time performance monitoring
- Custom indicator overlays
- Multi-timeframe analysis

---

*This document reflects current best practices as of implementation. Updates should maintain research-based standards and professional quality requirements.*