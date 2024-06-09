class Order:
    def __init__(self, timestamp, order_id, price, quantity, side, order_type='limit', stop_price=None, displayed_quantity=None):
        self.timestamp = timestamp
        self.order_id = order_id
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_type = order_type
        self.stop_price = stop_price
        self.displayed_quantity = displayed_quantity if displayed_quantity else quantity

    def __repr__(self):
        return (f"Order(timestamp={self.timestamp}, order_id={self.order_id}, price={self.price}, "
                f"quantity={self.quantity}, side={self.side}, type={self.order_type}, stop_price={self.stop_price}, "
                f"displayed_quantity={self.displayed_quantity})")

    def __lt__(self, other):
        return (self.price, self.timestamp) < (other.price, other.timestamp)
