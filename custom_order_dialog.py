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
        print("Initializing UI")
        # Set the window title
        self.setWindowTitle("Add Custom Order")

        # Create the layout for the dialog
        layout = QVBoxLayout()
        print("Layout created")

        # Create the form layout
        form_layout = QHBoxLayout()
        print("Form layout created")

        # Create the input fields for the order
        self.order_id_input = QLineEdit()  # Order ID input field
        print("Order ID input field created")
        self.price_input = QLineEdit()  # Price input field
        print("Price input field created")
        self.quantity_input = QSpinBox()  # Quantity input field
        print("Quantity input field created")
        self.quantity_input.setRange(1, 10000)  # Set the range for the quantity input
        print("Quantity range set")
        self.symbol_input = QComboBox()  # Symbol input field
        print("Symbol input field created")
        self.symbol_input.addItems(self.symbol_list)  # Populate the symbol input field with options
        print("Symbol input field populated")
        self.side_input = QComboBox()  # Side input field
        print("Side input field created")
        self.side_input.addItems(["buy", "sell"])  # Populate the side input field with options
        print("Side input field populated")
        self.type_input = QComboBox()  # Type input field
        print("Type input field created")
        self.type_input.addItems(["limit", "market"])  # Populate the type input field with options
        print("Type input field populated")

        # Add the input fields to the form layout
        form_layout.addWidget(QLabel("Order ID"))  # Label for the order ID input field
        print("Order ID label added")
        form_layout.addWidget(self.order_id_input)  # Order ID input field
        print("Order ID input field added")
        form_layout.addWidget(QLabel("Price"))  # Label for the price input field
        print("Price label added")
        form_layout.addWidget(self.price_input)  # Price input field
        print("Price input field added")
        form_layout.addWidget(QLabel("Quantity"))  # Label for the quantity input field
        print("Quantity label added")
        form_layout.addWidget(self.quantity_input)  # Quantity input field
        print("Quantity input field added")
        form_layout.addWidget(QLabel("Symbol"))  # Label for the symbol input field
        print("Symbol label added")
        form_layout.addWidget(self.symbol_input)  # Symbol input field
        print("Symbol input field added")
        form_layout.addWidget(QLabel("Side"))  # Label for the side input field
        print("Side label added")
        form_layout.addWidget(self.side_input)  # Side input field
        print("Side input field added")
        form_layout.addWidget(QLabel("Type"))  # Label for the type input field
        print("Type label added")
        form_layout.addWidget(self.type_input)  # Type input field
        print("Type input field added")

        # Create the add order button and connect it to the add_order method
        add_order_button = QPushButton("Add Order")
        print("Add order button created")
        add_order_button.clicked.connect(self.add_order)
        print("Add order button connected to add_order method")
        form_layout.addWidget(add_order_button)  # Add the add order button to the form layout
        print("Add order button added to form layout")

        # Add the form layout to the dialog layout
        layout.addLayout(form_layout)
        print("Form layout added to dialog layout")

        # Set the layout for the dialog
        self.setLayout(layout)
        print("Layout set for dialog")

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
