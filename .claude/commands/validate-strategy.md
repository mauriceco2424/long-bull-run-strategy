# Validate Strategy Template

---
description: Check strategy template completeness and parameter schema
argument-hint: [--test]
model: opus
---

I need to use the **trading-orchestrator** agent to validate that the strategy template is complete and ready for engine building.

**Strategy Source Selection:**
- **Default**: Validates `docs/SMR.md` (main strategy template)
- **Test Mode**: If `--test` flag provided, validates `docs/test/test_SMR.md` (test strategy)

## Strategy Template Validation Tasks

**Target File**: 
- If `--test` flag is provided in arguments: `docs/test/test_SMR.md`
- Otherwise: `docs/SMR.md` (following existing template structure)

### 1. **Required Sections Check**
- **Section 1a**: Strategy Description (Narrative) - filled with actual description
- **Section 2**: Entry Logic - complete with markers, parameters, conditions
- **Section 3**: Exit Logic - complete with markers, parameters, conditions
- **Section 4**: Portfolio & Risk Management - accounting mode and sizing chosen
- **Section 5**: Filters & Eligibility - data requirements and boundaries specified
- **Section 6**: Conflict Handling - clear precedence rules defined
- **Section 7**: Optional Extras - reviewed (can be empty)

### 2. **Parameter Schema Validation**
- All parameters have **specific values** or **valid ranges** defined
- Parameter types clearly specified (integer, float, string, etc.)
- No placeholder text or example values left unchanged
- Parameter descriptions are clear and actionable

### 3. **Strategy Logic Completeness**
- Entry conditions are **precise and executable** (not just examples)
- Exit conditions are **specific with clear precedence**
- Conflict handling rules are **explicitly defined**
- Execution timing is **clearly specified** (bar open/close)

### 4. **Market & Universe Definition**
- **Market/Universe** clearly defined (e.g., "binance_usdt", "crypto_majors")
- **Timeframe** specified (e.g., "1h", "4h", "1d")
- **Asset Selection** method specified
- **Date boundaries** for testing defined

### 5. **Checklist Completion**
- All checklist items at bottom of template are **ticked**
- No incomplete or pending items remain
- Template is ready for engine implementation

### 6. **Parameter Schema Export**
- Extract all parameters with their types and ranges
- Prepare parameter metadata for auto-generation system
- Validate parameter interdependencies

### 7. **Strategy Complexity Assessment**
- **Analyze SMR.md content** and calculate complexity score across multiple dimensions
- **Technical Indicators Complexity (0-4 points)**:
  - 0: No indicators or basic price data
  - 1: Single standard indicator (RSI, SMA, EMA)
  - 2: 2-3 standard indicators or 1 custom indicator
  - 3: 4+ indicators or multiple custom indicators  
  - 4: Complex indicators (ML, multi-timeframe)
- **Entry/Exit Logic Complexity (0-4 points)**:
  - 0: Single condition (e.g., "RSI < 30")
  - 1: 2 conditions with AND/OR
  - 2: 3-4 conditions or simple precedence rules
  - 3: 5+ conditions or complex precedence logic
  - 4: Dynamic conditions, ML-based, or algorithmic logic
- **Parameters Count (0-3 points)**:
  - 0: 1-2 parameters, 1: 3-5 parameters, 2: 6-10 parameters, 3: 10+ parameters
- **Portfolio Management Complexity (0-3 points)**:
  - 0: Fixed % equity, single position per symbol
  - 1: Multiple position sizes or basic risk targeting
  - 2: Volatility-adjusted sizing or position scaling
  - 3: Dynamic portfolio optimization or complex constraints
- **Market Scope Complexity (0-2 points)**:
  - 0: Single asset or small fixed list (<5 symbols)
  - 1: Asset universe 5-50 symbols or basic scanning
  - 2: Large universe (50+ symbols) or complex ranking/filtering
- **Determine complexity level**:
  - 0-3 points: **SIMPLE** (Target: 60s planning, 90s building)
  - 4-7 points: **MODERATE** (Target: 90s planning, 150s building) 
  - 8-12 points: **COMPLEX** (Target: 120s planning, 240s building)
  - 13+ points: **ADVANCED** (Target: 180s+ planning, 300s+ building)
- **Output assessment summary** with scoring breakdown and time targets

## Expected Outputs
- **PASS**: Strategy template complete, ready for `/plan-strategy`
- **FAIL**: Missing sections or incomplete parameters identified
- **Complexity Assessment**: Strategy complexity level with scoring breakdown and time targets
- Detailed validation report with specific issues and line numbers
- Parameter schema summary for engine building
- Recommendations for completing any missing sections

## Validation Criteria
The template passes validation only if:
- All required sections contain actual strategy-specific content
- All parameters have concrete values or valid ranges (no placeholders)
- Logic sections contain executable conditions (not examples)
- All checklist items are completed
- Parameter schema is consistent and complete

Please use the trading-orchestrator agent to perform thorough strategy template validation and report readiness for strategy development.