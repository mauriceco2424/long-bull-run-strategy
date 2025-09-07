#!/usr/bin/env python3
"""
Trading Strategy Framework Setup Validation

Validates that the skeleton framework is properly configured and ready for use.
Run this after cloning the repository to ensure everything is working correctly.

Usage: python validate_setup.py
"""

import os
import sys
import json
import importlib
from pathlib import Path
from typing import List, Dict, Tuple, Any


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'  
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ValidationResult:
    def __init__(self, passed: bool, message: str, details: str = ""):
        self.passed = passed
        self.message = message
        self.details = details


class FrameworkValidator:
    """Validates trading strategy framework setup"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.results: List[ValidationResult] = []
        
    def log(self, message: str, color: str = Colors.BLUE):
        """Print colored log message"""
        print(f"{color}{message}{Colors.END}")
        
    def success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}[PASS] {message}{Colors.END}")
        
    def error(self, message: str):
        """Print error message"""  
        print(f"{Colors.RED}[FAIL] {message}{Colors.END}")
        
    def warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")
        
    def validate_python_dependencies(self) -> ValidationResult:
        """Check that required Python packages can be imported, auto-install if missing"""
        self.log("Validating Python dependencies...")
        
        required_packages = [
            'yaml', 'pandas', 'numpy', 'matplotlib', 'json', 'pathlib',
            'datetime', 'importlib', 'traceback', 'signal'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            self.warning(f"Missing Python packages: {', '.join(missing_packages)}")
            
            # Check if requirements.txt exists
            requirements_file = self.root_dir / "requirements.txt"
            if requirements_file.exists():
                self.log("Attempting to install missing dependencies automatically...")
                
                try:
                    import subprocess
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        self.success("Successfully installed dependencies from requirements.txt")
                        
                        # Re-check missing packages
                        still_missing = []
                        for package in missing_packages:
                            try:
                                importlib.import_module(package)
                            except ImportError:
                                still_missing.append(package)
                        
                        if still_missing:
                            return ValidationResult(
                                False,
                                f"Some packages still missing after installation: {', '.join(still_missing)}",
                                "Manual installation may be required"
                            )
                        else:
                            return ValidationResult(True, "All required Python packages available (auto-installed)")
                            
                    else:
                        return ValidationResult(
                            False,
                            f"Failed to install dependencies automatically: {result.stderr}",
                            "Run manually: pip install -r requirements.txt"
                        )
                        
                except (subprocess.TimeoutExpired, Exception) as e:
                    return ValidationResult(
                        False,
                        f"Auto-installation failed: {str(e)}",
                        "Run manually: pip install -r requirements.txt"
                    )
            else:
                return ValidationResult(
                    False,
                    f"Missing Python packages: {', '.join(missing_packages)}",
                    "requirements.txt not found - manual installation required"
                )
        
        return ValidationResult(True, "All required Python packages available")
    
    def validate_directory_structure(self) -> ValidationResult:
        """Validate required directory structure exists"""
        self.log("Validating directory structure...")
        
        required_dirs = [
            '.claude/agents',
            '.claude/commands', 
            'docs',
            'docs/runs',
            'docs/schemas',
            'configs',
            'tools/hooks/core',
            'tools/hooks/lib',
            'tools/hooks/config',
            'cloud/state',
            'cloud/tasks',
            'data/runs',
            'data/sandbox'
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not (self.root_dir / dir_path).exists():
                missing_dirs.append(dir_path)
                
        if missing_dirs:
            return ValidationResult(
                False,
                f"Missing directories: {', '.join(missing_dirs)}",
                "Directory structure is incomplete"
            )
            
        return ValidationResult(True, "Directory structure is complete")
    
    def validate_core_files(self) -> ValidationResult:
        """Check that essential framework files exist"""
        self.log("Validating core files...")
        
        required_files = [
            'CLAUDE.md',
            'requirements.txt',
            '.gitignore',
            'docs/EMR.md',
            'docs/SMR.md',
            'docs/ECL.md',
            'docs/SCL.md',
            'tools/hooks/config/hooks.yaml',
            'tools/hooks/lib/hook_runner.py',
            'tools/hooks/lib/hook_context.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.root_dir / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            return ValidationResult(
                False,
                f"Missing core files: {', '.join(missing_files)}",
                "Framework files are incomplete"
            )
            
        return ValidationResult(True, "All core files present")
    
    def validate_agent_configs(self) -> ValidationResult:
        """Validate agent configuration files"""
        self.log("Validating agent configurations...")
        
        required_agents = [
            'trading-orchestrator.md',
            'trading-builder.md',
            'trading-single-analyzer.md',
            'trading-single-evaluator.md',
            'trading-optimizer.md',
            'trading-optimization-evaluator.md'
        ]
        
        missing_agents = []
        for agent in required_agents:
            agent_path = self.root_dir / '.claude' / 'agents' / agent
            if not agent_path.exists():
                missing_agents.append(agent)
                
        if missing_agents:
            return ValidationResult(
                False,
                f"Missing agent configs: {', '.join(missing_agents)}",
                "Agent configuration incomplete"
            )
            
        return ValidationResult(True, "All agent configurations present")
    
    def validate_command_configs(self) -> ValidationResult:
        """Validate command configuration files"""
        self.log("Validating command configurations...")
        
        required_commands = [
            'validate-setup.md', 'validate-strategy.md', 'plan-strategy.md', 
            'build-engine.md', 'run.md', 'analyze-single-run.md', 'evaluate-single-run.md',
            'run-optimization.md', 'evaluate-optimization.md'
        ]
        
        missing_commands = []
        for command in required_commands:
            cmd_path = self.root_dir / '.claude' / 'commands' / command
            if not cmd_path.exists():
                missing_commands.append(command)
                
        if missing_commands:
            return ValidationResult(
                False,
                f"Missing command configs: {', '.join(missing_commands)}",
                "Command configuration incomplete"
            )
            
        return ValidationResult(True, "All command configurations present")
    
    def validate_hook_system(self) -> ValidationResult:
        """Validate hook system configuration"""
        self.log("Validating hook system...")
        
        try:
            # Check hooks.yaml loads properly
            hooks_config = self.root_dir / 'tools' / 'hooks' / 'config' / 'hooks.yaml'
            if not hooks_config.exists():
                return ValidationResult(False, "hooks.yaml not found", "Hook configuration missing")
                
            # Try to import hook runner
            sys.path.insert(0, str(self.root_dir))
            from tools.hooks.lib.hook_runner import HookRunner
            from tools.hooks.lib.hook_context import HookContext
            
            # Test hook runner initialization
            runner = HookRunner(str(hooks_config))
            
            return ValidationResult(True, "Hook system validated successfully")
            
        except Exception as e:
            return ValidationResult(
                False, 
                f"Hook system validation failed: {str(e)}",
                "Check hooks configuration and Python imports"
            )
    
    def validate_json_schemas(self) -> ValidationResult:
        """Validate JSON schema files"""
        self.log("Validating JSON schemas...")
        
        schema_files = [
            'docs/schemas/run_registry_schema.json',
            'docs/schemas/manifest_schema.json',
            'docs/schemas/decision_registry_schema.json',
            'docs/schemas/anomaly_registry_schema.json'
        ]
        
        invalid_schemas = []
        for schema_file in schema_files:
            try:
                with open(self.root_dir / schema_file, 'r') as f:
                    json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                invalid_schemas.append(f"{schema_file}: {str(e)}")
                
        if invalid_schemas:
            return ValidationResult(
                False,
                f"Invalid schemas: {', '.join(invalid_schemas)}",
                "Schema validation failed"
            )
            
        return ValidationResult(True, "All JSON schemas valid")
    
    def validate_git_setup(self) -> ValidationResult:
        """Validate git repository setup"""
        self.log("Validating git setup...")
        
        if not (self.root_dir / '.git').exists():
            return ValidationResult(
                False,
                "Git repository not initialized",
                "Run: git init"
            )
            
        if not (self.root_dir / '.gitignore').exists():
            return ValidationResult(
                False,
                ".gitignore file missing",
                "Git ignore configuration missing"
            )
            
        return ValidationResult(True, "Git repository properly configured")
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        self.log(f"{Colors.BOLD}Trading Strategy Framework Validation{Colors.END}")
        self.log("=" * 50)
        
        validations = [
            self.validate_python_dependencies,
            self.validate_directory_structure,
            self.validate_core_files,
            self.validate_agent_configs,
            self.validate_command_configs,
            self.validate_hook_system,
            self.validate_json_schemas,
            self.validate_git_setup
        ]
        
        all_passed = True
        
        for validation in validations:
            result = validation()
            self.results.append(result)
            
            if result.passed:
                self.success(result.message)
            else:
                self.error(result.message)
                if result.details:
                    print(f"  {result.details}")
                all_passed = False
                
        self.log("=" * 50)
        
        if all_passed:
            self.success(f"{Colors.BOLD}All validations passed! Framework is ready for use.{Colors.END}")
            self.log("\nNext steps:")
            self.log("1. Create your strategy specification (.md file)")
            self.log("2. Run: /validate-setup to begin strategy development")
            self.log("3. Follow the build -> run -> analyze -> evaluate workflow")
        else:
            self.error(f"{Colors.BOLD}Some validations failed. Please fix the issues above.{Colors.END}")
            
        return all_passed


def main():
    """Main validation function"""
    validator = FrameworkValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()