"""
Run Executor

Main script for executing backtests via the /run command.
Coordinates between engine execution and artifact generation.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engine'))

from backtest import BacktestEngine
from utils.config_parser import ConfigParser
from utils.progress_tracker import ProgressTracker


class RunExecutor:
    """
    Coordinates backtest execution for the /run command.
    
    Handles:
    - Configuration validation
    - Engine execution
    - Artifact generation
    - Registry updates
    """
    
    def __init__(self, config_path: str = "parameter_config.md"):
        """
        Initialize run executor.
        
        Args:
            config_path: Path to parameter configuration file
        """
        self.config_path = config_path
        self.logger = self._setup_logging()
        
        # Initialize components
        self.config_parser = ConfigParser()
        self.progress_tracker = ProgressTracker()
        
        # Generate run ID
        self.run_id = self._generate_run_id()
        self.run_dir = os.path.join("data", "runs", self.run_id)
        
    def execute_run(self) -> Dict[str, Any]:
        """
        Execute complete backtest run.
        
        Returns:
            Run results dictionary
        """
        try:
            self.logger.info(f"Starting backtest run: {self.run_id}")
            
            # Start progress tracking
            self.progress_tracker.start_operation("Running backtest", total_phases=4)
            
            # Phase 1: Validate configuration
            self.progress_tracker.start_phase("Validating configuration")
            config = self._validate_configuration()
            self.progress_tracker.complete_phase()
            
            # Phase 2: Prepare run directory
            self.progress_tracker.start_phase("Preparing run directory") 
            self._prepare_run_directory()
            self.progress_tracker.complete_phase()
            
            # Phase 3: Execute backtest
            self.progress_tracker.start_phase("Executing backtest")
            backtest_engine = BacktestEngine(self.config_path)
            results = backtest_engine.run(self.run_id)
            self.progress_tracker.complete_phase()
            
            # Phase 4: Generate artifacts
            self.progress_tracker.start_phase("Generating artifacts")
            self._generate_artifacts(results)
            self._update_registry(results)
            self.progress_tracker.complete_phase()
            
            # Complete operation
            self.progress_tracker.complete_operation()
            
            self.logger.info(f"Backtest run completed successfully: {self.run_id}")
            
            return {
                'run_id': self.run_id,
                'status': 'success',
                'results': results,
                'run_directory': self.run_dir
            }
            
        except Exception as e:
            self.logger.error(f"Backtest run failed: {str(e)}")
            
            # Mark run as failed
            self._mark_run_failed(str(e))
            
            return {
                'run_id': self.run_id,
                'status': 'failed',
                'error': str(e),
                'run_directory': self.run_dir
            }
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        # Parse configuration
        config = self.config_parser.parse_config(self.config_path)
        
        # Validate configuration
        errors = self.config_parser.validate_config(config)
        if errors:
            error_msg = "Configuration validation errors: " + "; ".join(errors)
            raise ValueError(error_msg)
        
        self.logger.info("Configuration validated successfully")
        return config
    
    def _prepare_run_directory(self) -> None:
        """Prepare run directory structure."""
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, "figures"), exist_ok=True)
        
        self.logger.debug(f"Run directory prepared: {self.run_dir}")
    
    def _generate_artifacts(self, results: Dict[str, Any]) -> None:
        """Generate run artifacts."""
        # Generate manifest.json
        manifest = self._create_manifest(results)
        with open(os.path.join(self.run_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        # Generate metrics.json
        metrics = self._extract_metrics(results)
        with open(os.path.join(self.run_dir, "metrics.json"), 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        # Generate CSV files
        self._generate_csv_files(results)
        
        self.logger.info(f"Artifacts generated in {self.run_dir}")
    
    def _create_manifest(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create run manifest."""
        return {
            'run_id': self.run_id,
            'timestamp': datetime.now().isoformat(),
            'config_file': self.config_path,
            'engine_version': '1.0.0',
            'status': 'completed',
            'start_date': results.get('start_time'),
            'end_date': results.get('end_time'),
            'final_equity': results.get('final_equity'),
            'total_trades': results.get('total_trades'),
            'symbols': results.get('metadata', {}).get('symbols_traded', []),
            'artifacts': [
                'manifest.json',
                'metrics.json', 
                'trades.csv',
                'events.csv',
                'series.csv'
            ]
        }
    
    def _extract_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics."""
        # This would calculate comprehensive metrics
        # For now, basic structure
        return {
            'final_equity': results.get('final_equity'),
            'total_return_pct': ((results.get('final_equity', 100000) / 100000) - 1) * 100,
            'total_trades': results.get('total_trades'),
            'start_date': results.get('start_time'),
            'end_date': results.get('end_time'),
            # Additional metrics would be calculated here
        }
    
    def _generate_csv_files(self, results: Dict[str, Any]) -> None:
        """Generate CSV artifact files."""
        # Generate trades.csv
        trades_data = results.get('trades', [])
        if trades_data:
            import pandas as pd
            trades_df = pd.DataFrame(trades_data)
            trades_df.to_csv(os.path.join(self.run_dir, "trades.csv"), index=False)
        
        # Generate events.csv
        events_data = results.get('events', [])
        if events_data:
            import pandas as pd
            events_df = pd.DataFrame(events_data)
            events_df.to_csv(os.path.join(self.run_dir, "events.csv"), index=False)
        
        # Generate series.csv
        series_data = results.get('daily_series', [])
        if series_data:
            import pandas as pd
            series_df = pd.DataFrame(series_data)
            series_df.to_csv(os.path.join(self.run_dir, "series.csv"), index=False)
    
    def _update_registry(self, results: Dict[str, Any]) -> None:
        """Update run registry."""
        registry_file = os.path.join("docs", "runs", "run_registry.csv")
        
        # Ensure registry directory exists
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        
        # Create registry entry
        registry_entry = {
            'run_id': self.run_id,
            'timestamp': datetime.now().isoformat(),
            'config_file': self.config_path,
            'status': 'completed',
            'final_equity': results.get('final_equity'),
            'total_trades': results.get('total_trades'),
            'start_date': results.get('start_time'),
            'end_date': results.get('end_time'),
            'run_directory': self.run_dir
        }
        
        # Append to registry
        import pandas as pd
        if os.path.exists(registry_file):
            registry_df = pd.read_csv(registry_file)
            registry_df = pd.concat([registry_df, pd.DataFrame([registry_entry])], ignore_index=True)
        else:
            registry_df = pd.DataFrame([registry_entry])
        
        registry_df.to_csv(registry_file, index=False)
        self.logger.info(f"Registry updated: {registry_file}")
    
    def _mark_run_failed(self, error_message: str) -> None:
        """Mark run as failed."""
        try:
            os.makedirs(self.run_dir, exist_ok=True)
            
            # Create failure manifest
            failure_manifest = {
                'run_id': self.run_id,
                'timestamp': datetime.now().isoformat(),
                'config_file': self.config_path,
                'status': 'failed',
                'error_message': error_message
            }
            
            with open(os.path.join(self.run_dir, "failure_manifest.json"), 'w') as f:
                json.dump(failure_manifest, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to mark run as failed: {str(e)}")
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{timestamp}"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for run executor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)


if __name__ == "__main__":
    """Direct execution for testing."""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "parameter_config.md"
    
    executor = RunExecutor(config_path)
    result = executor.execute_run()
    
    print(f"Run completed with status: {result['status']}")
    if result['status'] == 'success':
        print(f"Run ID: {result['run_id']}")
        print(f"Final equity: ${result['results']['final_equity']:,.2f}")
    else:
        print(f"Error: {result['error']}")