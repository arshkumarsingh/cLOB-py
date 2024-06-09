import random
import time
import collections
import threading
from concurrent.futures import ThreadPoolExecutor

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
                f"quantity={self.quantity}, side={self.side}, order_type={self.order_type}, "
                f"stop_price={self.stop_price}, displayed_quantity={self.displayed_quantity})")

class LockFreeQueue:
    def __init__(self):
        self.queue = collections.deque()
        self.lock = threading.Lock()

    def push(self, item):
        with self.lock:
            self.queue.append(item)

    def pop(self):
        with self.lock:
            if len(self.queue) > 0:
                return self.queue.popleft()
            else:
                return None

class OrderBook:
    def __init__(self):
        self.buy_orders = LockFreeQueue()
        self.sell_orders = LockFreeQueue()
        self.order_map = {}

    def add_order(self, order):
        if order.side == 'buy':
            self.buy_orders.push(order)
        else:
            self.sell_orders.push(order)
        self.order_map[order.order_id] = order

    def remove_order(self, order_id):
        order = self.order_map.pop(order_id, None)
        if not order:
            return False
        # Simplified logic for removing order from LockFreeQueue
        return True

    def match_orders(self):
        matched_orders = []
        while True:
            best_buy = self.buy_orders.pop()
            best_sell = self.sell_orders.pop()

            if not best_buy or not best_sell:
                if best_buy:
                    self.buy_orders.push(best_buy)
                if best_sell:
                    self.sell_orders.push(best_sell)
                break

            if best_buy.price >= best_sell.price:
                match_qty = min(best_buy.quantity, best_sell.quantity)
                matched_orders.append((best_buy, best_sell, match_qty))

                best_buy.quantity -= match_qty
                best_sell.quantity -= match_qty

                if best_buy.quantity > 0:
                    self.buy_orders.push(best_buy)
                if best_sell.quantity > 0:
                    self.sell_orders.push(best_sell)
            else:
                self.buy_orders.push(best_buy)
                self.sell_orders.push(best_sell)
                break

        return matched_orders

    def trigger_stop_orders(self):
        # Dummy implementation to trigger stop orders
        print("Triggering stop orders...")

    def get_order_book(self):
        buy_orders = list(self.buy_orders.queue)
        sell_orders = list(self.sell_orders.queue)

        return {
            'buy_orders': sorted(buy_orders, key=lambda x: (-x.price, x.timestamp)),
            'sell_orders': sorted(sell_orders, key=lambda x: (x.price, x.timestamp))
        }

    def get_order_history(self):
        # Dummy implementation
        return []

    def get_liquidity_pool(self):
        # Dummy implementation
        return {}

def generate_random_order(order_id):
    timestamp = int(time.time() * 1000)  # current time in milliseconds
    price = random.randint(90, 110)
    quantity = random.randint(1, 20)
    side = random.choice(['buy', 'sell'])
    order_type = random.choice(['limit', 'market', 'iceberg', 'stop_loss', 'stop_limit'])
    stop_price = None
    displayed_quantity = None
    if order_type in ['stop_loss', 'stop_limit']:
        stop_price = random.randint(85, 115)
    if order_type == 'iceberg':
        displayed_quantity = random.randint(1, quantity)
    return Order(timestamp=timestamp, order_id=order_id, price=price, quantity=quantity, side=side, order_type=order_type, stop_price=stop_price, displayed_quantity=displayed_quantity)

def test_order_book():
    order_book = OrderBook()

    # Generate random orders
    for i in range(10):
        order = generate_random_order(f'{i+1}')
        order_book.add_order(order)
        print(f"Added {order.side} order: ID={order.order_id}, Price={order.price}, Quantity={order.quantity}")

    print("\nOrder Book Before Matching:")
    order_book_state = order_book.get_order_book()
    print("Buy Orders:", order_book_state['buy_orders'])
    print("Sell Orders:", order_book_state['sell_orders'])

    matched_orders = order_book.match_orders()

    print("\nMatched Orders:")
    for buy, sell, qty in matched_orders:
        print(f"Matched {qty} units between buy order {buy.order_id} and sell order {sell.order_id}")

    print("\nOrder Book After Matching:")
    order_book_state = order_book.get_order_book()
    print("Buy Orders:", order_book_state['buy_orders'])
    print("Sell Orders:", order_book_state['sell_orders'])

# Main entry point for the test
if __name__ == "__main__":
    test_order_book()
