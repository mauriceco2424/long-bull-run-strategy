#!/usr/bin/env python3
"""
after_universe_resolve hook - P2 nonblocking
Emit resolved symbol count and warnings after universe resolution
"""

import os
import json
from typing import Dict, Any
from ..lib.hook_context import HookContext, HookResult


def execute(ctx: HookContext) -> HookResult:
    """
    Report universe resolution results and emit warnings
    
    Actions:
    - Log final symbol count and composition
    - Warn if symbol count is below recommended minimum
    - Report any symbols that were filtered out
    - Generate universe summary for documentation
    """
    
    ctx.ensure_hook_dir()
    actions = []
    warnings = []
    
    try:
        # Look for resolved universe file
        universe_file = os.path.join(ctx.run_path, "resolved_universe.json")
        
        if not os.path.exists(universe_file):
            # Try to parse from context directly
            if ctx.universe:
                actions.append("No resolved_universe.json found, parsing from context")
                universe_data = _parse_universe_from_context(ctx)
            else:
                return HookResult(
                    success=False,
                    message="No universe data found in resolved file or context",
                    priority="P2"
                )
        else:
            with open(universe_file, 'r') as f:
                universe_data = json.load(f)
                actions.append("Loaded resolved universe data")
        
        symbol_count = universe_data.get('symbol_count', 0)
        source_type = universe_data.get('source_type', 'unknown')
        symbols = universe_data.get('symbols', [])
        
        # Generate summary
        summary_lines = [
            f"Universe resolved: {symbol_count} symbols",
            f"Source: {source_type}",
            f"Symbols: {', '.join(symbols[:10])}" + ("..." if len(symbols) > 10 else "")
        ]
        
        actions.append("Universe summary generated")
        
        # Check for warnings and recommendations
        if symbol_count < 5:
            warnings.append(f"Low symbol count: {symbol_count} < 5 (may not provide sufficient diversification)")
        
        if symbol_count > 500:
            warnings.append(f"High symbol count: {symbol_count} > 500 (may impact performance)")
        
        # Analyze symbol composition (for supported exchanges)
        if source_type == 'binance' and symbols:
            composition = _analyze_symbol_composition(symbols)
            summary_lines.append(f"Quote currencies: {', '.join(composition['quote_currencies'])}")
            summary_lines.append(f"Most common quote: {composition['most_common_quote']} ({composition['most_common_count']} symbols)")
            
            if composition['most_common_count'] / symbol_count > 0.9:
                warnings.append(f"Highly concentrated in {composition['most_common_quote']}: {composition['most_common_count']}/{symbol_count} symbols")
        
        # Check for any resolution warnings
        if 'warnings' in universe_data and universe_data['warnings']:
            warnings.extend(universe_data['warnings'])
        
        # Print console summary (observability)
        print("\n" + "-" * 50)
        print("UNIVERSE RESOLUTION SUMMARY")
        print("-" * 50)
        for line in summary_lines:
            print(line)
        
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  • {warning}")
        print("-" * 50 + "\n")
        
        # Write summary to file
        summary_file = os.path.join(ctx.run_path, "universe_summary.json")
        summary_data = {
            "symbol_count": symbol_count,
            "source_type": source_type,
            "composition": _analyze_symbol_composition(symbols) if symbols else {},
            "warnings": warnings,
            "summary": summary_lines,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        actions.append(f"Summary written to {summary_file}")
        
        # Write hook log
        log_data = {
            "hook": "after_universe_resolve",
            "status": "success",
            "symbol_count": symbol_count,
            "source_type": source_type,
            "warnings_count": len(warnings),
            "actions": actions,
            "summary": summary_lines,
            "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None
        }
        
        with open(ctx.hook_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        message = f"Universe summary: {symbol_count} {source_type} symbols"
        if warnings:
            message += f" ({len(warnings)} warnings)"
        
        return HookResult(
            success=True,
            message=message,
            priority="P2",
            details={
                "actions": actions,
                "warnings": warnings,
                "symbol_count": symbol_count,
                "source_type": source_type,
                "summary": summary_lines
            }
        )
        
    except Exception as e:
        return HookResult(
            success=False,
            message=f"Error in after_universe_resolve: {str(e)}",
            priority="P2",
            details={"exception": str(e), "type": type(e).__name__}
        )


def _parse_universe_from_context(ctx: HookContext) -> Dict[str, Any]:
    """Parse universe data directly from context when resolved file not available"""
    
    universe = ctx.universe
    if ':' in universe:
        source_type, source_data = universe.split(':', 1)
        symbols = [s.strip().upper() for s in source_data.split(',')]
    else:
        source_type = 'unknown'
        symbols = []
    
    return {
        "source_type": source_type,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "warnings": []
    }


def _analyze_symbol_composition(symbols: list) -> Dict[str, Any]:
    """Analyze the composition of trading symbols"""
    
    if not symbols:
        return {}
    
    # Extract quote currencies (assuming Binance format)
    quote_currencies = {}
    common_quotes = ['USDT', 'BTC', 'ETH', 'BNB', 'BUSD', 'USDC', 'USD', 'EUR']
    
    for symbol in symbols:
        quote = None
        for common_quote in sorted(common_quotes, key=len, reverse=True):  # Check longest first
            if symbol.endswith(common_quote):
                quote = common_quote
                break
        
        if quote:
            quote_currencies[quote] = quote_currencies.get(quote, 0) + 1
        else:
            # Try to guess quote currency (last 3-6 chars)
            for length in [4, 3, 5, 6]:  # USDT, BTC, BUSD, etc.
                if len(symbol) > length:
                    potential_quote = symbol[-length:]
                    if potential_quote.isalpha():
                        quote_currencies[potential_quote] = quote_currencies.get(potential_quote, 0) + 1
                        break
    
    if quote_currencies:
        most_common_quote = max(quote_currencies.items(), key=lambda x: x[1])
        return {
            "quote_currencies": list(quote_currencies.keys()),
            "quote_distribution": quote_currencies,
            "most_common_quote": most_common_quote[0],
            "most_common_count": most_common_quote[1],
            "quote_diversity": len(quote_currencies)
        }
    else:
        return {
            "quote_currencies": [],
            "quote_distribution": {},
            "most_common_quote": "unknown",
            "most_common_count": 0,
            "quote_diversity": 0
        }


if __name__ == "__main__":
    # Test hook
    import tempfile
    import shutil
    
    test_dir = tempfile.mkdtemp()
    
    # Create test resolved universe file
    universe_data = {
        "source_type": "binance",
        "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"],
        "symbol_count": 5,
        "warnings": []
    }
    
    universe_file = os.path.join(test_dir, "resolved_universe.json")
    with open(universe_file, 'w') as f:
        json.dump(universe_data, f)
    
    test_ctx = HookContext(
        run_id="test_universe",
        run_path=test_dir,
        phase="analyzer",
        universe="binance:BTCUSDT,ETHUSDT,ADAUSDT,DOTUSDT,LINKUSDT",
        hook_name="after_universe_resolve"
    )
    
    try:
        result = execute(test_ctx)
        print(f"Result: {result.success}")
        print(f"Message: {result.message}")
        if result.details:
            print(f"Actions: {len(result.details.get('actions', []))}")
            print(f"Symbol count: {result.details.get('symbol_count')}")
    finally:
        shutil.rmtree(test_dir)