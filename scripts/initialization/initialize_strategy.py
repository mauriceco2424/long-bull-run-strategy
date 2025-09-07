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
from typing import Dict, List, Tuple
import argparse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyInitializer:
    """
    Automates the transformation from skeleton to specific strategy project.
    """
    
    def __init__(self, strategy_display_name: str, strategy_repo_name: str):
        """
        Initialize strategy transformation.
        
        Args:
            strategy_display_name: Human-readable name (e.g., "RSI Momentum Strategy")
            strategy_repo_name: Repository name (e.g., "rsi-momentum-strategy")
        """
        self.strategy_display_name = strategy_display_name
        self.strategy_repo_name = strategy_repo_name
        self.strategy_class_name = self._to_class_name(strategy_display_name)
        self.strategy_var_name = self._to_variable_name(strategy_display_name)
        
        self.root_path = Path.cwd()
        self.transformations_applied = []
        
        logger.info(f"Initializing strategy transformation:")
        logger.info(f"  Display Name: {self.strategy_display_name}")
        logger.info(f"  Repo Name: {self.strategy_repo_name}")
        logger.info(f"  Class Name: {self.strategy_class_name}")
        logger.info(f"  Variable Name: {self.strategy_var_name}")
    
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
            
            # 5. Initialize git repository
            self._initialize_git_repository()
            
            # 6. Generate transformation report
            self._generate_transformation_report()
            
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
    
    def _initialize_git_repository(self) -> None:
        """Initialize new git repository and remove skeleton references."""
        import subprocess
        
        try:
            # Initialize new repository
            subprocess.run(["git", "init"], cwd=self.root_path, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=self.root_path, check=True, capture_output=True)
            
            commit_message = f"""Initialize {self.strategy_display_name} from skeleton

Automated transformation from trading_bot_skeleton to {self.strategy_repo_name}
- Updated all file references and names
- Customized documentation and configuration
- Ready for strategy development

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            subprocess.run([
                "git", "commit", "-m", commit_message
            ], cwd=self.root_path, check=True, capture_output=True)
            
            self.transformations_applied.append("Initialized new git repository")
            logger.info("✅ Initialized new git repository")
            logger.info(f"📋 Create GitHub repository: https://github.com/new (name: {self.strategy_repo_name})")
            logger.info(f"📤 Then run: git remote add origin https://github.com/YOUR_USERNAME/{self.strategy_repo_name}.git && git push -u origin master")
            
        except subprocess.CalledProcessError as e:
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


def main():
    """Main entry point for strategy initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize a new strategy project from trading_bot_skeleton"
    )
    parser.add_argument(
        "strategy_display_name",
        help="Human-readable strategy name (e.g., 'RSI Momentum Strategy')"
    )
    parser.add_argument(
        "strategy_repo_name", 
        help="Repository name (e.g., 'rsi-momentum-strategy')"
    )
    
    args = parser.parse_args()
    
    initializer = StrategyInitializer(args.strategy_display_name, args.strategy_repo_name)
    initializer.execute_transformation()


if __name__ == "__main__":
    main()