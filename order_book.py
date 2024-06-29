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

        - buy_orders: A list to store buy orders.
        - sell_orders: A list to store sell orders.
        - order_history: A deque to store the history of orders.
        - last_matched_price: A variable to store the last matched price.
        - users: A list to store users.
        - current_user: A variable to store the current user.

        It also sets up logging with a filename 'order_book.log', level INFO,
        and a format of '%(asctime)s %(message)s'.

        """
        # Initialize attributes
        self.buy_orders = []  # List to store buy orders
        self.sell_orders = []  # List to store sell orders
        self.order_history = deque()  # Deque to store the history of orders
        self.last_matched_price = None  # Variable to store the last matched price
        self.users = []  # List to store users
        self.current_user = None  # Variable to store the current user

        # Set up logging
        logging.basicConfig(
            filename='order_book.log',
            level=logging.INFO,
            format='%(asctime)s %(message)s'
        )

    def add_order(self, order):
        """
        Adds the given order to the order book.

        Args:
            order (Order): The order to be added to the order book.

        Raises:
            Exception: If there is an error adding the order.

        Returns:
            None
        """
        try:
            # Validate the order before adding it to the order book.
            self.validate_order(order)

            # Determine the heap to push the order into based on the order side.
            if order.side == "buy":
                heap = self.buy_orders
            else:
                heap = self.sell_orders

            # Push the order into the heap with the price and timestamp as the key.
            heapq.heappush(heap, (order.price, order.timestamp, order))

            # Log the successful addition of the order.
            logging.info(f"Added order: {order}")

        except Exception as e:
            # Log the error caused by failure to add the order.
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
        # Iterate over the buy and sell order lists
        for order_list in [self.buy_orders, self.sell_orders]:
            # Iterate over the orders in the order list
            for index, (_, _, order) in enumerate(order_list):
                # Check if the order ID matches the given order ID
                if order.order_id == order_id:
                    # Cancel the order
                    order.cancel()

                    # Remove the order from the order list
                    order_list.pop(index)

                    # Rebuild the heap to maintain the heap property
                    heapq.heapify(order_list)

                    # Log the cancellation of the order
                    logging.info(f"Order {order_id} cancelled.")

                    # Return a success message
                    return f"Order {order_id} cancelled."

        # If the order is not found, log a warning and return an error message
        logging.warning(f"Order {order_id} not found.")
        return f"Order {order_id} not found."

    def match_orders(self) -> List[Tuple[Order, Order, int]]:
        """
        Matches buy and sell orders based on quantity and price, updates order quantities,
        creates matched orders, logs the match, and returns a list of matched orders.

        Returns:
            A list of tuples containing the matched orders, their quantities,
            and the timestamp of the match.
        """
        # Initialize an empty list to store the matched orders
        matched: List[Tuple[Order, Order, int]] = []

        # Print a starting message
        print("Starting order matching...")

        # Continue matching orders until there are no more buy or sell orders,
        # or the best buy order's price is greater than the best sell order's price
        while self.buy_orders and self.sell_orders and -self.buy_orders[0][0] >= self.sell_orders[0][0]:
            # Print a message for each iteration
            print("Matching orders...")

            # Get the first buy and sell orders
            buy_price, _, buy_order = self.buy_orders[0]
            sell_price, _, sell_order = self.sell_orders[0]

            # Calculate the quantity to match between the buy and sell orders
            matched_quantity = min(buy_order.quantity, sell_order.quantity)

            # Update the quantities of the buy and sell orders
            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity

            # Create a dictionary to represent the matched order
            matched_order = {
                "buy_order_id": str(buy_order.order_id),
                "sell_order_id": str(sell_order.order_id),
                "symbol": buy_order.symbol,
                "quantity": matched_quantity,
                "price": int(sell_price),
                "timestamp": int(time.time()),
            }

            # Add the matched order to the order history
            self.order_history.appendleft(matched_order)

            # Update the last matched price
            self.last_matched_price = sell_price

            # If the buy order has remaining quantity, push it back into the buy orders heap
            if buy_order.quantity:
                heapq.heappush(self.buy_orders, (-buy_price, buy_order.timestamp, buy_order))
            # Otherwise, remove the buy order from the heap
            else:
                heapq.heappop(self.buy_orders)

            # If the sell order has remaining quantity, push it back into the sell orders heap
            if sell_order.quantity:
                heapq.heappush(self.sell_orders, (sell_price, sell_order.timestamp, sell_order))
            # Otherwise, remove the sell order from the heap
            else:
                heapq.heappop(self.sell_orders)

            # Execute the buy and sell orders
            buy_order.execute(0)
            sell_order.execute(0)

            # Log the match
            logging.info(
                f"Matched {matched_quantity} units between buy order {buy_order.order_id}"
                f" and sell order {sell_order.order_id}"
            )

            # Add the matched order to the list of matched orders
            matched.append((buy_order, sell_order, matched_quantity))

            # Print a message for each iteration
            print("Orders matched.")

        # Print a completion message
        print("Order matching completed.")

        # Return the list of matched orders
        return matched

    def get_order_book(self) -> Dict[str, List[Order]]:
        """
        Returns a dictionary representation of the order book.

        Returns:
            Dict[str, List[Order]]: A dictionary with keys "buy_orders" and "sell_orders",
            each containing a list of Order objects.
        """
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
        """
        Authenticates a user with the given username and password.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            bool: True if the user is authenticated successfully, False otherwise.
        """
        # Iterate through the list of users
        for user in self.users:
            # Check if the username and password match
            if user.username == username and user.check_password(password):
                # Set the current user to the authenticated user
                self.current_user = user
                # Log the successful authentication
                logging.info(f"User authenticated: {user}")
                # Return True to indicate successful authentication
                return True
        # Log the failed authentication attempt
        logging.warning(f"Authentication failed for user: {username}")
        # Return False to indicate failed authentication
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

    This function generates a random order with a unique order ID, a symbol, 
    a current price, a side (either "buy" or "sell"), a price, a quantity, 
    an order type (either "limit" or "market"), and a timestamp.

    Args:
        order_id (str): The unique identifier for the order.
        symbol (str): The symbol for which the order is placed.
        current_price (float): The current price of the symbol.

    Returns:
        Order: An instance of the Order class representing the generated order.
    """
    # Generate a random side of the order ("buy" or "sell")
    side = random.choice(["buy", "sell"])

    # Generate a random price for the order within 5% of the current price
    price = current_price * random.uniform(0.95, 1.05)

    # Generate a random quantity for the order between 1 and 100
    quantity = random.randint(1, 100)

    # Generate a random order type ("limit" or "market")
    order_type = random.choice(["limit", "market"])

    # Generate a timestamp for the order using the current time in milliseconds
    timestamp = int(time.time() * 1000)

    # Create and return a new instance of the Order class with the generated attributes
    return Order(timestamp, order_id, symbol, price, quantity, side, order_type)
