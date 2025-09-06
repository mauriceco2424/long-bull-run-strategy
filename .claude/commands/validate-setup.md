# Validate Trading System Setup

---
description: Check system requirements, dependencies, and data sources
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-orchestrator** agent to validate that all system prerequisites are met before strategy development.

## System Validation Tasks

### 1. **System Requirements Check**
- Verify available RAM (≥4GB recommended for backtesting)
- Check available disk space for data storage and artifacts
- Validate Python environment and version compatibility
- Confirm required packages are installed

### 2. **Dependencies Validation**
- Check trading framework dependencies (pandas, numpy, etc.)
- Verify progress bar libraries (tqdm, rich, progressbar2)
- Confirm LaTeX installation for report generation
- Validate visualization libraries (matplotlib, plotly)

### 3. **Data Sources & Cache**
- Verify data source connections (APIs, local data)
- Check cache availability and integrity
- Validate data format compatibility
- Confirm market data access permissions

### 4. **Framework Structure**
- Verify `/docs/` directory structure exists
- Check for required template files
- Validate hook system configuration
- Confirm Git repository is properly initialized

### 5. **Quality Gates**
- Test hook system functionality
- Verify progress reporting framework
- Check file permission and write access
- Validate version control integration

## Expected Outputs
- **PASS**: All prerequisites met, system ready for strategy development
- **FAIL**: Missing dependencies or configuration issues identified
- Detailed report of any issues found with resolution steps
- System capability summary (hardware specs, available resources)

Please use the trading-orchestrator agent to perform comprehensive system validation and report readiness status.