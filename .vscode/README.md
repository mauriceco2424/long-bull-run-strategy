# VS Code Workspace Configuration

This directory contains optimized VS Code settings for trading framework development.

## What These Settings Do

### 🎯 **Screen Flicker Prevention**
- **`gpuAcceleration: "off"`** - Forces DOM renderer to prevent WebGL glitches
- **`scrollback: 1000`** - Reduces terminal buffer size for less rendering work  
- **`smoothScrolling: false`** - Eliminates animations that cause flickering
- **`windowsEnableConpty: false`** - Uses compatibility mode for Windows terminals

### 🐍 **Python Development Optimization**
- **Black formatter** with 100-character line length (matches framework standards)
- **Ruff linting** with automatic import organization
- **pytest integration** (matches framework testing approach)
- **Auto-formatting on save** with import organization

### 🔧 **Git Workflow Enhancements**
- **Auto-fetch enabled** - Stay up to date with remote changes
- **Smart commits** - Automatically stage changes when committing
- **Streamlined sync** - No confirmation dialogs for push/pull operations

### 🖥️ **Terminal Configuration**
- **Git Bash as default** - Preferred terminal for framework operations
- **PowerShell fallback** - Secondary option for Windows-specific tasks
- **Cross-platform compatibility** - Uses VS Code's built-in terminal detection

## How It Works

When you open the workspace file (`{strategy-name}.code-workspace`), VS Code automatically applies these settings to your project. No manual configuration required!

## Customization

To override these settings for your personal preferences:

1. **User Settings**: Open `File > Preferences > Settings` and modify your user settings
2. **Workspace Settings**: Edit `.vscode/settings.json` directly (affects all users of this project)

User settings always take precedence over workspace settings.

## Key Benefits

✅ **Eliminates screen flickering** during Claude Code operations  
✅ **Consistent Python formatting** across all contributors  
✅ **Streamlined Git workflow** with auto-fetch and smart commits  
✅ **Optimal terminal performance** for long-running operations  
✅ **Zero setup required** - works out of the box

## Troubleshooting

### Terminal Flickering Still Occurs?
1. Restart VS Code after opening the workspace
2. Verify settings are applied: `Ctrl+Shift+P` → "Open Workspace Settings (JSON)"
3. Check if user settings override workspace settings

### Git Bash Not Available?
VS Code will automatically fallback to PowerShell or Command Prompt if Git Bash isn't installed.

### Python Formatter Not Working?
Install the required extensions:
- `ms-python.black-formatter`
- `charliermarsh.ruff`

VS Code will prompt to install these when first opening Python files.