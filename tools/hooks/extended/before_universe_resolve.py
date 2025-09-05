#!/usr/bin/env python3
"""
before_universe_resolve hook - P0 blocking
Validate universe source and format before resolution
"""

import os
import re
import json
from pathlib import Path
from typing import List, Set, Dict, Any
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Validate universe source and format before resolution
    
    Checks:
    - Universe source format (binance:..., file:..., etc.)
    - Symbol format validation  
    - Blacklist/whitelist application
    - De-duplication
    - Source accessibility
    """
    
    ctx.ensure_hook_dir()
    checks = []
    warnings = []
    
    try:
        universe = ctx.universe
        if not universe:
            return HookResult(
                success=False,
                message="No universe specified in context",
                priority="P0",
                should_halt=True
            )
        
        # Parse universe source
        if ':' in universe:
            source_type, source_data = universe.split(':', 1)
        else:
            source_type = 'unknown'
            source_data = universe
        
        checks.append(f"Universe source: {source_type}")
        
        # Validate source type and format
        if source_type == 'binance':
            symbols = [s.strip().upper() for s in source_data.split(',')]
            validation_result = _validate_binance_symbols(symbols)
            
            if not validation_result['valid']:
                return HookResult(
                    success=False,
                    message=f"Invalid Binance symbols: {validation_result['invalid_symbols']}",
                    priority="P0",
                    should_halt=True
                )
            
            checks.append(f"Binance symbols: {len(symbols)} validated")
            
            # Check for duplicates
            unique_symbols = list(set(symbols))
            if len(unique_symbols) != len(symbols):
                warnings.append(f"Duplicate symbols removed: {len(symbols) - len(unique_symbols)}")
                symbols = unique_symbols
                
            validated_symbols = symbols
            
        elif source_type == 'file':
            # File-based universe
            file_path = source_data
            if not os.path.isabs(file_path):
                file_path = os.path.join("data", "universe", file_path)
            
            if not os.path.exists(file_path):
                return HookResult(
                    success=False,
                    message=f"Universe file not found: {file_path}",
                    priority="P0",
                    should_halt=True
                )
            
            try:
                with open(file_path, 'r') as f:
                    if file_path.endswith('.json'):
                        data = json.load(f)
                        if isinstance(data, list):
                            validated_symbols = data
                        elif isinstance(data, dict) and 'symbols' in data:
                            validated_symbols = data['symbols']
                        else:
                            return HookResult(
                                success=False,
                                message=f"Invalid JSON format in {file_path}",
                                priority="P0",
                                should_halt=True
                            )
                    else:
                        # Text file, one symbol per line
                        validated_symbols = [line.strip().upper() for line in f if line.strip()]
                
                checks.append(f"File universe: {len(validated_symbols)} symbols from {file_path}")
                
            except Exception as e:
                return HookResult(
                    success=False,
                    message=f"Error reading universe file {file_path}: {e}",
                    priority="P0",
                    should_halt=True
                )
        
        elif source_type in ['coinbase', 'kraken', 'ftx']:
            # Other exchange formats (basic validation)
            symbols = [s.strip().upper() for s in source_data.split(',')]
            validated_symbols = symbols
            checks.append(f"{source_type} symbols: {len(symbols)} (basic validation)")
            
        else:
            return HookResult(
                success=False,
                message=f"Unsupported universe source type: {source_type}",
                priority="P0",
                should_halt=True
            )
        
        # Apply blacklist/whitelist if configured
        filtered_symbols, filter_stats = _apply_symbol_filters(validated_symbols)
        
        if filter_stats['blacklisted'] > 0:
            warnings.append(f"Blacklisted symbols removed: {filter_stats['blacklisted']}")
        
        if filter_stats['whitelisted'] is not None:
            checks.append(f"Whitelist applied: {filter_stats['whitelisted']} symbols kept")
        
        final_symbol_count = len(filtered_symbols)
        
        # Validate final symbol count
        if final_symbol_count == 0:
            return HookResult(
                success=False,
                message="No symbols remaining after filtering",
                priority="P0",
                should_halt=True
            )
        
        if final_symbol_count > 1000:
            warnings.append(f"Large universe: {final_symbol_count} symbols (may impact performance)")
        
        checks.append(f"Final universe: {final_symbol_count} symbols")
        
        # Store resolved universe for next hooks
        resolved_universe = {
            "source_type": source_type,
            "source_data": source_data,
            "symbols": filtered_symbols,
            "symbol_count": final_symbol_count,
            "warnings": warnings
        }
        
        universe_file = os.path.join(ctx.run_path, "resolved_universe.json")
        os.makedirs(os.path.dirname(universe_file), exist_ok=True)
        
        with open(universe_file, 'w') as f:
            json.dump(resolved_universe, f, indent=2)
        
        # Write hook log
        log_data = {
            "hook": "before_universe_resolve",
            "status": "success",
            "source_type": source_type,
            "symbol_count": final_symbol_count,
            "warnings": len(warnings),
            "checks": checks,
            "details": filter_stats,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        message = f"Universe validated: {final_symbol_count} symbols"
        if warnings:
            message += f" ({len(warnings)} warnings)"
        
        return HookResult(
            success=True,
            message=message,
            priority="P0",
            details={
                "checks": checks,
                "warnings": warnings,
                "symbol_count": final_symbol_count,
                "source_type": source_type
            }
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Unexpected error in before_universe_resolve: {str(e)}",
            priority="P0",
            should_halt=True,
            details={"exception": str(e), "type": type(e).__name__}
        )


def _validate_binance_symbols(symbols: List[str]) -> Dict[str, Any]:
    """Validate Binance symbol format"""
    valid_symbols = []
    invalid_symbols = []
    
    # Binance symbol pattern: base currency + quote currency (e.g., BTCUSDT, ETHBTC)
    symbol_pattern = re.compile(r'^[A-Z0-9]{2,10}[A-Z]{3,6}$')  # 2-10 chars base + 3-6 chars quote
    
    common_quotes = {'USDT', 'BTC', 'ETH', 'BNB', 'BUSD', 'USDC', 'USD', 'EUR'}
    
    for symbol in symbols:
        if symbol_pattern.match(symbol):
            # Additional check: does it end with a known quote currency?
            has_valid_quote = any(symbol.endswith(quote) for quote in common_quotes)
            
            if has_valid_quote:
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(f"{symbol} (unknown quote currency)")
        else:
            invalid_symbols.append(f"{symbol} (invalid format)")
    
    return {
        "valid": len(invalid_symbols) == 0,
        "valid_symbols": valid_symbols,
        "invalid_symbols": invalid_symbols
    }


def _apply_symbol_filters(symbols: List[str]) -> tuple[List[str], Dict[str, Any]]:
    """Apply blacklist and whitelist filters to symbols"""
    
    # Load filters from config (if available)
    blacklist_file = os.path.join("configs", "symbol_blacklist.json")
    whitelist_file = os.path.join("configs", "symbol_whitelist.json")
    
    blacklist = set()
    whitelist = None
    
    # Load blacklist
    if os.path.exists(blacklist_file):
        try:
            with open(blacklist_file, 'r') as f:
                blacklist_data = json.load(f)
                if isinstance(blacklist_data, list):
                    blacklist = set(blacklist_data)
                elif isinstance(blacklist_data, dict) and 'symbols' in blacklist_data:
                    blacklist = set(blacklist_data['symbols'])
        except Exception:
            pass
    
    # Load whitelist
    if os.path.exists(whitelist_file):
        try:
            with open(whitelist_file, 'r') as f:
                whitelist_data = json.load(f)
                if isinstance(whitelist_data, list):
                    whitelist = set(whitelist_data)
                elif isinstance(whitelist_data, dict) and 'symbols' in whitelist_data:
                    whitelist = set(whitelist_data['symbols'])
        except Exception:
            pass
    
    # Apply filters
    original_count = len(symbols)
    filtered_symbols = []
    blacklisted_count = 0
    
    for symbol in symbols:
        # Apply blacklist
        if symbol in blacklist:
            blacklisted_count += 1
            continue
        
        # Apply whitelist (if exists)
        if whitelist is not None and symbol not in whitelist:
            continue
        
        filtered_symbols.append(symbol)
    
    stats = {
        "original_count": original_count,
        "blacklisted": blacklisted_count,
        "whitelisted": len(filtered_symbols) if whitelist is not None else None,
        "final_count": len(filtered_symbols)
    }
    
    return filtered_symbols, stats


if __name__ == "__main__":
    # Test hook
    test_ctx = HookContext(
        run_id="test_universe",
        run_path="./test_run",
        phase="analyzer",
        universe="binance:BTCUSDT,ETHUSDT,ADAUSDT,INVALID",
        hook_name="before_universe_resolve"
    )
    
    result = execute(test_ctx)
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Symbol count: {result.details.get('symbol_count')}")
        print(f"Warnings: {len(result.details.get('warnings', []))}")