# Initialize

Transform the long-bull-run-strategy into a specific strategy project with **automated GitHub repository creation**, content customization, and Git setup. **Automatically reads strategy name from SMR.md**. Does NOT rename the folder - user handles that manually for reliability.

## Usage

```
/initialize
```

That's it! The command automatically:
1. Reads strategy name from `docs/SMR.md` 
2. Generates repository name (e.g., "RSI Momentum Strategy" → "rsi-momentum-strategy")
3. **Creates GitHub repository automatically** using GitHub CLI
4. Transforms all file contents with strategy names
5. Pushes initial commit to GitHub

**Note**: Folder renaming is done manually after initialization for reliability across all platforms.

## Prerequisites

1. **Git Bash Terminal** (required for GitHub CLI integration)
2. **GitHub CLI Authentication**: Run `gh auth login` first
3. **Update SMR.md**: Edit `docs/SMR.md` following `docs/guides/STRAT_TEMPLATE.md` format
4. **Set Strategy Name**: Change `**Name**: <Strategy Name>` to your actual strategy name

## Examples

```bash
# 1. Edit SMR.md with your strategy name
# **Name**: `RSI Momentum Strategy`

# 2. Run initialization
/initialize

# 3. Manually rename folder (more reliable than automatic)
cd ..
mv long-bull-run-strategy rsi-momentum-strategy
cd rsi-momentum-strategy

# 4. Open renamed workspace
code rsi-momentum-strategy.code-workspace
```

## Optional Override

```
/initialize "Custom Strategy Name" "custom-repo-name"
```

## What This Command Does

1. **Update Content**: Replaces all skeleton references with strategy names
2. **Customize Documentation**: Updates README, SMR.md, EMR.md with strategy info
3. **Rename Workspace File**: Updates workspace file to match strategy name
4. **Clean Skeleton Artifacts**: Removes all test files and skeleton-specific content:
   - Test configurations (`test_parameter_config.md`, `test_config.json`, `test_optimization_config.json`)
   - Test scripts (`run_test.py`, `test_optimization_simple.py`, `scripts/create_test_data.py`, `scripts/create_discrepancy_test.py`, `scripts/run_full_test_suite.py`)
   - Test data directories (`/data/test_runs/`, `/data/test_results/`, `/docs/test/`)
   - Test analysis scripts (`scripts/single_analysis/analyze_test*.py`, `scripts/single_analysis/detailed_test_report.py`)
   - Test evaluation scripts (`scripts/single_evaluation/evaluate_test.py`)
   - Test strategy implementation (`scripts/engine/rsi_mean_reversion_strategy.py`)
   - Test notices (`docs/notices/SER/SER_test_*.json`)
   - Skeleton metadata (`SKELETON_VERSION.md`)
   - Skeleton-specific tasks in `/cloud/tasks/` (including `test_strategy_*.md`)
   - Test documentation (`docs/TESTING.md` - framework validation guide)
5. **Create GitHub Repository**: Automatically creates repo using `gh repo create`
6. **Setup Git Branching**: Creates `main` and `develop` branches with proper structure
7. **Branch Protection**: Configures branch protection rules for safe development
8. **Initial Commit**: Pushes clean, production-ready codebase to both branches
9. **Generate Report**: Creates transformation report with next steps

**Not included**: Folder renaming (done manually for cross-platform reliability)

## Parameters

- **Strategy Display Name**: Human-readable name (e.g., "RSI Momentum Strategy")
- **Repo Name**: GitHub repository name (kebab-case, e.g., "rsi-momentum-strategy")

## Files Preserved After Transformation

The following essential framework components are kept:
- `.claude/` - All agents and commands for strategy development
- `scripts/engine/` - Engine framework (Builder will customize for your strategy)
- `scripts/analyzer/`, `scripts/single_analysis/`, `scripts/single_evaluation/` - Analysis pipeline
- `scripts/optimization/`, `scripts/opt_evaluation/` - Optimization pipeline
- `scripts/quiet_mode.py` - Output control utility
- `tools/` - All tools, hooks, and validators
- `docs/` - EMR, SMR, SCL, ECL, guides, schemas (test artifacts removed)
- `configs/` - Configuration templates
- `requirements.txt`, `.gitignore`, `README.md`, `CLAUDE.md` - Project essentials

## Output

- **GitHub Repository**: Automatically created with professional branching structure
- **Git Branches**: `main` (production) and `develop` (integration) branches created
- **Branch Protection**: Rules configured to prevent direct pushes to `main`
- Renamed workspace file: `{repo-name}.code-workspace`
- Updated all file contents with strategy names
- **Clean codebase**: All skeleton test artifacts removed
- Clean git repository with remote origin set
- Initial commit pushed to both branches
- Transformation report with next steps

## Next Steps After Initialization

**1. Manual Folder Renaming** (for reliability):
```bash
cd ..
mv long-bull-run-strategy your-strategy-name
cd your-strategy-name
code your-strategy-name.code-workspace
```

**2. Start Development on Feature Branch**:
```bash
# Create your first feature branch  
git checkout develop
git checkout -b feature/initial-parameters

# Continue with strategy development
/validate-setup && /validate-strategy && /plan-strategy && /build-engine
```

**Merge to Production When Ready**:
```bash
# After testing and validation
gh pr create --base develop --title "Initial strategy implementation"
# Review, test, then merge develop → main when stable
```

## Requirements

- **Git Bash terminal** (required for GitHub CLI)
- **GitHub CLI authenticated** (`gh auth login` completed)
- Must be run in a directory containing the long-bull-run-strategy content
- `docs/SMR.md` must exist and follow `docs/guides/STRAT_TEMPLATE.md` format
- Strategy name in SMR.md should not be the placeholder `<Strategy Name>`

## Automatic Features

- **GitHub Repository Creation**: Uses `gh repo create` to automatically create the repository
- **Professional Git Setup**: Creates `main` + `develop` branches with protection rules
- **Branch Protection**: Configures GitHub to require PRs for `main` branch changes
- **Content Transformation**: Updates all file contents with strategy names (folder renaming done manually)
- **Smart Name Generation**: Converts "RSI Momentum Strategy" → "rsi-momentum-strategy" 
- **Template Detection**: Validates SMR.md follows proper format
- **Complete Git Integration**: Creates repository, sets remote, pushes to both branches

This command is designed to be run immediately after:
1. Cloning skeleton content into a directory
2. Editing `docs/SMR.md` with your strategy specification following `docs/guides/STRAT_TEMPLATE.md`
3. Authenticating with GitHub CLI (`gh auth login`)