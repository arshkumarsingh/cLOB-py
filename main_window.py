import sys
import random
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QWidget, QTreeWidget, QTreeWidgetItem, QLineEdit, 
                             QComboBox, QSpinBox, QMessageBox, QSplitter, QDialog, QToolBar, QAction)
from PyQt5.QtCore import Qt, QTimer, QMutex, QMutexLocker
from order import Order
from order_book import OrderBook, fetch_current_prices, generate_realistic_order
from custom_order_dialog import CustomOrderDialog
import logging
import redis
import excel_exporter  # Import the new module

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class OrderBookGUI(QMainWindow):
    def __init__(self):
        """
        Initialize the OrderBookGUI class.

        This constructor initializes the following attributes:
        - order_book: an instance of the OrderBook class
        - order_id_counter: a counter for generating unique order IDs
        - symbols: a list of financial symbols
        - current_prices: a dictionary of current prices for the symbols
        - mutex: a QMutex object for thread synchronization

        It also sets up the user interface, starts the auto-update timer, and configures logging.
        """
        super().__init__()  # Call the parent constructor

        # Set the window title
        self.setWindowTitle("Order Book Ladder")

        # Initialize the order book
        self.order_book = OrderBook()

        # Initialize the order ID counter
        self.order_id_counter = 1

        # Initialize the list of financial symbols
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

        # Fetch the current prices for the symbols
        self.current_prices = fetch_current_prices(self.symbols)

        # Initialize the mutex for thread synchronization
        self.mutex = QMutex()

        # Initialize the user interface
        self.init_ui()

        # Start the auto-update timer
        self.start_auto_update()

        # Configure logging
        logging.basicConfig(
            filename='order_book_gui.log',
            level=logging.INFO,
            format='%(asctime)s %(message)s'
        )

    def init_ui(self):
        """
        Initialize the user interface.

        This function sets up the main window's layout and adds various widgets to it.
        """
        print("Initializing UI...")
        # Create the central widget and set it as the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        print("Central widget initialized")

        # Create the main vertical layout
        main_layout = QVBoxLayout(central_widget)
        print("Main vertical layout initialized")

        # Create the toolbar and add it to the main layout
        self.create_toolbar()
        print("Toolbar created")

        # Create the header layout
        header_layout = QHBoxLayout()
        print("Header layout initialized")

        # Create the symbol input combo box and add it to the header layout
        self.symbol_input = QComboBox()
        self.symbol_input.addItems(self.symbols)
        header_layout.addWidget(QLabel("Symbol"))
        header_layout.addWidget(self.symbol_input)
        print("Symbol input combo box added to header layout")

        # Create the price label and add it to the header layout
        self.price_label = QLabel("")
        self.price_label.setStyleSheet("font-size: 16px; color: red;")
        header_layout.addWidget(self.price_label)
        print("Price label added to header layout")

        # Add the header layout to the main layout
        main_layout.addLayout(header_layout)
        print("Header layout added to main layout")

        # Create the splitter and add the buy and sell tree views to it
        splitter = QSplitter(Qt.Horizontal)
        self.buy_tree = self.create_treeview("Buy Orders")
        self.sell_tree = self.create_treeview("Sell Orders")
        splitter.addWidget(self.buy_tree)
        splitter.addWidget(self.sell_tree)
        print("Buy and sell tree views added to splitter")

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)
        print("Splitter added to main layout")

        # Create the bottom layout
        bottom_layout = QHBoxLayout()
        print("Bottom layout initialized")

        # Create the labels and add them to the bottom layout
        self.low_label = QLabel("")
        self.high_label = QLabel("")
        self.open_label = QLabel("")
        self.prev_close_label = QLabel("")
        for label in [self.low_label, self.high_label, self.open_label, self.prev_close_label]:
            label.setStyleSheet("font-size: 12px; color: white;")
            bottom_layout.addWidget(label)
            print(f"{label} added to bottom layout")

        # Add the bottom layout to the main layout
        main_layout.addLayout(bottom_layout)
        print("Bottom layout added to main layout")

        # Create the filter layout and add it to the main layout
        self.create_filter_layout(main_layout)
        print("Filter layout created and added to main layout")

        # Create the statistics layout and add it to the main layout
        self.create_statistics_layout(main_layout)
        print("Statistics layout created and added to main layout")

        # Create the chart layout and add it to the main layout
        self.create_chart_layout(main_layout)
        print("Chart layout created and added to main layout")

        # Create the status label and add it to the main layout
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.status_label)
        print("Status label created and added to main layout")
        print("UI initialization complete")

    def create_toolbar(self):
        """
        Create a toolbar with actions for adding random orders, matching orders,
        canceling orders, exporting to Excel, and adding custom orders.
        """
        # Create the toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add a random order action
        add_random_order_action = QAction("Add Random Order", self)
        add_random_order_action.triggered.connect(self.add_random_order)
        toolbar.addAction(add_random_order_action)

        # Add a match orders action
        match_orders_action = QAction("Match Orders", self)
        match_orders_action.triggered.connect(self.match_orders)
        toolbar.addAction(match_orders_action)

        # Add a cancel order action
        cancel_order_action = QAction("Cancel Order", self)
        cancel_order_action.triggered.connect(self.cancel_order)
        toolbar.addAction(cancel_order_action)

        # Add an export to Excel action
        export_to_excel_action = QAction("Export to Excel", self)
        export_to_excel_action.triggered.connect(self.export_to_excel)
        toolbar.addAction(export_to_excel_action)

        # Add an add custom order action
        add_custom_order_action = QAction("Add Custom Order", self)
        add_custom_order_action.triggered.connect(self.open_custom_order_dialog)
        toolbar.addAction(add_custom_order_action)

    def create_treeview(self, label):
        tree = QTreeWidget()
        tree.setColumnCount(4)  # Add an extra column for execution time
        tree.setHeaderLabels([label, "Orders", "Qty", "Exec Time"])
        return tree

    def create_filter_layout(self, layout):
        """
        Create a layout for filter options and apply button.

        Args:
            layout (QHBoxLayout): The layout to add the filter layout to.
        """
        # Create a horizontal layout for the filter options
        filter_layout = QHBoxLayout()
        
        # Create input fields for minimum price, maximum price, minimum quantity, and maximum quantity
        self.min_price_input = QLineEdit()
        self.max_price_input = QLineEdit()
        self.min_qty_input = QSpinBox()
        self.max_qty_input = QSpinBox()
        
        # Add labels and input fields to the filter layout
        filter_layout.addWidget(QLabel("Min Price"))
        filter_layout.addWidget(self.min_price_input)
        filter_layout.addWidget(QLabel("Max Price"))
        filter_layout.addWidget(self.max_price_input)
        filter_layout.addWidget(QLabel("Min Quantity"))
        filter_layout.addWidget(self.min_qty_input)
        filter_layout.addWidget(QLabel("Max Quantity"))
        filter_layout.addWidget(self.max_qty_input)
        
        # Create a button to apply the filter
        apply_filter_button = QPushButton("Apply Filter")
        apply_filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_filter_button)
        
        # Add the filter layout to the main layout
        layout.addLayout(filter_layout)

    def create_statistics_layout(self, layout):
        stats_layout = QVBoxLayout()
        self.total_buy_orders_label = QLabel("0")
        self.total_sell_orders_label = QLabel("0")
        self.avg_buy_price_label = QLabel("0.00")
        self.avg_sell_price_label = QLabel("0.00")
        
        for label_text, label in [("Total Buy Orders", self.total_buy_orders_label), 
                                  ("Total Sell Orders", self.total_sell_orders_label), 
                                  ("Average Buy Price", self.avg_buy_price_label), 
                                  ("Average Sell Price", self.avg_sell_price_label)]:
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label_text))
            h_layout.addWidget(label)
            stats_layout.addLayout(h_layout)
        
        layout.addLayout(stats_layout)

    def create_chart_layout(self, layout):
        self.fig, self.ax = plt.subplots()
        self.chart_canvas = FigureCanvas(self.fig)
        layout.addWidget(self.chart_canvas)

    def add_random_order(self):
        """
        Adds either one buy and one sell order or a random order to the order book.
        """
        try:
            # Decide whether to add one buy and one sell order or a random order
            if random.random() <= 0.9:
                # Generate one buy and one sell order
                symbol = self.symbol_input.currentText()  # Get the selected symbol
                current_price = self.current_prices[symbol]

                # Generate a buy order
                buy_order = generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)
                buy_order.side = "buy"
                self.order_book.add_order(buy_order)
                self.order_id_counter += 1

                # Generate a sell order
                sell_order = generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)
                sell_order.side = "sell"
                self.order_book.add_order(sell_order)
                self.order_id_counter += 1

                logging.info(f"Buy and sell orders added: {buy_order}, {sell_order}")
            else:
                # Generate a random order
                order = self.generate_random_order()
                self.order_book.add_order(order)
                self.order_id_counter += 1
                logging.info(f"Random order added: {order}")

            self.update_gui()
        except Exception as e:
            # Handle any exceptions that occur during the order addition process
            self.show_error("Failed to add random order", str(e))
            logging.error(f"Failed to add random order: {e}")

    def cancel_order(self):
        """
        Cancels an order with the given order ID.

        This method attempts to cancel an order by calling the `cancel_order` method of the `order_book` object with the provided order ID. If the cancellation is successful, a message box is displayed with the result. The result is also logged using the `logging` module.

        After the order is successfully cancelled, the corresponding order entry is deleted from the Redis database using the `redis_client.delete` method. Finally, the GUI is updated by calling the `update_gui` method.

        If any exception occurs during the cancellation process, an error message box is displayed with the error message. The error is also logged using the `logging` module.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            None
        """
        try:
            order_id = self.order_id_input.text()
            result = self.order_book.cancel_order(order_id)
            QMessageBox.information(self, "Cancel Order", result)
            logging.info(result)
            redis_client.delete(f"order:{order_id}")
            self.update_gui()
        except Exception as e:
            self.show_error("Failed to cancel order", str(e))
            logging.error(f"Failed to cancel order: {e}")

    def match_orders(self):
        """
        Match orders in the order book and update the GUI.

        This function attempts to match orders in the order book and logs the
        result. If no orders are matched, it logs a message saying so.
        Otherwise, it logs a message for each matched order.

        After matching the orders, it updates the GUI.

        Raises:
            Exception: If there is an error matching the orders or updating the GUI.
        """
        try:
            # Match orders in the order book
            matched = self.order_book.match_orders()

            # If no orders are matched, log a message
            if not matched:
                logging.info("No orders matched.")
            else:
                # Log a message for each matched order
                for buy, sell, qty in matched:
                    logging.info(f"Matched {qty} units between buy order {buy.order_id} and sell order {sell.order_id}")

            # Update the GUI
            self.update_gui()
        except Exception as e:
            # Handle any exceptions that occur during the order matching process
            self.show_error("Failed to match orders", str(e))
            logging.error(f"Failed to match orders: {e}")

    def open_custom_order_dialog(self):
        dialog = CustomOrderDialog(self.order_book, self.symbols)
        dialog.exec_()
        self.update_gui()

    def apply_filter(self):
        try:
            min_price = float(self.min_price_input.text())
            max_price = float(self.max_price_input.text())
            min_qty = self.min_qty_input.value()
            max_qty = self.max_qty_input.value()
            
            filtered_buy_orders = [order for _, _, order in self.order_book.buy_orders if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]
            filtered_sell_orders = [order for _, _, order in self.order_book.sell_orders if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]
            
            self.update_tree(self.buy_tree, filtered_buy_orders)
            self.update_tree(self.sell_tree, filtered_sell_orders)
        except Exception as e:
            self.show_error("Failed to apply filter", str(e))
            logging.error(f"Failed to apply filter: {e}")

    def export_to_excel(self):
        try:
            matched_orders = self.order_book.get_order_history()
            result = excel_exporter.export_orders_to_excel(matched_orders)
            QMessageBox.information(self, "Export to Excel", result)
        except Exception as e:
            self.show_error("Failed to export to Excel", str(e))
            logging.error(f"Failed to export to Excel: {e}")

    def generate_random_order(self):
        symbol = self.symbol_input.currentText()  # Get the selected symbol
        current_price = self.current_prices[symbol]
        return generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)

    def update_gui(self):
        """
        Update the GUI with the current state of the order book.

        This function acquires a lock on the GUI mutex to ensure that no other
        thread is modifying the GUI at the same time. It then retrieves the
        current state of the order book using the `get_order_book` method of
        the `OrderBook` class. It updates the buy and sell trees with the
        current state of the buy and sell orders. It also updates the stock
        information, statistics, and chart. Finally, it sets the status label
        to indicate that the GUI has been updated successfully.

        If any exception occurs during this process, it displays an error
        message and logs the details of the exception.
        """
        try:
            # Acquire the GUI mutex lock to ensure exclusive access to the GUI
            with QMutexLocker(self.mutex):
                # Retrieve the current state of the order book
                order_book_state = self.order_book.get_order_book()

                # Update the buy tree with the current state of the buy orders
                self.update_tree(self.buy_tree, order_book_state['buy_orders'])
                # Update the sell tree with the current state of the sell orders
                self.update_tree(self.sell_tree, order_book_state['sell_orders'])

                # Update the stock information
                self.update_stock_info()
                # Update the statistics
                self.update_statistics()
                # Update the chart
                self.update_chart()

                # Set the status label to indicate GUI update success
                self.status_label.setText("Order Book Updated")
                # Log a success message
                logging.info("GUI updated successfully")
        except Exception as e:
            # Display an error message if any exception occurs
            self.show_error("Failed to update GUI", str(e))
            # Log the details of the exception
            logging.error(f"Failed to update GUI: {e}")

    def update_tree(self, tree, orders):
        tree.clear()
        for order in orders:
            item = QTreeWidgetItem([str(order.price), str(len(orders)), str(order.quantity), f"{order.execution_time:.4f} s" if order.execution_time else "N/A"])
            tree.addTopLevelItem(item)

    def update_stock_info(self):
        if self.order_book.last_matched_price is not None:
            last_price = self.order_book.last_matched_price
            current_price = last_price
            price_change = current_price - self.current_prices[self.symbol_input.currentText()]
            percent_change = (price_change / self.current_prices[self.symbol_input.currentText()]) * 100
            self.price_label.setText(f"{current_price:.2f}  {price_change:.2f} ({percent_change:.2f}%)")
            self.price_label.setStyleSheet("color: green;" if price_change >= 0 else "color: red;")
            self.current_prices[self.symbol_input.currentText()] = current_price

    def update_statistics(self):
        buy_orders = [order for _, _, order in self.order_book.buy_orders]
        sell_orders = [order for _, _, order in self.order_book.sell_orders]

        total_buy_orders = len(buy_orders)
        total_sell_orders = len(sell_orders)
        avg_buy_price = sum(order.price for order in buy_orders) / total_buy_orders if total_buy_orders else 0
        avg_sell_price = sum(order.price for order in sell_orders) / total_sell_orders if total_sell_orders else 0

        self.total_buy_orders_label.setText(str(total_buy_orders))
        self.total_sell_orders_label.setText(str(total_sell_orders))
        self.avg_buy_price_label.setText(f"{avg_buy_price:.2f}")
        self.avg_sell_price_label.setText(f"{avg_sell_price:.2f}")

    def update_chart(self):
        try:
            buy_orders = [order for _, _, order in self.order_book.buy_orders]
            sell_orders = [order for _, _, order in self.order_book.sell_orders]

            buy_prices = [order.price for order in buy_orders]
            buy_quantities = [order.quantity for order in buy_orders]
            sell_prices = [order.price for order in sell_orders]
            sell_quantities = [order.quantity for order in sell_orders]

            self.plot_orders(buy_prices, buy_quantities, sell_prices, sell_quantities)
        except Exception as e:
            self.show_error("Failed to update chart", str(e))
            logging.error(f"Failed to update chart: {e}")

    def plot_orders(self, buy_prices, buy_quantities, sell_prices, sell_quantities):
        self.ax.clear()
        self.ax.bar(buy_prices, buy_quantities, color='green', label='Buy Orders')
        self.ax.bar(sell_prices, sell_quantities, color='red', label='Sell Orders')
        self.ax.set_xlabel('Price')
        self.ax.set_ylabel('Quantity')
        self.ax.set_title('Order Distribution')
        self.ax.legend()
        self.chart_canvas.draw()

    def start_auto_update(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_gui)
        timer.start(5000)  # Update every 5 seconds

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

# If this script is run directly (i.e., not imported as a module), create a
# QApplication object and instantiate the OrderBookGUI class.
# 
# The QApplication object is necessary to create a GUI application and to
# handle events. The OrderBookGUI class is the main window of the application.
# 
# The show() method is called on the OrderBookGUI instance to display the
# window. Finally, the exec_() method of the QApplication object is called to
# start the event loop and run the application.
# 
# Note: The if __name__ == "__main__": condition is necessary to prevent the
# code from being executed when this script is imported as a module in another
# script.
if __name__ == "__main__":
    # Create a QApplication object with the command line arguments
    app = QApplication(sys.argv)

    # Instantiate the OrderBookGUI class
    window = OrderBookGUI()

    # Show the main window
    window.show()

    # Start the event loop and run the application
    sys.exit(app.exec_())

