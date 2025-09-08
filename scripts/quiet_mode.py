"""
Quiet Mode Control

Simple script to enable/disable quiet mode for all trading operations.
"""

import os
import sys
import json
from pathlib import Path

# Persistent state file
STATE_FILE = Path("cloud/state/quiet_mode.json")

def ensure_state_dir():
    """Ensure state directory exists."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_quiet_mode(enabled: bool):
    """Save quiet mode state persistently."""
    ensure_state_dir()
    with open(STATE_FILE, 'w') as f:
        json.dump({"enabled": enabled}, f)

def load_quiet_mode():
    """Load quiet mode state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f).get("enabled", False)
    return False  # Default is non-quiet mode (shows progress bars)

def enable_quiet_mode():
    """Enable quiet mode - agents will be almost completely silent."""
    os.environ['TRADING_QUIET_MODE'] = 'true'
    save_quiet_mode(True)
    print("Quiet mode ENABLED")
    print("   Agents will only show final results and critical errors")
    print("   No progress bars, no debug output, no flickering")
    print("   To disable: python scripts/quiet_mode.py off")

def disable_quiet_mode():
    """Disable quiet mode - agents will show detailed output."""
    os.environ['TRADING_QUIET_MODE'] = 'false'
    save_quiet_mode(False)
    print("Quiet mode DISABLED") 
    print("   Agents will show detailed progress and debug output")
    print("   Set TRADING_VERBOSE=true for full verbosity")
    print("   To enable: python scripts/quiet_mode.py on")

def show_status():
    """Show current quiet mode status."""
    # Check persistent state file first, then env var as fallback
    current_status = load_quiet_mode()
    if not current_status:
        current_status = os.getenv('TRADING_QUIET_MODE', 'false').lower() == 'true'
    
    status_text = "ENABLED" if current_status else "DISABLED"
    print(f"Quiet mode: {status_text}")
    
    if current_status:
        print("   Agents are almost completely silent")
        print("   Only final results and critical errors shown")
        print("   To disable: python scripts/quiet_mode.py off")
    else:
        print("   Agents show detailed progress and debug output")
        print("   Set TRADING_VERBOSE=true for maximum verbosity")
        print("   To enable: python scripts/quiet_mode.py on")

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/quiet_mode.py [on|off|status]")
        print("")
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['on', 'enable', 'true']:
        enable_quiet_mode()
    elif command in ['off', 'disable', 'false']:
        disable_quiet_mode()
    elif command in ['status', 'check']:
        show_status()
    else:
        print(f"Unknown command: {command}")
        print("Use: on, off, or status")
        show_status()

if __name__ == "__main__":
    main()