import time
import logging
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QMessageBox
from order import Order

class CustomOrderDialog(QDialog):
    def __init__(self, order_book, symbol_list):
        """
        Initializes a new instance of the CustomOrderDialog class.

        Args:
            order_book (OrderBook): The order book object.
            symbol_list (list): The list of symbols.
        """
        # Call the parent constructor
        super().__init__()

        # Initialize instance variables
        self.order_book = order_book
        self.symbol_list = symbol_list

        # Initialize the user interface
        self.init_ui()

        # Configure logging
        logging.basicConfig(
            filename='custom_order_dialog.log',
            level=logging.INFO,
            format='%(asctime)s %(message)s'
        )

    def init_ui(self):
        """
        Initializes the user interface for the custom order dialog.
        """
        # Set the window title
        self.setWindowTitle("Add Custom Order")

        # Create the layout for the dialog
        layout = QVBoxLayout()

        # Create the form layout
        form_layout = QHBoxLayout()

        # Create the input fields for the order
        self.order_id_input = QLineEdit()  # Order ID input field
        self.price_input = QLineEdit()  # Price input field
        self.quantity_input = QSpinBox()  # Quantity input field
        self.quantity_input.setRange(1, 10000)  # Set the range for the quantity input
        self.symbol_input = QComboBox()  # Symbol input field
        self.symbol_input.addItems(self.symbol_list)  # Populate the symbol input field with options
        self.side_input = QComboBox()  # Side input field
        self.side_input.addItems(["buy", "sell"])  # Populate the side input field with options
        self.type_input = QComboBox()  # Type input field
        self.type_input.addItems(["limit", "market"])  # Populate the type input field with options

        # Add the input fields to the form layout
        form_layout.addWidget(QLabel("Order ID"))  # Label for the order ID input field
        form_layout.addWidget(self.order_id_input)  # Order ID input field
        form_layout.addWidget(QLabel("Price"))  # Label for the price input field
        form_layout.addWidget(self.price_input)  # Price input field
        form_layout.addWidget(QLabel("Quantity"))  # Label for the quantity input field
        form_layout.addWidget(self.quantity_input)  # Quantity input field
        form_layout.addWidget(QLabel("Symbol"))  # Label for the symbol input field
        form_layout.addWidget(self.symbol_input)  # Symbol input field
        form_layout.addWidget(QLabel("Side"))  # Label for the side input field
        form_layout.addWidget(self.side_input)  # Side input field
        form_layout.addWidget(QLabel("Type"))  # Label for the type input field
        form_layout.addWidget(self.type_input)  # Type input field

        # Create the add order button and connect it to the add_order method
        add_order_button = QPushButton("Add Order")
        add_order_button.clicked.connect(self.add_order)
        form_layout.addWidget(add_order_button)  # Add the add order button to the form layout

        # Add the form layout to the dialog layout
        layout.addLayout(form_layout)

        # Set the layout for the dialog
        self.setLayout(layout)

    def add_order(self):
        """
        Adds the custom order to the order book and logs the success or failure.
        """
        try:
            # Generate timestamp in milliseconds
            timestamp = int(time.time() * 1000)

            # Create Order object with user input
            order = Order(
                timestamp=timestamp,
                order_id=self.order_id_input.text(),
                symbol=self.symbol_input.currentText(),
                price=float(self.price_input.text()),
                quantity=self.quantity_input.value(),
                side=self.side_input.currentText(),
                order_type=self.type_input.currentText()
            )

            # Print the order details for debugging
            print("Adding order:", order.__dict__)

            # Add the order to the order book
            self.order_book.add_order(order)

            # Print the successful addition of the order
            print("Order added:", order.__dict__)

            # Close the dialog
            self.accept()

        except ValueError as e:
            # Log the error caused by invalid input
            logging.error(f"Invalid input for order: {e}")

            # Print the error message for debugging
            print("Error:", e)

            # Show an error message to the user
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")

        except Exception as e:
            # Log the error caused by failure to add the order
            logging.error(f"Failed to add custom order: {e}")

            # Print the error message for debugging
            print("Error:", e)

            # Show an error message to the user
            QMessageBox.critical(self, "Error", f"Failed to add custom order: {e}")
