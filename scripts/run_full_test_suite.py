#!/usr/bin/env python3
"""
Complete Trading Framework Test Suite

Automated testing script that validates all components of the trading skeleton.
Future Claude instances can run this to quickly verify framework health.
"""

import os
import sys
import json
import subprocess
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    color = Colors.BLUE
    if status == "PASS":
        color = Colors.GREEN
    elif status == "FAIL":
        color = Colors.RED
    elif status == "WARN":
        color = Colors.YELLOW

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {status}: {message}{Colors.ENDC}")

def run_command(cmd: str, description: str, timeout: int = 60, cwd: str = None) -> Tuple[bool, str, str]:
    """Run a command and capture output."""
    print_status(f"Running: {description}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )

        success = result.returncode == 0
        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists."""
    exists = os.path.exists(file_path)
    status = "PASS" if exists else "FAIL"
    print_status(f"File check: {description} - {file_path}", status)
    return exists

def check_import(module_path: str, description: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        cmd = f'python -c "import {module_path}; print(\\"✓ Import successful\\")"'
        success, stdout, stderr = run_command(cmd, f"Import check: {description}", timeout=10)

        if success and "✓" in stdout:
            print_status(f"Import check: {description}", "PASS")
            return True
        else:
            print_status(f"Import check: {description} - {stderr}", "FAIL")
            return False

    except Exception as e:
        print_status(f"Import check: {description} - {str(e)}", "FAIL")
        return False

class TradingFrameworkTestSuite:
    """Complete test suite for the trading framework."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def test(self, test_name: str, test_func, *args, **kwargs):
        """Run a test and record results."""
        self.test_count += 1
        print_status(f"Test {self.test_count}: {test_name}", "INFO")

        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            execution_time = time.time() - start_time

            if result:
                self.passed_count += 1
                print_status(f"Test {self.test_count}: {test_name} ({execution_time:.2f}s)", "PASS")
            else:
                self.failed_count += 1
                print_status(f"Test {self.test_count}: {test_name} ({execution_time:.2f}s)", "FAIL")

            self.results["tests"][test_name] = {
                "passed": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.failed_count += 1
            print_status(f"Test {self.test_count}: {test_name} - ERROR: {str(e)}", "FAIL")

            self.results["tests"][test_name] = {
                "passed": False,
                "execution_time": execution_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

            return False

    def test_file_structure(self) -> bool:
        """Test that all required files exist."""
        required_files = [
            "CLAUDE.md",
            "requirements.txt",
            "test_parameter_config.md",
            "test_optimization_config.json",
            "run_test.py",
            "scripts/engine/backtest.py",
            "scripts/engine/utils/config_parser.py",
            "scripts/single_analysis/analyze_test_run.py",
            "scripts/single_evaluation/evaluator.py",
            "scripts/optimization/optimization_engine.py",
            "docs/TESTING.md"
        ]

        all_exist = True
        for file_path in required_files:
            if not check_file_exists(file_path, f"Required file: {file_path}"):
                all_exist = False

        return all_exist

    def test_python_imports(self) -> bool:
        """Test that all critical Python modules can be imported."""
        # Add current directory to Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'

        import_tests = [
            ("scripts.engine.backtest", "Core backtest engine"),
            ("scripts.engine.utils.config_parser", "Configuration parser"),
            ("scripts.single_analysis.analyze_test_run", "Single run analyzer"),
            ("scripts.optimization.optimization_engine", "Optimization engine")
        ]

        all_imported = True
        for module_path, description in import_tests:
            # Use environment with PYTHONPATH set
            cmd = f'python -c "import {module_path}; print(\\"+ Import successful\\")"'
            success, stdout, stderr = run_command(cmd, f"Import: {description}", timeout=15)

            if success and "+" in stdout:
                print_status(f"Import: {description}", "PASS")
            else:
                print_status(f"Import: {description} - {stderr}", "FAIL")
                all_imported = False

        return all_imported

    def test_basic_engine(self) -> bool:
        """Test basic engine functionality."""
        success, stdout, stderr = run_command(
            "python run_test.py",
            "Basic engine test",
            timeout=120
        )

        if success and ("TEST COMPLETED" in stdout or "Status: PASS" in stdout):
            return True
        else:
            print_status(f"Basic engine test failed: {stderr}", "FAIL")
            return False

    def test_comprehensive_backtest(self) -> bool:
        """Test comprehensive backtest with accounting validation."""
        # Set environment variable for Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'

        cmd = f'python -m scripts.engine.backtest test_parameter_config.md --test-mode --validate-accounting'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )

        success = result.returncode == 0
        stdout = result.stdout
        stderr = result.stderr

        if success and "Backtest completed" in stdout:
            return True
        else:
            print_status(f"Comprehensive backtest failed: {stderr}", "FAIL")
            return False

    def test_single_analysis(self) -> bool:
        """Test single run analysis functionality."""
        success, stdout, stderr = run_command(
            "python scripts/single_analysis/analyze_test_run.py",
            "Single run analysis",
            timeout=120
        )

        if success and ("PASSED" in stdout or "ANALYSIS COMPLETED" in stdout):
            return True
        else:
            print_status(f"Single analysis failed: {stderr}", "FAIL")
            return False

    def test_optimization_framework(self) -> bool:
        """Test optimization framework."""
        success, stdout, stderr = run_command(
            "python test_optimization_simple.py",
            "Optimization framework",
            timeout=60
        )

        if success and ("✓ Optimization test completed" in stdout or "parameter combinations" in stdout):
            return True
        else:
            print_status(f"Optimization framework failed: {stderr}", "FAIL")
            return False

    def test_config_parser(self) -> bool:
        """Test configuration parser with test config."""
        test_code = '''
import sys, os
sys.path.append(os.path.join("scripts", "engine"))
from utils.config_parser import ConfigParser

parser = ConfigParser()
config = parser.parse_config("test_parameter_config.md")

# Check required sections
required = ["backtest", "universe", "strategy_parameters"]
for section in required:
    assert section in config, f"Missing section: {section}"

# Check specific values
assert config["backtest"]["initial_capital"] == 10000.0
assert config["universe"]["symbols"] == ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
assert config["universe"]["timeframe"] == "1h"

print("+ Config parser validation passed")
'''

        success, stdout, stderr = run_command(
            f'python -c "{test_code}"',
            "Configuration parser validation",
            timeout=30
        )

        if success and "+" in stdout:
            return True
        else:
            print_status(f"Config parser test failed: {stderr}", "FAIL")
            return False

    def test_quiet_mode(self) -> bool:
        """Test quiet mode functionality."""
        success, stdout, stderr = run_command(
            "python scripts/quiet_mode.py status",
            "Quiet mode check",
            timeout=10
        )

        if success and "Quiet mode:" in stdout:
            return True
        else:
            print_status(f"Quiet mode test failed: {stderr}", "FAIL")
            return False

    def save_results(self):
        """Save test results to file."""
        self.results["summary"] = {
            "total_tests": self.test_count,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "success_rate": f"{(self.passed_count/self.test_count*100):.1f}%" if self.test_count > 0 else "0%"
        }

        # Create results directory if it doesn't exist
        Path("data/test_results").mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"data/test_results/test_suite_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print_status(f"Test results saved to: {results_file}", "INFO")

    def run_all_tests(self):
        """Run the complete test suite."""
        print_status("Starting Trading Framework Test Suite", "INFO")
        print("=" * 60)

        # Core structure and setup tests
        self.test("File Structure", self.test_file_structure)
        self.test("Python Imports", self.test_python_imports)
        self.test("Configuration Parser", self.test_config_parser)
        self.test("Quiet Mode", self.test_quiet_mode)

        # Engine functionality tests
        self.test("Basic Engine", self.test_basic_engine)
        self.test("Comprehensive Backtest", self.test_comprehensive_backtest)

        # Analysis and optimization tests
        self.test("Single Analysis", self.test_single_analysis)
        self.test("Optimization Framework", self.test_optimization_framework)

        # Summary
        print("=" * 60)
        print_status("Test Suite Complete", "INFO")
        print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"  Total Tests: {self.test_count}")
        print(f"  Passed: {Colors.GREEN}{self.passed_count}{Colors.ENDC}")
        print(f"  Failed: {Colors.RED}{self.failed_count}{Colors.ENDC}")

        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        print(f"  Success Rate: {success_rate:.1f}%")

        self.save_results()

        if self.failed_count == 0:
            print_status("*** ALL TESTS PASSED - Framework is ready for use! ***", "PASS")
            return True
        else:
            print_status(f"X {self.failed_count} tests failed - Check individual test results", "FAIL")
            return False

def main():
    """Main entry point."""
    print(f"{Colors.BOLD}Trading Framework Test Suite{Colors.ENDC}")
    print(f"Testing complete skeleton functionality for future Claude instances")
    print()

    # Change to the script's directory to ensure relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))

    suite = TradingFrameworkTestSuite()
    success = suite.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()