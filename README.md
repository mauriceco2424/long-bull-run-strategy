# Trading Strategy Framework Skeleton

A production-ready framework for building, backtesting, and optimizing trading strategies using Claude Code agents and a sophisticated pipeline architecture.

## 🚀 Quick Start

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/mauriceco2424/trading_bot_skeleton.git
   cd trading_bot_skeleton
   pip install -r requirements.txt
   python tools/validate_setup.py
   ```

2. **Create Your Strategy**:
   Write a strategy specification (.md file) with your trading rules, entry/exit logic, and parameters.

3. **Build and Test**:
   ```bash
   /kickoff "Your strategy description"
   /build-run configs/your_config.json your_universe 2021-01-01:2023-12-31
   /evaluate your_run_id
   ```

## 📋 What This Skeleton Provides

### 🤖 **7 Specialized Agents**

**Common Agents:**
- **trading-orchestrator**: Coordinates pipeline, manages quality gates, handles documentation
- **trading-builder**: Implements backtest engines, optimizes performance, writes ECNs

**Single-Run Agents:**
- **trading-single-runner**: Executes individual backtests with specific parameters
- **trading-single-analyzer**: Processes single run data, generates artifacts and visualizations
- **trading-single-evaluator**: Evaluates single-run performance and generates PDF reports

**Optimization Agents:**
- **trading-optimization-runner**: Executes parameter sweeps with walk-forward analysis
- **trading-optimization-analyzer**: Processes optimization studies into parameter performance matrices
- **trading-optimization-evaluator**: Evaluates parameter optimization results and generates optimization reports

### ⚡ **Streamlined Command System**

**Setup & Planning (4 commands):**
| Command | Purpose |
|---------|---------|
| `/validate-setup` | Validate framework setup and dependencies |
| `/validate-strategy` | Validate strategy specification |
| `/plan-strategy` | Plan strategy development approach |
| `/build-engine` | Build trading engine and generate parameter template |

**Single-Run Path (3 commands):**
| Command | Purpose |
|---------|---------|
| `/run` | Execute single backtest with parameter_config.md |
| `/analyze-run` | Process single run data into metrics and visualizations |
| `/evaluate-run` | Evaluate single-run performance and generate PDF report |

**Optimization Path (3 commands):**
| Command | Purpose |
|---------|---------|
| `/optimize-run` | Execute parameter sweep with optimization_config.json |
| `/analyze-optimization` | Process optimization study into parameter performance matrices |
| `/evaluate-optimization` | Evaluate parameter optimization and generate optimization report |

### 🔧 **Production Hook System**
- **6 core hooks** with P0/P1/P2 priorities
- Resource validation, artifact integrity, accounting checks
- Configurable timeouts and error handling
- Safety hooks for lookahead and accounting validation

### 📚 **Documentation Framework**
- **EMR/SMR**: Engine and Strategy Master Reports with versioning
- **ECL/SCL**: Append-only changelogs
- **ECN/SER/SDCN**: Change notices and evaluation reports
- JSON schemas for all data structures

## 🏗️ Architecture

### **Directory Structure**
```
├── .claude/                    # Claude Code configuration
│   ├── agents/                # 7 specialized agents
│   └── commands/              # 10 streamlined commands
├── docs/                      # Authoritative documentation
│   ├── runs/                  # Run registry and results
│   └── schemas/               # JSON schemas
├── configs/                   # Strategy configurations
├── tools/hooks/               # Hook system
│   ├── core/                  # Essential hooks
│   ├── lib/                   # Hook infrastructure
│   └── config/                # Hook configuration
├── cloud/                     # State management
│   ├── tasks/                 # Task planning
│   └── state/                 # Runtime state
└── data/                      # Run data (not committed)
    ├── runs/                  # Backtest results
    └── sandbox/               # Development data
```

### **Dual Workflow Paths**

**Single-Run Workflow:**
1. **Setup** → `/validate-setup` → `/validate-strategy` → `/plan-strategy` → `/build-engine`
2. **Execute** → `/run` (uses parameter_config.md)
3. **Analyze** → `/analyze-run` (process data + visualizations)
4. **Evaluate** → `/evaluate-run` (performance evaluation + PDF report)

**Parameter Optimization Workflow:**
1. **Setup** → Same as single-run setup
2. **Optimize** → `/optimize-run` (uses optimization_config.json for parameter sweeps)
3. **Analyze** → `/analyze-optimization` (parameter performance matrices)
4. **Evaluate** → `/evaluate-optimization` (parameter interpretation + optimization report)

### **Quality Gates**
- **Docs Fresh Gate**: EMR/SMR in sync with latest changes
- **Pre-run Gates**: Tests pass, no conflicting runs
- **Post-run Gates**: Artifacts complete, anomalies flagged

## 🎯 Usage Examples

### **Single-Run Strategy Development**
```bash
/validate-setup
/validate-strategy
/plan-strategy
/build-engine
/run
/analyze-run
/evaluate-run
```

### **Parameter Optimization Study**
```bash
/validate-setup
/validate-strategy  
/plan-strategy
/build-engine
# Create optimization_config.json with parameter ranges
/optimize-run
/analyze-optimization
/evaluate-optimization
```

## 🔒 Safety & Validation

- **No-lookahead enforcement**: Features use data ≤ t for actions at t+1
- **Accounting integrity**: Rigorous P&L tracking with fees/slippage
- **Deterministic execution**: Seeded operations for reproducibility
- **Statistical validation**: Multiple-testing corrections, overfitting detection
- **Realism checks**: Liquidity, slippage, trade density validation

## 📊 Output Artifacts

Each backtest run produces:
- `manifest.json`: Run metadata and hashes
- `metrics.json`: Performance statistics (CAGR, Sortino, Sharpe, MaxDD, etc.)
- `trades.csv`: Individual trade records with fees and P&L
- `events.csv`: Strategy events and signals
- `series.csv`: Time series data (equity curve, positions, etc.)
- `figs/`: Professional visualizations

## 🛠️ Customization

### **Adding New Strategies**
1. Create strategy specification (.md)
2. Use `/kickoff` to plan implementation
3. Framework builds everything automatically

### **Extending Hooks**
Add custom hooks in `tools/hooks/extended/` with proper priority and error handling.

### **Custom Agents**
Extend agent capabilities by modifying `.claude/agents/` configurations.

## 📈 Performance

- **Optimized for speed**: Processes 1-year, 300-symbol universe in <5 minutes
- **Memory efficient**: Configurable caching with resource profiling
- **Hardware-aware**: Auto-configures based on system capabilities
- **Incremental computation**: Monotone gate shortcuts for faster iterations

## 🤝 Contributing

This is a skeleton framework. Customize for your specific needs:
- Add domain-specific features
- Extend hook system for your workflows  
- Modify agents for specialized strategies
- Add custom validation rules

## 📝 License

MIT License - Use freely for your trading strategy development.

---

**Ready to build your next profitable strategy?** 

Run `python validate_setup.py` to verify your setup, then start with `/kickoff "Your strategy idea"`!