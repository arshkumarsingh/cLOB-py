class Order:
    def __init__(self, timestamp, order_id, symbol, price, quantity, side, order_type='limit', stop_price=None, displayed_quantity=None):
        self.timestamp = timestamp
        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_type = order_type
        self.stop_price = stop_price
        self.displayed_quantity = displayed_quantity if displayed_quantity else quantity

    def __repr__(self):
        return (f"Order(timestamp={self.timestamp}, order_id={self.order_id}, symbol={self.symbol}, price={self.price}, "
                f"quantity={self.quantity}, side={self.side}, order_type={self.order_type}, "
                f"stop_price={self.stop_price}, displayed_quantity={self.displayed_quantity})")
