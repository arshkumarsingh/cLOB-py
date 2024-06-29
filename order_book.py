import heapq
import time
import logging
import random
from collections import deque
from typing import Dict, List, Tuple, Union
from order import Order
from user import User

class OrderBook:
    def __init__(self):
        """
        Initializes a new instance of the OrderBook class.

        This constructor initializes the following attributes:
        - buy_orders: a list to store buy orders
        - sell_orders: a list to store sell orders
        - order_history: a deque to store the history of orders
        - last_matched_price: a variable to store the last matched price
        - users: a list to store users
        - current_user: a variable to store the current user

        It also sets up logging with a filename 'order_book.log', level INFO, and a format of '%(asctime)s %(message)s'.
        """
        self.buy_orders = []
        self.sell_orders = []
        self.order_history = deque()
        self.last_matched_price = None
        self.users = []
        self.current_user = None
        logging.basicConfig(filename='order_book.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def add_order(self, order):
        """
        Adds the given order to the order book.
        
        Parameters:
            order: Order - the order to be added to the order book
        
        Raises:
            Exception: If there is an error adding the order
        
        Returns:
            None
        """
        try:
            self.validate_order(order)
            if order.side == "buy":
                heapq.heappush(self.buy_orders, (-order.price, order.timestamp, order))
            else:
                heapq.heappush(self.sell_orders, (order.price, order.timestamp, order))
            logging.info(f"Added order: {order}")
        except Exception as e:
            logging.error(f"Error adding order: {order}. Error: {str(e)}")
            raise

    def cancel_order(self, order_id):
        """
        Cancels an order by its ID.

        Args:
            order_id (str): The ID of the order to be cancelled.

        Returns:
            str: A message indicating whether the order was cancelled or not.

        Raises:
            None.

        Examples:
            >>> order_book = OrderBook()
            >>> order_book.add_order(Order("buy", 10, 100))
            >>> order_book.add_order(Order("sell", 5, 100))
            >>> order_book.cancel_order("1")
            "Order 1 cancelled."
            >>> order_book.cancel_order("2")
            "Order 2 not found."
        """
        for order_list in [self.buy_orders, self.sell_orders]:
            for index, (_, _, order) in enumerate(order_list):
                if order.order_id == order_id:
                    order.cancel()
                    order_list.pop(index)
                    heapq.heapify(order_list)
                    logging.info(f"Order {order_id} cancelled.")
                    return f"Order {order_id} cancelled."
        logging.warning(f"Order {order_id} not found.")
        return f"Order {order_id} not found."

    def match_orders(self) -> List[Tuple[Order, Order, int]]:
        """
        Matches buy and sell orders based on quantity and price, updates order quantities,
        creates matched orders, logs the match, and returns a list of matched orders.

        :return: A list of tuples containing the matched orders, their quantities,
                 and the timestamp of the match.
        :rtype: List[Tuple[Order, Order, int]]
        """
        matched: List[Tuple[Order, Order, int]] = []

        while self.buy_orders and self.sell_orders and -self.buy_orders[0][0] >= self.sell_orders[0][0]:
            buy_price, _, buy_order = self.buy_orders[0]
            sell_price, _, sell_order = self.sell_orders[0]

            matched_quantity = min(buy_order.quantity, sell_order.quantity)
            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity

            matched_order = {
                "buy_order_id": str(buy_order.order_id),
                "sell_order_id": str(sell_order.order_id),
                "symbol": buy_order.symbol,
                "quantity": matched_quantity,
                "price": int(sell_price),
                "timestamp": int(time.time()),
            }

            self.order_history.appendleft(matched_order)
            self.last_matched_price = sell_price

            if buy_order.quantity:
                heapq.heappush(self.buy_orders, (-buy_price, buy_order.timestamp, buy_order))
            else:
                heapq.heappop(self.buy_orders)

            if sell_order.quantity:
                heapq.heappush(self.sell_orders, (sell_price, sell_order.timestamp, sell_order))
            else:
                heapq.heappop(self.sell_orders)

            buy_order.execute(0)
            sell_order.execute(0)

            logging.info(
                f"Matched {matched_quantity} units between buy order {buy_order.order_id}"
                f" and sell order {sell_order.order_id}"
            )
            matched.append((buy_order, sell_order, matched_quantity))

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
        """
        Adds a new user to the system with the specified username, password, and role.

        Parameters:
            username (str): The username of the new user.
            password (str): The password of the new user.
            role (str): The role of the new user, which must be 'admin', 'trader', or 'viewer'.

        Returns:
            None
        """
        if role not in ["admin", "trader", "viewer"]:
            raise ValueError("Role must be either 'admin', 'trader', or 'viewer']")
        user = User(username, password, role)
        self.users.append(user)
        logging.info(f"User added: {user}")

    def authenticate_user(self, username, password):
        for user in self.users:
            if user.username == username and user.check_password(password):
                self.current_user = user
                logging.info(f"User authenticated: {user}")
                return True
        logging.warning(f"Authentication failed for user: {username}")
        return False

    def get_current_user_role(self):
        return self.current_user.role if self.current_user else None

def fetch_current_prices(symbols):
    """
    Fetches the current prices for a list of symbols.

    Args:
        symbols (list): A list of symbols for which to fetch the current prices.

    Returns:
        dict: A dictionary mapping each symbol to its current price, which is a random float between 100 and 500.
    """
    prices = {}
    for symbol in symbols:
        prices[symbol] = random.uniform(100, 500)
    return prices

def generate_realistic_order(order_id, symbol, current_price):
    """
    Generates a realistic order with randomized attributes.

    Args:
        order_id (str): The unique identifier for the order.
        symbol (str): The symbol for which the order is placed.
        current_price (float): The current price of the symbol.

    Returns:
        Order: An instance of the Order class representing the generated order.
    """
    side = random.choice(["buy", "sell"])
    price = current_price * random.uniform(0.95, 1.05)
    quantity = random.randint(1, 100)
    order_type = random.choice(["limit", "market"])
    timestamp = int(time.time() * 1000)
    return Order(timestamp, order_id, symbol, price, quantity, side, order_type)
