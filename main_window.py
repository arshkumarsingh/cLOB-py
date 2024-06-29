"""
This module contains the main GUI class for the Order Book application.
"""

import sys
import random
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QTreeWidget, QTreeWidgetItem, QLineEdit, 
    QComboBox, QSpinBox, QMessageBox, QSplitter, QDialog, QToolBar, QAction
)
from PyQt5.QtCore import Qt, QTimer, QMutex, QMutexLocker

# Import the Order and OrderBook classes from the order module
from order import Order
from order_book import OrderBook

# Import the functions for fetching current prices and generating realistic orders
from order_book import fetch_current_prices, generate_realistic_order

# Import the CustomOrderDialog class from the custom_order_dialog module
from custom_order_dialog import CustomOrderDialog

# Import the logging module for debugging and error handling
import logging

# Import the redis module for accessing the Redis database
import redis

# Import the excel_exporter module for exporting data to Excel
import excel_exporter

# Create a logger for the main_window module
logger = logging.getLogger(__name__)

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
        # Create the central widget and set it as the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the main vertical layout
        main_layout = QVBoxLayout(central_widget)

        # Create the toolbar and add it to the main layout
        self.create_toolbar()

        # Create the header layout
        self.header_layout = QHBoxLayout()
        main_layout.addLayout(self.header_layout)

        # Create the splitter and add the buy and sell tree views to it
        splitter = QSplitter(Qt.Horizontal)
        self.buy_tree = self.create_treeview("Buy Orders")
        self.sell_tree = self.create_treeview("Sell Orders")
        splitter.addWidget(self.buy_tree)
        splitter.addWidget(self.sell_tree)
        main_layout.addWidget(splitter)

        # Create the bottom layout
        self.bottom_layout = QHBoxLayout()
        main_layout.addLayout(self.bottom_layout)

        # Create the filter layout and add it to the main layout
        self.create_filter_layout()

        # Create the statistics layout and add it to the main layout
        self.create_statistics_layout()

        # Create the chart layout and add it to the main layout
        self.create_chart_layout()

        # Create the status label and add it to the main layout
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.status_label)

        # Add all the widgets to the main layout in one pass
        self.header_layout.addWidget(QLabel("Symbol"))
        self.header_layout.addWidget(self.symbol_input)
        self.header_layout.addWidget(self.price_label)

        self.bottom_layout.addWidget(self.low_label)
        self.bottom_layout.addWidget(self.high_label)
        self.bottom_layout.addWidget(self.open_label)
        self.bottom_layout.addWidget(self.prev_close_label)

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
        """
        Create a layout for displaying statistics.

        Args:
            layout (QVBoxLayout): The layout to add the statistics layout to.
        """
        # Create a vertical layout for the statistics
        stats_layout = QVBoxLayout()
        
        # Create labels for total buy and sell orders, average buy and sell prices
        self.total_buy_orders_label = QLabel("0")
        self.total_sell_orders_label = QLabel("0")
        self.avg_buy_price_label = QLabel("0.00")
        self.avg_sell_price_label = QLabel("0.00")
        
        # Add labels and their corresponding values to the statistics layout
        for label_text, label in [("Total Buy Orders", self.total_buy_orders_label), 
                                  ("Total Sell Orders", self.total_sell_orders_label), 
                                  ("Average Buy Price", self.avg_buy_price_label), 
                                  ("Average Sell Price", self.avg_sell_price_label)]:
            # Create a horizontal layout for each label and its corresponding value
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label_text))  # Add label text
            h_layout.addWidget(label)  # Add label value
            stats_layout.addLayout(h_layout)  # Add horizontal layout to the statistics layout
        
        layout.addLayout(stats_layout)  # Add the statistics layout to the main layout

    def create_chart_layout(self, layout):
        """
        Create a layout for displaying a chart.

        Args:
            layout (QVBoxLayout): The layout to add the chart layout to.
        """
        # Create a figure and axes for the chart
        self.fig, self.ax = plt.subplots()  # Create a figure and axes
        
        # Create a canvas to display the chart
        self.chart_canvas = FigureCanvas(self.fig)  # Create a canvas to display the figure
        
        # Add the canvas to the layout
        layout.addWidget(self.chart_canvas)  # Add the canvas to the layout

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

        Args:
            self (OrderBookGUI): The instance of the class.

        Returns:
            None
        """
        try:
            # Get the order ID from the input field
            order_id = self.order_id_input.text()

            # Call the `cancel_order` method of the `order_book` object with the order ID
            result = self.order_book.cancel_order(order_id)

            # Display a message box with the result
            QMessageBox.information(self, "Cancel Order", result)

            # Log the result
            logging.info(result)

            # Delete the corresponding order entry from the Redis database
            redis_client.delete(f"order:{order_id}")

            # Update the GUI
            self.update_gui()
        except Exception as e:
            # Display an error message box with the error message
            self.show_error("Failed to cancel order", str(e))

            # Log the error
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
        """
        Open the custom order dialog and update the GUI.

        This function creates a new instance of the CustomOrderDialog class
        using the current order book and symbol list. It then displays the
        dialog and updates the GUI after the dialog is closed.

        Raises:
            Exception: If there is an error creating the dialog or updating the GUI.
        """
        # Create a new instance of the CustomOrderDialog class
        dialog = CustomOrderDialog(self.order_book, self.symbols)

        # Display the dialog and wait for it to be closed
        dialog.exec_()

        # Update the GUI after the dialog is closed
        self.update_gui()

    def apply_filter(self):
        """
        Apply the filter to the buy and sell orders in the order book and update the GUI.

        This function retrieves the minimum and maximum price and quantity values from the input fields.
        It then filters the buy and sell orders in the order book based on the price and quantity ranges.
        The filtered orders are stored in separate lists and used to update the buy and sell trees in the GUI.

        Raises:
            Exception: If there is an error retrieving the input values or applying the filter.
        """
        try:
            # Retrieve the minimum and maximum price values from the input fields
            min_price = float(self.min_price_input.text())
            max_price = float(self.max_price_input.text())

            # Retrieve the minimum and maximum quantity values from the input fields
            min_qty = self.min_qty_input.value()
            max_qty = self.max_qty_input.value()

            # Filter the buy orders based on the price and quantity ranges
            filtered_buy_orders = [order for _, _, order in self.order_book.buy_orders
                                   if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]

            # Filter the sell orders based on the price and quantity ranges
            filtered_sell_orders = [order for _, _, order in self.order_book.sell_orders
                                    if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]

            # Update the buy tree with the filtered buy orders
            self.update_tree(self.buy_tree, filtered_buy_orders)

            # Update the sell tree with the filtered sell orders
            self.update_tree(self.sell_tree, filtered_sell_orders)
        except Exception as e:
            # Handle any exceptions that occur during the filter application process
            self.show_error("Failed to apply filter", str(e))
            logging.error(f"Failed to apply filter: {e}")

    def export_to_excel(self):
        """
        Export the matched orders to an Excel file.

        This function retrieves the matched orders from the order book
        and exports them to an Excel file using the excel_exporter module.
        A success message is displayed if the export is successful.

        Raises:
            Exception: If there is an error retrieving the matched orders
                       or exporting them to Excel.
        """
        try:
            # Retrieve the matched orders from the order book
            matched_orders = self.order_book.get_order_history()

            # Export the matched orders to an Excel file
            result = excel_exporter.export_orders_to_excel(matched_orders)

            # Display a success message with the result
            QMessageBox.information(self, "Export to Excel", result)
        except Exception as e:
            # Handle any exceptions that occur during the export process
            self.show_error("Failed to export to Excel", str(e))
            logging.error(f"Failed to export to Excel: {e}")

    def generate_random_order(self):
        """
        Generate a random order with current symbol and price.

        This function retrieves the current symbol and price from the GUI
        and uses them to generate a random order with a new order ID.

        Returns:
            Order: The generated random order.
        """

        # Get the selected symbol
        symbol = self.symbol_input.currentText()

        # Get the current price for the selected symbol
        current_price = self.current_prices[symbol]

        # Generate a random order with a new order ID
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
        """
        Update the stock information on the GUI.

        This function retrieves the last matched price from the order book and calculates the current price,
        price change, and percentage change compared to the current price for the selected symbol. It then
        updates the GUI label with the current price and its change information. The label color is set
        to green if the price change is positive and red if it is negative. Finally, it updates the current
        price for the selected symbol in the `self.current_prices` dictionary.
        """
        # Check if last matched price is available
        if self.order_book.last_matched_price is not None:
            # Retrieve the last matched price
            last_price = self.order_book.last_matched_price
            
            # Calculate the current price as the last matched price
            current_price = last_price
            
            # Calculate the price change and percentage change
            price_change = current_price - self.current_prices[self.symbol_input.currentText()]
            percent_change = (price_change / self.current_prices[self.symbol_input.currentText()]) * 100
            
            # Update the GUI label with the current price and its change information
            self.price_label.setText(f"{current_price:.2f}  {price_change:.2f} ({percent_change:.2f}%)")
            self.price_label.setStyleSheet("color: green;" if price_change >= 0 else "color: red;")
            
            # Update the current price for the selected symbol
            self.current_prices[self.symbol_input.currentText()] = current_price

    def update_statistics(self):
        """
        Update the statistics on the GUI.

        This function calculates the total number of buy and sell orders, the average buy price,
        and the average sell price. It then updates the GUI labels with the corresponding values.
        """
        # Calculate the total number of buy and sell orders
        buy_orders = [order for _, _, order in self.order_book.buy_orders]
        sell_orders = [order for _, _, order in self.order_book.sell_orders]

        total_buy_orders = len(buy_orders)
        total_sell_orders = len(sell_orders)

        # Calculate the average buy price and average sell price
        avg_buy_price = (sum(order.price for order in buy_orders) / total_buy_orders
                         if total_buy_orders else 0)
        avg_sell_price = (sum(order.price for order in sell_orders) / total_sell_orders
                          if total_sell_orders else 0)

        # Update the GUI labels with the corresponding values
        self.total_buy_orders_label.setText(str(total_buy_orders))
        self.total_sell_orders_label.setText(str(total_sell_orders))
        self.avg_buy_price_label.setText(f"{avg_buy_price:.2f}")
        self.avg_sell_price_label.setText(f"{avg_sell_price:.2f}")

    def update_chart(self):
        """
        Update the chart on the GUI with the latest buy and sell orders.

        This function retrieves the latest buy and sell orders from the order book,
        extracts the prices and quantities of each order, and plots them on the chart.
        If any error occurs during the process, an error message is displayed and logged.
        """
        try:
            # Retrieve the latest buy and sell orders from the order book
            buy_orders = [order for _, _, order in self.order_book.buy_orders]
            sell_orders = [order for _, _, order in self.order_book.sell_orders]

            # Extract the prices and quantities of each order
            buy_prices = [order.price for order in buy_orders]
            buy_quantities = [order.quantity for order in buy_orders]
            sell_prices = [order.price for order in sell_orders]
            sell_quantities = [order.quantity for order in sell_orders]

            # Plot the buy and sell orders on the chart
            self.plot_orders(buy_prices, buy_quantities, sell_prices, sell_quantities)
        except Exception as e:
            # Display an error message and log the exception
            self.show_error("Failed to update chart", str(e))
            logging.error(f"Failed to update chart: {e}")

    def plot_orders(self, buy_prices, buy_quantities, sell_prices, sell_quantities):
        """
        Plot the buy and sell orders on the chart.

        Args:
            buy_prices (List[float]): List of buy order prices.
            buy_quantities (List[int]): List of buy order quantities.
            sell_prices (List[float]): List of sell order prices.
            sell_quantities (List[int]): List of sell order quantities.
        """
        # Clear the existing chart
        self.ax.clear()

        # Plot the buy orders
        self.ax.bar(buy_prices, buy_quantities, color='green', label='Buy Orders')

        # Plot the sell orders
        self.ax.bar(sell_prices, sell_quantities, color='red', label='Sell Orders')

        # Set the labels for the x and y axes
        self.ax.set_xlabel('Price')
        self.ax.set_ylabel('Quantity')

        # Set the title for the chart
        self.ax.set_title('Order Distribution')

        # Add a legend to the chart
        self.ax.legend()

        # Update the canvas to display the chart
        self.chart_canvas.draw()

    def start_auto_update(self):
        """
        Start the auto-update timer.

        This function creates a QTimer object and connects its timeout signal to
        the update_gui method. The timer is set to update the GUI every 5
        seconds.
        """
        # Create a QTimer object
        timer = QTimer(self)

        # Connect the timeout signal of the timer to the update_gui method
        timer.timeout.connect(self.update_gui)

        # Start the timer with a timeout interval of 5000 milliseconds (5 seconds)
        timer.start(5000)

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

