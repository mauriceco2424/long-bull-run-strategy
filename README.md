# Trading Strategy Framework Skeleton

A production-ready framework for building, backtesting, and optimizing trading strategies using Claude Code agents and a sophisticated pipeline architecture.

## 🚀 Quick Start

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/mauriceco2424/trading_bot_skeleton.git
   cd trading_bot_skeleton
   pip install -r requirements.txt
   python validate_setup.py
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

### 🤖 **4 Specialized Agents**
- **trading-orchestrator**: Coordinates pipeline, manages quality gates, handles documentation
- **trading-builder**: Implements backtest engines, optimizes performance, writes ECNs
- **trading-analyzer**: Executes backtests, generates artifacts, validates results
- **trading-evaluator**: Assesses performance, ranks strategies, makes decisions

### ⚡ **12 Slash Commands**
| Command | Purpose |
|---------|---------|
| `/kickoff` | Start new strategy development cycle |
| `/build-run` | Build engine and execute backtest |
| `/analyze-run` | Process data into canonical outputs |
| `/evaluate` | Assess results and decide next steps |
| `/status` | Check pipeline state and gates |
| `/sync-docs` | Update documentation from notices |
| `/validate-gates` | Verify prerequisites |
| `/test-engine` | Run comprehensive test suite |
| `/optimize-engine` | Profile and improve performance |
| `/validate-run` | Check run integrity |
| `/compare-runs` | Compare multiple strategies |
| `/research` | Investigate topics |
| `/visualize` | Generate professional charts |

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
│   ├── agents/                # 4 specialized agents
│   └── commands/              # 12 slash commands
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

### **Workflow**
1. **Plan** (`/kickoff`) → Create comprehensive development plan
2. **Build** (`/build-run`) → Implement engine and execute backtest  
3. **Analyze** → Process results into canonical artifacts
4. **Evaluate** → Assess performance and decide next steps
5. **Iterate** → Optimize based on evaluation feedback

### **Quality Gates**
- **Docs Fresh Gate**: EMR/SMR in sync with latest changes
- **Pre-run Gates**: Tests pass, no conflicting runs
- **Post-run Gates**: Artifacts complete, anomalies flagged

## 🎯 Usage Examples

### **New Strategy Development**
```bash
/kickoff "Momentum strategy with volatility filters for crypto majors"
/validate-gates
/build-run configs/momentum_v1.json crypto_top20 2022-01-01:2024-01-01
/evaluate run_20241205_momentum_v1
```

### **Strategy Optimization**
```bash
/optimize-engine caching
/compare-runs baseline_run optimized_run_v1 optimized_run_v2
/research "momentum indicator effectiveness in crypto markets"
```

### **Analysis and Visualization**
```bash
/analyze-run configs/strategy.json binance_usdt 2023-01-01:2023-12-31
/visualize run_20241205_analysis all
/validate-run run_20241205_analysis
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