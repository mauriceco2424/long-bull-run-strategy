# Initialize Strategy

Transform the trading_bot_skeleton into a specific strategy project with proper naming, GitHub repository setup, and file customization.

## Usage

```
/initialize-strategy "Strategy Display Name" "repo-name"
```

## Examples

```
/initialize-strategy "RSI Momentum Strategy" "rsi-momentum-strategy"
/initialize-strategy "Bollinger Band Breakout" "bb-breakout"
/initialize-strategy "MACD Cross Strategy" "macd-cross"
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
   git remote add origin https://github.com/YOUR_USERNAME/{repo-name}.git
   git push -u origin master
   ```
3. Continue with strategy development:
   ```
   /validate-setup && /validate-strategy && /plan-strategy && /build-engine
   ```

## Requirements

- Must be run in a directory containing the trading_bot_skeleton content
- Strategy name should be descriptive and unique
- Repository name should follow GitHub naming conventions (lowercase, hyphens)

This command is designed to be run immediately after cloning the skeleton content into an empty directory.