import random
import time

class Order:
    def __init__(self, timestamp, order_id, symbol, price, quantity, side, order_type):
        self.timestamp = timestamp
        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_type = order_type

class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.order_history = []
        self.last_matched_price = None

    def add_order(self, order):
        if order.side == "buy":
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda x: (-x.price, x.timestamp))
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda x: (x.price, x.timestamp))

    def cancel_order(self, order_id):
        for order_list in [self.buy_orders, self.sell_orders]:
            for order in order_list:
                if order.order_id == order_id:
                    order_list.remove(order)
                    return f"Order {order_id} cancelled."
        return f"Order {order_id} not found."

    def match_orders(self):
        matched = []
        while self.buy_orders and self.sell_orders and self.buy_orders[0].price >= self.sell_orders[0].price:
            buy_order = self.buy_orders[0]
            sell_order = self.sell_orders[0]
            matched_quantity = min(buy_order.quantity, sell_order.quantity)

            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity

            self.order_history.append({
                "buy_order_id": buy_order.order_id,
                "sell_order_id": sell_order.order_id,
                "symbol": buy_order.symbol,
                "quantity": matched_quantity,
                "price": sell_order.price,
                "timestamp": int(time.time())
            })

            self.last_matched_price = sell_order.price

            if buy_order.quantity == 0:
                self.buy_orders.pop(0)
            if sell_order.quantity == 0:
                self.sell_orders.pop(0)

            matched.append((buy_order, sell_order, matched_quantity))

        return matched

    def get_order_book(self):
        return {
            "buy_orders": self.buy_orders,
            "sell_orders": self.sell_orders
        }

    def get_order_history(self):
        return self.order_history

def fetch_current_prices(symbols):
    prices = {}
    for symbol in symbols:
        prices[symbol] = random.uniform(100, 500)
    return prices

def generate_realistic_order(order_id, symbol, current_price):
    side = random.choice(["buy", "sell"])
    price = current_price * random.uniform(0.95, 1.05)
    quantity = random.randint(1, 100)
    order_type = random.choice(["limit", "market"])
    timestamp = int(time.time() * 1000)
    return Order(timestamp, order_id, symbol, price, quantity, side, order_type)
