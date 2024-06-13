import redis

class Order:
    def __init__(self, timestamp, order_id, symbol, price, quantity, side, order_type='limit'):
        self.timestamp = timestamp
        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_type = order_type
        self.execution_time = None  # Add execution time attribute

    def __repr__(self):
        return (f"Order(timestamp={self.timestamp}, order_id={self.order_id}, symbol={self.symbol}, price={self.price}, "
                f"quantity={self.quantity}, side={self.side}, order_type={self.order_type}, execution_time={self.execution_time})")

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
        """Set the execution time for the order."""
        self.execution_time = execution_time
