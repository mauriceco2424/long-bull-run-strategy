"""
Order Manager

Handles order lifecycle management, execution timing, and order book simulation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from enum import Enum
from collections import defaultdict


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class Order:
    """Individual order representation."""
    
    def __init__(self, order_id: str, symbol: str, action: str, quantity: float,
                 order_type: str = "market", limit_price: Optional[float] = None,
                 stop_price: Optional[float] = None, timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict] = None):
        self.order_id = order_id
        self.symbol = symbol
        self.action = action.lower()  # buy, sell, close
        self.quantity = abs(quantity)  # Always positive
        self.order_type = OrderType(order_type.lower())
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
        # Order state
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0.0
        self.remaining_quantity = self.quantity
        self.fills = []  # List of partial fills
        
    def is_fully_filled(self) -> bool:
        return abs(self.remaining_quantity) < 1e-8
    
    def is_buy_order(self) -> bool:
        return self.action in ['buy', 'long']
    
    def is_sell_order(self) -> bool:
        return self.action in ['sell', 'short', 'close']


class OrderManager:
    """
    Manages order lifecycle and execution simulation.
    
    Handles:
    - Order placement and validation
    - Next-bar execution simulation
    - Stop loss and take profit orders
    - Order conflict resolution
    - Realistic fill simulation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize order manager with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Order storage
        self.pending_orders = []  # Orders waiting for execution
        self.order_history = []   # All historical orders
        self.order_counter = 0    # For unique order IDs
        
        # Execution settings
        self.execution_delay = config.get('execution_delay', 1)  # Bars delay
        self.allow_partial_fills = config.get('allow_partial_fills', False)
        self.max_orders_per_symbol = config.get('max_orders_per_symbol', 10)
        
        # Stop loss and take profit settings
        self.sl_tp_enabled = config.get('enable_sl_tp', True)
        
    def add_order(self, order_data: Dict[str, Any]) -> str:
        """
        Add a new order to the pending queue.
        
        Args:
            order_data: Order information dictionary
            
        Returns:
            Order ID if successful, None if rejected
        """
        try:
            # Generate unique order ID
            order_id = f"order_{self.order_counter:06d}"
            self.order_counter += 1
            
            # Create order object
            order = Order(
                order_id=order_id,
                symbol=order_data['symbol'],
                action=order_data['action'],
                quantity=order_data['quantity'],
                order_type=order_data.get('order_type', 'market'),
                limit_price=order_data.get('limit_price'),
                stop_price=order_data.get('stop_price'),
                timestamp=order_data.get('timestamp'),
                metadata=order_data.get('metadata', {})
            )
            
            # Validate order
            if not self._validate_order(order):
                order.status = OrderStatus.REJECTED
                self.order_history.append(order)
                self.logger.warning(f"Order rejected: {order_id}")
                return None
            
            # Check order limits per symbol
            symbol_orders = [o for o in self.pending_orders if o.symbol == order.symbol]
            if len(symbol_orders) >= self.max_orders_per_symbol:
                order.status = OrderStatus.REJECTED
                self.order_history.append(order)
                self.logger.warning(f"Too many pending orders for {order.symbol}")
                return None
            
            # Add to pending orders
            self.pending_orders.append(order)
            
            self.logger.debug(f"Order added: {order_id} - {order.action} {order.quantity} {order.symbol}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error adding order: {str(e)}")
            return None
    
    def process_pending_orders(self, current_ohlcv: Dict[str, Dict[str, float]], 
                             fill_simulator, fee_calculator) -> List[Dict[str, Any]]:
        """
        Process pending orders against current market data.
        
        Args:
            current_ohlcv: Current OHLCV data for all symbols
            fill_simulator: Fill simulator instance
            fee_calculator: Fee calculator instance
            
        Returns:
            List of fill information dictionaries
        """
        if not self.pending_orders:
            return []
        
        fills = []
        orders_to_remove = []
        
        for order in self.pending_orders:
            if order.symbol not in current_ohlcv:
                continue  # No data for this symbol
            
            bar_data = current_ohlcv[order.symbol]
            
            # Check if order should be executed
            should_execute, fill_price = self._should_execute_order(order, bar_data)
            
            if should_execute:
                # Simulate the fill
                fill_info = fill_simulator.simulate_fill(order, bar_data, fill_price)
                
                if fill_info:
                    # Calculate fees
                    fees = fee_calculator.calculate_fees(
                        order.symbol, fill_info['quantity'], fill_info['fill_price']
                    )
                    fill_info['fees'] = fees
                    
                    # Update order state
                    order.filled_quantity += fill_info['quantity']
                    order.remaining_quantity -= fill_info['quantity']
                    order.fills.append(fill_info)
                    
                    # Check if fully filled
                    if order.is_fully_filled():
                        order.status = OrderStatus.FILLED
                        orders_to_remove.append(order)
                    
                    fills.append(fill_info)
                    
                    self.logger.debug(f"Order filled: {order.order_id} - "
                                    f"{fill_info['quantity']} @ {fill_info['fill_price']:.4f}")
        
        # Remove filled orders from pending
        for order in orders_to_remove:
            self.pending_orders.remove(order)
            self.order_history.append(order)
        
        return fills
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successfully cancelled, False otherwise
        """
        for order in self.pending_orders:
            if order.order_id == order_id:
                order.status = OrderStatus.CANCELLED
                self.pending_orders.remove(order)
                self.order_history.append(order)
                self.logger.debug(f"Order cancelled: {order_id}")
                return True
        
        self.logger.warning(f"Order not found for cancellation: {order_id}")
        return False
    
    def cancel_symbol_orders(self, symbol: str) -> int:
        """
        Cancel all pending orders for a symbol.
        
        Args:
            symbol: Symbol to cancel orders for
            
        Returns:
            Number of orders cancelled
        """
        cancelled_count = 0
        orders_to_cancel = [o for o in self.pending_orders if o.symbol == symbol]
        
        for order in orders_to_cancel:
            if self.cancel_order(order.order_id):
                cancelled_count += 1
        
        return cancelled_count
    
    def get_pending_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get pending orders, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of pending orders
        """
        if symbol:
            return [o for o in self.pending_orders if o.symbol == symbol]
        return self.pending_orders.copy()
    
    def has_pending_orders(self, symbol: Optional[str] = None) -> bool:
        """Check if there are pending orders."""
        if symbol:
            return any(o.symbol == symbol for o in self.pending_orders)
        return len(self.pending_orders) > 0
    
    def get_order_stats(self) -> Dict[str, Any]:
        """Get order management statistics."""
        total_orders = len(self.order_history) + len(self.pending_orders)
        filled_orders = len([o for o in self.order_history if o.status == OrderStatus.FILLED])
        cancelled_orders = len([o for o in self.order_history if o.status == OrderStatus.CANCELLED])
        rejected_orders = len([o for o in self.order_history if o.status == OrderStatus.REJECTED])
        
        return {
            'total_orders': total_orders,
            'pending_orders': len(self.pending_orders),
            'filled_orders': filled_orders,
            'cancelled_orders': cancelled_orders,
            'rejected_orders': rejected_orders,
            'fill_rate': filled_orders / total_orders if total_orders > 0 else 0.0
        }
    
    def _validate_order(self, order: Order) -> bool:
        """Validate order parameters."""
        # Check quantity
        if order.quantity <= 0:
            self.logger.error(f"Invalid quantity: {order.quantity}")
            return False
        
        # Check action
        if order.action not in ['buy', 'sell', 'close', 'long', 'short']:
            self.logger.error(f"Invalid action: {order.action}")
            return False
        
        # Check limit order price
        if order.order_type == OrderType.LIMIT and order.limit_price is None:
            self.logger.error("Limit order requires limit_price")
            return False
        
        # Check stop order price
        if order.order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT] and order.stop_price is None:
            self.logger.error("Stop order requires stop_price")
            return False
        
        return True
    
    def _should_execute_order(self, order: Order, bar_data: Dict[str, float]) -> Tuple[bool, Optional[float]]:
        """
        Determine if an order should be executed and at what price.
        
        Args:
            order: Order to check
            bar_data: OHLCV data for the bar
            
        Returns:
            Tuple of (should_execute, fill_price)
        """
        if order.order_type == OrderType.MARKET:
            # Market orders execute at open of next bar
            return True, bar_data['open']
        
        elif order.order_type == OrderType.LIMIT:
            # Limit order execution logic
            if order.is_buy_order():
                # Buy limit: execute if low <= limit_price
                if bar_data['low'] <= order.limit_price:
                    # Fill at limit price or better
                    fill_price = min(order.limit_price, bar_data['open'])
                    return True, fill_price
            else:
                # Sell limit: execute if high >= limit_price
                if bar_data['high'] >= order.limit_price:
                    # Fill at limit price or better
                    fill_price = max(order.limit_price, bar_data['open'])
                    return True, fill_price
        
        elif order.order_type == OrderType.STOP_LOSS:
            # Stop loss execution logic
            if order.is_buy_order():
                # Buy stop: execute if high >= stop_price
                if bar_data['high'] >= order.stop_price:
                    return True, max(order.stop_price, bar_data['open'])
            else:
                # Sell stop: execute if low <= stop_price
                if bar_data['low'] <= order.stop_price:
                    return True, min(order.stop_price, bar_data['open'])
        
        elif order.order_type == OrderType.TAKE_PROFIT:
            # Take profit execution logic (similar to limit orders)
            if order.is_buy_order():
                if bar_data['low'] <= order.stop_price:
                    return True, min(order.stop_price, bar_data['open'])
            else:
                if bar_data['high'] >= order.stop_price:
                    return True, max(order.stop_price, bar_data['open'])
        
        return False, None
    
    def clear_all_orders(self) -> None:
        """Clear all pending orders (for cleanup)."""
        for order in self.pending_orders:
            order.status = OrderStatus.CANCELLED
            self.order_history.append(order)
        
        self.pending_orders.clear()
        self.logger.info("All pending orders cleared")