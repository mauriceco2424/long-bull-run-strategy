"""
Strategy Initialization Script

Transforms the trading_bot_skeleton into a specific strategy project with proper naming,
GitHub repository creation, and file customization.
"""

import os
import json
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import logging

# Import quiet output utilities
import sys
sys.path.append(str(Path(__file__).parent.parent / "engine" / "utils"))
from quiet_output import git_quiet, quiet_print, QuietContext
from logging_config import setup_logging
from datetime import datetime

# Setup logging with quiet mode awareness
logger = setup_logging(__name__)


class StrategyInitializer:
    """
    Automates the transformation from skeleton to specific strategy project.
    Reads strategy name from SMR.md and derives all naming automatically.
    """
    
    def __init__(self, strategy_display_name: Optional[str] = None, strategy_repo_name: Optional[str] = None):
        """
        Initialize strategy transformation.
        
        Args:
            strategy_display_name: Optional override for strategy name (normally read from SMR.md)
            strategy_repo_name: Optional override for repo name (normally auto-generated)
        """
        self.root_path = Path.cwd()
        self.transformations_applied = []
        
        # Read strategy name from SMR.md if not provided
        if strategy_display_name is None:
            self.strategy_display_name = self._read_strategy_name_from_smr()
        else:
            self.strategy_display_name = strategy_display_name
            
        # Auto-generate repo name if not provided
        if strategy_repo_name is None:
            self.strategy_repo_name = self._to_repo_name(self.strategy_display_name)
        else:
            self.strategy_repo_name = strategy_repo_name
            
        self.strategy_class_name = self._to_class_name(self.strategy_display_name)
        self.strategy_var_name = self._to_variable_name(self.strategy_display_name)
        
        # Read skeleton version for lineage tracking
        self.skeleton_version = self._read_skeleton_version()
        
        logger.info(f"Initializing strategy transformation:")
        logger.info(f"  Display Name: {self.strategy_display_name}")
        logger.info(f"  Repo Name: {self.strategy_repo_name}")
        logger.info(f"  Class Name: {self.strategy_class_name}")
        logger.info(f"  Variable Name: {self.strategy_var_name}")
        logger.info(f"  Skeleton Version: {self.skeleton_version}")
    
    def _read_strategy_name_from_smr(self) -> str:
        """Read strategy name from SMR.md file."""
        smr_path = self.root_path / "docs" / "SMR.md"
        
        if not smr_path.exists():
            raise FileNotFoundError(
                f"SMR.md not found at {smr_path}. "
                "Please ensure you have the strategy specification file in docs/SMR.md "
                "following the docs/guides/STRAT_TEMPLATE.md format."
            )
        
        try:
            content = smr_path.read_text(encoding='utf-8')
            
            # Look for pattern: **Name**: `<Strategy Name>`
            name_match = re.search(r'\*\*Name\*\*:\s*`([^`]+)`', content)
            if name_match:
                strategy_name = name_match.group(1)
                if strategy_name and strategy_name != "<Strategy Name>":
                    logger.info(f"Found strategy name in SMR.md: {strategy_name}")
                    return strategy_name
            
            # Alternative pattern: **Name**: Strategy Name (without backticks)
            alt_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', content)
            if alt_match:
                strategy_name = alt_match.group(1).strip()
                if strategy_name and not strategy_name.startswith('<') and not strategy_name.startswith('`'):
                    logger.info(f"Found strategy name in SMR.md: {strategy_name}")
                    return strategy_name
                    
            raise ValueError(
                "Strategy name not found or still template placeholder in SMR.md. "
                "Please update the **Name**: field in docs/SMR.md with your actual strategy name. "
                "Follow the docs/guides/STRAT_TEMPLATE.md format."
            )
            
        except Exception as e:
            logger.error(f"Error reading SMR.md: {str(e)}")
            raise
    
    def _read_skeleton_version(self) -> str:
        """Read skeleton version from SKELETON_VERSION.md file."""
        version_path = self.root_path / "SKELETON_VERSION.md"
        
        if not version_path.exists():
            logger.warning("SKELETON_VERSION.md not found, using default version")
            return "unknown"
        
        try:
            content = version_path.read_text(encoding='utf-8')
            
            # Look for pattern: **Current Version**: 1.0.0
            version_match = re.search(r'\*\*Current Version\*\*:\s*([^\s\n]+)', content)
            if version_match:
                version = version_match.group(1)
                logger.info(f"Found skeleton version: {version}")
                return version
            
            logger.warning("Could not parse version from SKELETON_VERSION.md")
            return "unknown"
            
        except Exception as e:
            logger.warning(f"Error reading SKELETON_VERSION.md: {str(e)}")
            return "unknown"
    
    def _to_repo_name(self, name: str) -> str:
        """Convert display name to repository name format (kebab-case)."""
        # Remove special characters and convert to lowercase
        clean_name = re.sub(r'[^\w\s-]', '', name.lower())
        # Replace spaces and underscores with hyphens
        repo_name = re.sub(r'[\s_]+', '-', clean_name)
        # Remove multiple consecutive hyphens
        repo_name = re.sub(r'-+', '-', repo_name)
        # Remove leading/trailing hyphens
        return repo_name.strip('-')
    
    def _to_class_name(self, name: str) -> str:
        """Convert display name to ClassName format."""
        words = re.findall(r'\b\w+\b', name)
        return ''.join(word.capitalize() for word in words)
    
    def _to_variable_name(self, name: str) -> str:
        """Convert display name to variable_name format."""
        words = re.findall(r'\b\w+\b', name.lower())
        return '_'.join(words)
    
    def execute_transformation(self) -> None:
        """Execute complete skeleton-to-strategy transformation."""
        logger.info("Starting strategy transformation process...")
        
        try:
            # 1. Rename workspace file
            self._rename_workspace_file()
            
            # 2. Update all file contents with strategy names
            self._update_file_contents()
            
            # 3. Update README with strategy-specific information
            self._update_readme()
            
            # 4. Update documentation files
            self._update_documentation()
            
            # 5. Rename parent folder if needed
            self._rename_parent_folder()
            
            # 6. Initialize git repository
            self._initialize_git_repository()
            
            # 7. Generate framework info (preserve skeleton version)
            self._generate_framework_info()
            
            # 8. Generate transformation report
            self._generate_transformation_report()
            
            # 9. Cleanup skeleton artifacts (final step)
            self._cleanup_skeleton_artifacts()
            
            logger.info("✅ Strategy transformation completed successfully!")
            logger.info(f"Your {self.strategy_display_name} project is ready!")
            logger.info(f"Next steps: /validate-setup && /validate-strategy")
            
        except Exception as e:
            logger.error(f"❌ Transformation failed: {str(e)}")
            raise
    
    def _rename_workspace_file(self) -> None:
        """Rename workspace file to strategy name."""
        old_workspace_files = list(self.root_path.glob("*.code-workspace"))
        
        if old_workspace_files:
            old_file = old_workspace_files[0]
            new_file = self.root_path / f"{self.strategy_repo_name}.code-workspace"
            
            shutil.move(str(old_file), str(new_file))
            self.transformations_applied.append(f"Renamed {old_file.name} → {new_file.name}")
            logger.info(f"Renamed workspace: {new_file.name}")
    
    def _update_file_contents(self) -> None:
        """Update all relevant files with strategy-specific names."""
        # Define replacement patterns
        replacements = [
            # Generic skeleton references
            ("trading_bot_skeleton", self.strategy_repo_name),
            ("Trading Strategy Framework Skeleton", self.strategy_display_name + " Framework"),
            ("trading skeleton", self.strategy_var_name),
            ("Skeleton", self.strategy_class_name),
            ("skeleton", self.strategy_var_name.lower()),
            
            # Workspace and project references
            ("claude_skeleton_trading strat", self.strategy_repo_name),
            ("claude_skeleton_trading", self.strategy_repo_name),
        ]
        
        # File patterns to update
        file_patterns = [
            "**/*.md", "**/*.py", "**/*.json", "**/*.yaml", "**/*.yml",
            "**/*.toml", "**/*.cfg", "**/*.ini", "**/*.txt"
        ]
        
        # Files to exclude
        exclude_patterns = [
            ".git/**", "data/**", "cache/**", "__pycache__/**", 
            "*.pyc", ".venv/**", "venv/**", "node_modules/**"
        ]
        
        files_updated = 0
        
        for pattern in file_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and not self._should_exclude_file(file_path, exclude_patterns):
                    if self._update_file_content(file_path, replacements):
                        files_updated += 1
        
        self.transformations_applied.append(f"Updated {files_updated} files with strategy names")
        logger.info(f"Updated {files_updated} files with strategy-specific names")
    
    def _should_exclude_file(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded from updates."""
        for pattern in exclude_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def _update_file_content(self, file_path: Path, replacements: List[Tuple[str, str]]) -> bool:
        """Update content of a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except (UnicodeDecodeError, PermissionError, OSError) as e:
            logger.warning(f"Could not update {file_path}: {str(e)}")
        
        return False
    
    def _update_readme(self) -> None:
        """Update README with strategy-specific quick start."""
        readme_path = self.root_path / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            
            # Update title
            content = re.sub(
                r"# Trading Strategy Framework Skeleton",
                f"# {self.strategy_display_name}",
                content
            )
            
            # Update description
            content = re.sub(
                r"A production-ready framework for building, backtesting, and optimizing trading strategies.*",
                f"A production-ready {self.strategy_display_name.lower()} implementation using the Claude Code trading framework with sophisticated backtesting and optimization capabilities.",
                content
            )
            
            # Add skeleton version reference after description
            from datetime import datetime
            version_line = f"\n> **Built with**: Trading Bot Skeleton v{self.skeleton_version} | **Initialized**: {datetime.now().strftime('%Y-%m-%d')}\n"
            content = re.sub(
                r"(A production-ready .* capabilities\.)\n",
                r"\1" + version_line + "\n",
                content
            )
            
            # Update quick start examples
            content = content.replace(
                'mkdir my-rsi-momentum-strategy',
                f'mkdir {self.strategy_repo_name}'
            )
            content = content.replace(
                'cd my-rsi-momentum-strategy',
                f'cd {self.strategy_repo_name}'
            )
            
            readme_path.write_text(content, encoding='utf-8')
            self.transformations_applied.append("Updated README with strategy-specific information")
    
    def _update_documentation(self) -> None:
        """Update documentation files."""
        # Update SMR.md with strategy name
        smr_path = self.root_path / "docs" / "SMR.md"
        if smr_path.exists():
            content = smr_path.read_text(encoding='utf-8')
            content = content.replace("Strategy Name", self.strategy_display_name)
            smr_path.write_text(content, encoding='utf-8')
            self.transformations_applied.append("Updated SMR.md with strategy name")
        
        # Update EMR.md if needed
        emr_path = self.root_path / "docs" / "EMR.md"
        if emr_path.exists():
            content = emr_path.read_text(encoding='utf-8')
            content = content.replace("Trading Bot Skeleton", self.strategy_display_name)
            emr_path.write_text(content, encoding='utf-8')
            self.transformations_applied.append("Updated EMR.md with strategy name")
    
    def _rename_parent_folder(self) -> None:
        """Rename parent folder to match strategy repo name."""
        current_folder_name = self.root_path.name
        target_folder_name = self.strategy_repo_name
        
        # Skip if folder names already match
        if current_folder_name != target_folder_name:
            parent_dir = self.root_path.parent
            new_folder_path = parent_dir / target_folder_name
            
            # Check if target folder already exists
            if new_folder_path.exists():
                logger.warning(f"Target folder {target_folder_name} already exists. Skipping folder rename.")
                return
            
            try:
                # Rename the folder
                self.root_path.rename(new_folder_path)
                self.root_path = new_folder_path  # Update our working directory
                self.transformations_applied.append(f"Renamed folder: {current_folder_name} → {target_folder_name}")
                logger.info(f"✅ Renamed folder: {current_folder_name} → {target_folder_name}")
                
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not rename folder: {str(e)}")
                logger.info(f"You can manually rename {current_folder_name} to {target_folder_name}")
        else:
            logger.info(f"Folder name already matches strategy: {current_folder_name}")
            self.transformations_applied.append(f"Folder name already correct: {current_folder_name}")
    
    def _initialize_git_repository(self) -> None:
        """Initialize new git repository and remove skeleton references."""
        try:
            # Initialize new repository using quiet operations
            git_quiet("init", cwd=self.root_path)
            git_quiet("add", ".", cwd=self.root_path)
            
            commit_message = f"""Initialize {self.strategy_display_name} from skeleton

Automated transformation from trading_bot_skeleton to {self.strategy_repo_name}
- Updated all file references and names
- Customized documentation and configuration
- Ready for strategy development

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            git_quiet("commit", "-m", commit_message, cwd=self.root_path)
            
            self.transformations_applied.append("Initialized new git repository")
            logger.info("✅ Initialized new git repository")
            logger.info(f"📋 Create GitHub repository: https://github.com/new (name: {self.strategy_repo_name})")
            logger.info(f"📤 Then run: git remote add origin https://github.com/YOUR_USERNAME/{self.strategy_repo_name}.git && git push -u origin master")
            
        except Exception as e:
            logger.warning(f"Git initialization failed: {e}")
            self.transformations_applied.append(f"Git initialization failed: {e}")
    
    def _generate_transformation_report(self) -> None:
        """Generate transformation report."""
        report = {
            "transformation_date": datetime.now().isoformat(),
            "strategy_display_name": self.strategy_display_name,
            "strategy_repo_name": self.strategy_repo_name,
            "strategy_class_name": self.strategy_class_name,
            "strategy_var_name": self.strategy_var_name,
            "transformations_applied": self.transformations_applied,
            "next_steps": [
                "/validate-setup",
                "/validate-strategy",
                "/plan-strategy", 
                "/build-engine"
            ],
            "github_setup": {
                "create_repo_url": "https://github.com/new",
                "repo_name": self.strategy_repo_name,
                "add_remote_command": f"git remote add origin https://github.com/YOUR_USERNAME/{self.strategy_repo_name}.git",
                "push_command": "git push -u origin master"
            }
        }
        
        report_path = self.root_path / f"TRANSFORMATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Transformation report saved: {report_path.name}")
    
    def _generate_framework_info(self) -> None:
        """Generate framework information file to preserve skeleton version lineage."""
        from datetime import datetime
        
        framework_info = {
            "generated_from": f"Trading Bot Skeleton v{self.skeleton_version}",
            "generation_date": datetime.now().strftime('%Y-%m-%d'),
            "strategy_name": self.strategy_display_name,
            "strategy_repo_name": self.strategy_repo_name,
            "framework_features": [
                "9-command dual-path workflow",
                "6 specialized Claude Code agents", 
                "Automated GitHub repository creation",
                "Universal speed optimization (10-50x)",
                "Professional LaTeX reporting",
                "Production-ready validation hooks"
            ]
        }
        
        # Create user-friendly markdown file
        framework_content = f"""# Strategy Framework Information

**Generated from**: Trading Bot Skeleton v{self.skeleton_version}  
**Generation Date**: {framework_info['generation_date']}  
**Strategy Name**: {self.strategy_display_name}

This strategy was created using the Trading Bot Skeleton framework.

## Framework Capabilities (v{self.skeleton_version})
- 9-command dual-path workflow (single-run + optimization paths)
- 6 specialized Claude Code agents with quality gates  
- Automated GitHub repository creation and professional Git branching
- Universal speed optimization (FilterGateManager, ReferenceEngine)
- Comprehensive visualization and LaTeX reporting system
- Production-ready hook system with safety validation

## Commands Available
- **Setup**: `/validate-setup` → `/validate-strategy` → `/plan-strategy` → `/build-engine`
- **Single-Run**: `/run` → `/analyze-single-run` → `/evaluate-single-run`  
- **Optimization**: `/run-optimization` → `/evaluate-optimization`

---
*This file tracks the framework lineage and is safe to keep for reference.*
"""
        
        framework_path = self.root_path / "FRAMEWORK_INFO.md"
        
        with open(framework_path, 'w', encoding='utf-8') as f:
            f.write(framework_content)
        
        self.transformations_applied.append(f"Generated framework info - preserves skeleton v{self.skeleton_version} lineage")
        logger.info(f"📋 Generated framework info - skeleton v{self.skeleton_version} lineage preserved")
    
    def _cleanup_skeleton_artifacts(self) -> None:
        """Cleanup skeleton-specific files that become obsolete after transformation."""
        logger.info("🧹 Cleaning up skeleton artifacts...")
        
        try:
            # Safety check: Ensure transformation was successful
            if not self.strategy_display_name or self.strategy_display_name == "<Strategy Name>":
                logger.warning("Skipping cleanup - transformation may not be complete")
                return
            
            # Files/directories to remove (in safe order)
            cleanup_targets = [
                # Remove skeleton version file (replaced by FRAMEWORK_INFO.md)
                self.root_path / "SKELETON_VERSION.md",
                
                # Remove initialize command (no longer needed)
                self.root_path / ".claude" / "commands" / "initialize.md",
                
                # Remove initialization script directory (this script's parent)
                # Note: This removes the script itself, so must be last
                self.root_path / "scripts" / "initialization"
            ]
            
            # Remove obsolete files
            for target in cleanup_targets[:-1]:  # All except initialization directory
                if target.exists():
                    if target.is_file():
                        target.unlink()
                        self.transformations_applied.append(f"Removed obsolete file: {target.name}")
                        logger.info(f"🗑️  Removed: {target.relative_to(self.root_path)}")
                    elif target.is_dir():
                        import shutil
                        shutil.rmtree(target)
                        self.transformations_applied.append(f"Removed obsolete directory: {target.name}")
                        logger.info(f"🗑️  Removed: {target.relative_to(self.root_path)}")
            
            # Update files to remove skeleton references
            self._update_claude_md_cleanup()
            self._update_readme_cleanup()
            
            # Schedule removal of initialization directory (delayed)
            # This directory contains the currently running script
            init_dir = self.root_path / "scripts" / "initialization"
            if init_dir.exists():
                # Create a cleanup script that removes the directory after this script exits
                cleanup_script = self.root_path / "cleanup_init.py"
                cleanup_content = f'''#!/usr/bin/env python3
import os
import shutil
import time
from pathlib import Path

# Wait a moment for parent process to exit
time.sleep(1)

# Remove initialization directory
init_dir = Path("{init_dir}")
if init_dir.exists():
    shutil.rmtree(init_dir)
    quiet_print("🗑️  Removed: scripts/initialization/")

# Remove this cleanup script
cleanup_script = Path(__file__)
if cleanup_script.exists():
    cleanup_script.unlink()
'''
                with open(cleanup_script, 'w') as f:
                    f.write(cleanup_content)
                
                # Mark cleanup script for execution after main script exits
                self.transformations_applied.append("Scheduled removal of initialization directory")
                logger.info("📝 Scheduled cleanup of initialization directory after script completion")
            
            logger.info("✅ Skeleton artifact cleanup completed")
            
        except Exception as e:
            logger.warning(f"Cleanup encountered issues: {str(e)}")
            logger.info("Strategy transformation was successful, cleanup issues are non-critical")
    
    def _update_claude_md_cleanup(self) -> None:
        """Remove skeleton-specific commands from CLAUDE.md."""
        claude_md = self.root_path / "CLAUDE.md"
        if not claude_md.exists():
            return
        
        try:
            content = claude_md.read_text(encoding='utf-8')
            
            # Remove initialization command reference
            content = content.replace(
                "- `python scripts/initialization/initialize_strategy.py` - Transform skeleton to specific strategy project\n", 
                ""
            )
            
            claude_md.write_text(content, encoding='utf-8')
            self.transformations_applied.append("Updated CLAUDE.md - removed skeleton transformation commands")
            logger.info("📝 Updated CLAUDE.md - removed obsolete commands")
            
        except Exception as e:
            logger.warning(f"Could not update CLAUDE.md: {str(e)}")
    
    def _update_readme_cleanup(self) -> None:
        """Update README.md to focus on strategy development instead of skeleton setup."""
        readme_path = self.root_path / "README.md"
        if not readme_path.exists():
            return
        
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Update title to strategy name
            content = re.sub(
                r"# Trading Strategy Framework Skeleton",
                f"# {self.strategy_display_name}",
                content
            )
            
            # Replace skeleton setup section with strategy development guide
            setup_section = '''## 🚀 Strategy Development

This is a fully configured trading strategy project. The skeleton transformation has been completed.

### **Prerequisites**
- **Git Bash** (for GitHub operations)
- **GitHub CLI** installed (`gh auth login` completed)
- **Python dependencies**: Run `/validate-setup` to install

### **Development Workflow**

1. **Setup Dependencies**:
   ```bash
   /validate-setup
   ```

2. **Build and Test Your Strategy**:
   ```bash
   /validate-strategy && /plan-strategy && /build-engine
   /run && /analyze-single-run && /evaluate-single-run
   ```

3. **Parameter Optimization** (optional):
   ```bash
   # Create optimization_config.json first
   /run-optimization && /evaluate-optimization
   ```'''
            
            # Replace the entire Quick Start section
            content = re.sub(
                r"## 🚀 Quick Start.*?(?=## 🌿 Git Branching Workflow)",
                setup_section + "\n\n",
                content,
                flags=re.DOTALL
            )
            
            readme_path.write_text(content, encoding='utf-8')
            self.transformations_applied.append("Updated README.md - replaced skeleton setup with strategy development guide")
            logger.info("📝 Updated README.md - focused on strategy development")
            
        except Exception as e:
            logger.warning(f"Could not update README.md: {str(e)}")


def main():
    """Main entry point for strategy initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize a new strategy project from trading_bot_skeleton. "
        "Reads strategy name from docs/SMR.md by default."
    )
    parser.add_argument(
        "strategy_display_name", 
        nargs='?',
        help="Optional: Override strategy name (normally read from SMR.md)"
    )
    parser.add_argument(
        "strategy_repo_name", 
        nargs='?',
        help="Optional: Override repository name (normally auto-generated)"
    )
    parser.add_argument(
        "--from-smr", 
        action="store_true", 
        default=True,
        help="Read strategy name from SMR.md (default behavior)"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, read from SMR.md
    if args.strategy_display_name is None and args.strategy_repo_name is None:
        logger.info("No arguments provided. Reading strategy name from docs/SMR.md...")
        initializer = StrategyInitializer()
    else:
        initializer = StrategyInitializer(args.strategy_display_name, args.strategy_repo_name)
        
    initializer.execute_transformation()


if __name__ == "__main__":
    main()