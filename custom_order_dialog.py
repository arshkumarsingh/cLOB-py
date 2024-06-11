import time
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QMessageBox
from order import Order

class CustomOrderDialog(QDialog):
    def __init__(self, order_book, symbol_list):
        super().__init__()
        self.order_book = order_book
        self.symbol_list = symbol_list
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Custom Order")
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        
        self.order_id_input = QLineEdit()
        self.price_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.symbol_input = QComboBox()
        self.symbol_input.addItems(self.symbol_list)
        self.side_input = QComboBox()
        self.side_input.addItems(["buy", "sell"])
        self.type_input = QComboBox()
        self.type_input.addItems(["limit", "market"])

        form_layout.addWidget(QLabel("Order ID"))
        form_layout.addWidget(self.order_id_input)
        form_layout.addWidget(QLabel("Price"))
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(QLabel("Quantity"))
        form_layout.addWidget(self.quantity_input)
        form_layout.addWidget(QLabel("Symbol"))
        form_layout.addWidget(self.symbol_input)
        form_layout.addWidget(QLabel("Side"))
        form_layout.addWidget(self.side_input)
        form_layout.addWidget(QLabel("Type"))
        form_layout.addWidget(self.type_input)

        add_order_button = QPushButton("Add Order")
        add_order_button.clicked.connect(self.add_order)
        form_layout.addWidget(add_order_button)

        layout.addLayout(form_layout)
        self.setLayout(layout)

    def add_order(self):
        try:
            timestamp = int(time.time() * 1000)
            order = Order(
                timestamp=timestamp,
                order_id=self.order_id_input.text(),
                symbol=self.symbol_input.currentText(),
                price=float(self.price_input.text()),
                quantity=self.quantity_input.value(),
                side=self.side_input.currentText(),
                order_type=self.type_input.currentText()
            )
            self.order_book.add_order(order)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add custom order: {e}")
