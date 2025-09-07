# Initialize

Transform the trading_bot_skeleton into a specific strategy project with proper naming, GitHub repository setup, and file customization. **Automatically reads strategy name from SMR.md**.

## Usage

```
/initialize
```

That's it! The command automatically:
1. Reads strategy name from `docs/SMR.md` 
2. Generates repository name (e.g., "RSI Momentum Strategy" → "rsi-momentum-strategy")
3. Transforms all files and folders accordingly

## Prerequisites

1. **Update SMR.md**: Edit `docs/SMR.md` following `docs/guides/STRAT_TEMPLATE.md` format
2. **Set Strategy Name**: Change `**Name**: <Strategy Name>` to your actual strategy name

## Examples

```bash
# 1. Edit SMR.md with your strategy name
# **Name**: `RSI Momentum Strategy`

# 2. Run initialization
/initialize

# Done! Everything is automatically named and configured
```

## Optional Override

```
/initialize "Custom Strategy Name" "custom-repo-name"
```

## What This Command Does

1. **Rename Files**: Updates workspace file to match strategy name
2. **Update Content**: Replaces all skeleton references with strategy names
3. **Customize Documentation**: Updates README, SMR.md, EMR.md with strategy info
4. **Git Repository**: Initializes new repository with clean commit history
5. **Generate Report**: Creates transformation report with next steps

## Parameters

- **Strategy Display Name**: Human-readable name (e.g., "RSI Momentum Strategy")
- **Repo Name**: GitHub repository name (kebab-case, e.g., "rsi-momentum-strategy")

## Output

- Renamed workspace file: `{repo-name}.code-workspace`
- Updated all file contents with strategy names
- Clean git repository ready for GitHub
- Transformation report with next steps

## Next Steps After Initialization

1. Create GitHub repository: https://github.com/new
2. Add remote and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/{auto-generated-repo-name}.git
   git push -u origin master
   ```
3. Continue with strategy development:
   ```
   /validate-setup && /validate-strategy && /plan-strategy && /build-engine
   ```

## Requirements

- Must be run in a directory containing the trading_bot_skeleton content
- `docs/SMR.md` must exist and follow `docs/guides/STRAT_TEMPLATE.md` format
- Strategy name in SMR.md should not be the placeholder `<Strategy Name>`

## Automatic Features

- **Folder Renaming**: Renames `new_strat` or similar generic folders to strategy name
- **Smart Name Generation**: Converts "RSI Momentum Strategy" → "rsi-momentum-strategy" 
- **Template Detection**: Validates SMR.md follows proper format
- **Git Integration**: Creates clean repository ready for GitHub

This command is designed to be run immediately after:
1. Cloning skeleton content into a directory
2. Editing `docs/SMR.md` with your strategy specification following `docs/guides/STRAT_TEMPLATE.md`