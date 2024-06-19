import heapq
import time
import logging
import random
from collections import deque
from order import Order
from user import User
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.order_history = deque()
        self.last_matched_price = None
        self.users = []
        self.current_user = None
        logging.basicConfig(filename='order_book.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def add_order(self, order):
        try:
            self.validate_order(order)
            if order.side == "buy":
                heapq.heappush(self.buy_orders, (-order.price, order.timestamp, order))
            else:
                heapq.heappush(self.sell_orders, (order.price, order.timestamp, order))
            logging.info(f"Added order: {order}")
            redis_client.set(f"order:{order.order_id}", order.__repr__())
        except Exception as e:
            logging.error(f"Error adding order: {order}. Error: {str(e)}")
            raise

    def cancel_order(self, order_id):
        for order_list in [self.buy_orders, self.sell_orders]:
            for index, (_, _, order) in enumerate(order_list):
                if order.order_id == order_id:
                    order.cancel()
                    order_list.pop(index)
                    heapq.heapify(order_list)
                    logging.info(f"Order {order_id} cancelled.")
                    redis_client.delete(f"order:{order_id}")
                    return f"Order {order_id} cancelled."
        logging.warning(f"Order {order_id} not found.")
        return f"Order {order_id} not found."

    def match_orders(self):
        matched = []
        while self.buy_orders and self.sell_orders and -self.buy_orders[0][0] >= self.sell_orders[0][0]:
            _, _, buy_order = heapq.heappop(self.buy_orders)
            _, _, sell_order = heapq.heappop(self.sell_orders)
            
            start_time = time.time()

            matched_quantity = min(buy_order.quantity, sell_order.quantity)
            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity

            matched_order = {
                "buy_order_id": buy_order.order_id,
                "sell_order_id": sell_order.order_id,
                "symbol": buy_order.symbol,
                "quantity": matched_quantity,
                "price": sell_order.price,
                "timestamp": int(time.time())
            }

            self.order_history.appendleft(matched_order)
            self.last_matched_price = sell_order.price

            if buy_order.quantity > 0:
                heapq.heappush(self.buy_orders, (-buy_order.price, buy_order.timestamp, buy_order))
            if sell_order.quantity > 0:
                heapq.heappush(self.sell_orders, (sell_order.price, sell_order.timestamp, sell_order))

            end_time = time.time()
            execution_time = end_time - start_time
            buy_order.execute(execution_time)
            sell_order.execute(execution_time)

            logging.info(f"Matched {matched_quantity} units between buy order {buy_order.order_id} and sell order {sell_order.order_id} in {execution_time:.4f} seconds")
            matched.append((buy_order, sell_order, matched_quantity))
            redis_client.set(f"order:{buy_order.order_id}", buy_order.__repr__())
            redis_client.set(f"order:{sell_order.order_id}", sell_order.__repr__())

        return matched

    def get_order_book(self):
        return {
            "buy_orders": [order for _, _, order in self.buy_orders],
            "sell_orders": [order for _, _, order in self.sell_orders]
        }

    def get_order_history(self):
        return list(self.order_history)

    def validate_order(self, order):
        if order.price <= 0 or order.quantity <= 0:
            raise ValueError("Price and quantity must be greater than zero")
        if order.side not in ["buy", "sell"]:
            raise ValueError("Side must be either 'buy' or 'sell'")

    def add_user(self, username, password, role):
        if role not in ["admin", "trader", "viewer"]:
            raise ValueError("Role must be either 'admin', 'trader', or 'viewer'")
        user = User(username, password, role)
        self.users.append(user)
        logging.info(f"User added: {user}")
        redis_client.set(f"user:{username}", user.__repr__())

    def authenticate_user(self, username, password):
        for user in self.users:
            if user.username == username and user.check_password(password):
                self.current_user = user
                logging.info(f"User authenticated: {user}")
                redis_client.set(f"user:{username}", user.__repr__())
                return True
        logging.warning(f"Authentication failed for user: {username}")
        return False

    def get_current_user_role(self):
        return self.current_user.role if self.current_user else None

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
