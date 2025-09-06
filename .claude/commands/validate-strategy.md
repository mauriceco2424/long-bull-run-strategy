# Validate Strategy Template

---
description: Check strategy template completeness and parameter schema
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-orchestrator** agent to validate that the strategy template (STRAT_TEMPLATE.md) is complete and ready for engine building.

## Strategy Template Validation Tasks

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

## Expected Outputs
- **PASS**: Strategy template complete, ready for `/plan-strategy`
- **FAIL**: Missing sections or incomplete parameters identified
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