from datetime import datetime

class Order:
    def __init__(self, timestamp, order_id, symbol, price, quantity, side, order_type='limit'):
        """
        Initialize an Order object.

        Args:
            timestamp (int): The timestamp of the order creation in milliseconds.
            order_id (str): The unique identifier for the order.
            symbol (str): The symbol for which the order is placed.
            price (float): The price of the symbol at which the order is placed.
            quantity (int): The quantity of the symbol to be traded.
            side (str): The side of the order ("buy" or "sell").
            order_type (str, optional): The type of the order ("limit" or "market", default is "limit").
        """
        
        # Initialize the timestamp of the order creation
        self.timestamp = timestamp
        
        # Initialize the unique identifier for the order
        self.order_id = order_id
        
        # Initialize the symbol for which the order is placed
        self.symbol = symbol
        
        # Initialize the price of the symbol at which the order is placed
        self.price = price
        
        # Initialize the quantity of the symbol to be traded
        self.quantity = quantity
        
        # Initialize the side of the order ("buy" or "sell")
        self.side = side
        
        # Initialize the type of the order ("limit" or "market", default is "limit")
        self.order_type = order_type
        
        # Initialize the execution time of the order as None (not executed yet)
        self.execution_time = None
        
        # Initialize the status of the order as "pending" (not yet executed or cancelled)
        self.status = 'pending'

    def __repr__(self):
        return (f"Order(timestamp={self.timestamp}, order_id={self.order_id}, symbol={self.symbol}, price={self.price}, "
                f"quantity={self.quantity}, side={self.side}, order_type={self.order_type}, execution_time={self.execution_time}, status={self.status})")

    def is_valid(self):
        """Validate the order details."""
        if self.price <= 0 or self.quantity <= 0:
            return False
        if self.side not in ["buy", "sell"]:
            return False
        if self.order_type not in ["limit", "market"]:
            return False
        return True

    def update_quantity(self, quantity):
        """Update the order quantity."""
        if quantity > 0:
            self.quantity = quantity
        else:
            raise ValueError("Quantity must be greater than zero")

    def execute(self, execution_time):
        """
        Set the execution time for the order and update its status.

        Args:
            execution_time (float): The time taken to execute the order in seconds.
        """
        # Update the status and execution time in a single assignment
        self.status, self.execution_time = 'fulfilled', execution_time

    def cancel(self):
        """Cancel the order."""
        self.status = 'canceled'

    def modify(self, price=None, quantity=None):
        """Modify the order."""
        if price:
            self.price = price
        if quantity:
            self.update_quantity(quantity)
