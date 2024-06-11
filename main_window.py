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

class OrderBookGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Book Ladder")
        self.order_book = OrderBook()
        self.order_id_counter = 1
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        self.current_prices = fetch_current_prices(self.symbols)
        self.mutex = QMutex()
        self.init_ui()
        self.start_auto_update()
        logging.basicConfig(filename='order_book_gui.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.create_toolbar()

        header_layout = QHBoxLayout()
        self.symbol_input = QComboBox()
        self.symbol_input.addItems(self.symbols)
        header_layout.addWidget(QLabel("Symbol"))
        header_layout.addWidget(self.symbol_input)
        self.price_label = QLabel("")
        self.price_label.setStyleSheet("font-size: 16px; color: red;")
        header_layout.addWidget(self.price_label)
        main_layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Horizontal)
        self.buy_tree = self.create_treeview("Buy Orders")
        self.sell_tree = self.create_treeview("Sell Orders")
        splitter.addWidget(self.buy_tree)
        splitter.addWidget(self.sell_tree)
        main_layout.addWidget(splitter)

        bottom_layout = QHBoxLayout()
        self.low_label = QLabel("")
        self.high_label = QLabel("")
        self.open_label = QLabel("")
        self.prev_close_label = QLabel("")
        for label in [self.low_label, self.high_label, self.open_label, self.prev_close_label]:
            label.setStyleSheet("font-size: 12px; color: white;")
            bottom_layout.addWidget(label)
        main_layout.addLayout(bottom_layout)

        self.create_filter_layout(main_layout)
        self.create_statistics_layout(main_layout)
        self.create_chart_layout(main_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.status_label)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        add_random_order_action = QAction("Add Random Order", self)
        add_random_order_action.triggered.connect(self.add_random_order)
        toolbar.addAction(add_random_order_action)

        match_orders_action = QAction("Match Orders", self)
        match_orders_action.triggered.connect(self.match_orders)
        toolbar.addAction(match_orders_action)

        cancel_order_action = QAction("Cancel Order", self)
        cancel_order_action.triggered.connect(self.cancel_order)
        toolbar.addAction(cancel_order_action)

        export_to_excel_action = QAction("Export to Excel", self)
        export_to_excel_action.triggered.connect(self.export_to_excel)
        toolbar.addAction(export_to_excel_action)

        add_custom_order_action = QAction("Add Custom Order", self)
        add_custom_order_action.triggered.connect(self.open_custom_order_dialog)
        toolbar.addAction(add_custom_order_action)

    def create_treeview(self, label):
        tree = QTreeWidget()
        tree.setColumnCount(4)  # Add an extra column for execution time
        tree.setHeaderLabels([label, "Orders", "Qty", "Exec Time"])
        return tree

    def create_filter_layout(self, layout):
        filter_layout = QHBoxLayout()
        self.min_price_input = QLineEdit()
        self.max_price_input = QLineEdit()
        self.min_qty_input = QSpinBox()
        self.max_qty_input = QSpinBox()
        
        filter_layout.addWidget(QLabel("Min Price"))
        filter_layout.addWidget(self.min_price_input)
        filter_layout.addWidget(QLabel("Max Price"))
        filter_layout.addWidget(self.max_price_input)
        filter_layout.addWidget(QLabel("Min Quantity"))
        filter_layout.addWidget(self.min_qty_input)
        filter_layout.addWidget(QLabel("Max Quantity"))
        filter_layout.addWidget(self.max_qty_input)
        
        apply_filter_button = QPushButton("Apply Filter")
        apply_filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_filter_button)
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
        try:
            if random.random() <= 0.9:
                # Generate one buy and one sell order
                symbol = self.symbol_input.currentText()  # Get the selected symbol
                current_price = self.current_prices[symbol]

                buy_order = generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)
                buy_order.side = "buy"
                self.order_book.add_order(buy_order)
                self.order_id_counter += 1

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
            self.show_error("Failed to add random order", str(e))
            logging.error(f"Failed to add random order: {e}")

    def cancel_order(self):
        try:
            order_id = self.order_id_input.text()
            result = self.order_book.cancel_order(order_id)
            QMessageBox.information(self, "Cancel Order", result)
            logging.info(result)
            self.update_gui()
        except Exception as e:
            self.show_error("Failed to cancel order", str(e))
            logging.error(f"Failed to cancel order: {e}")

    def match_orders(self):
        try:
            matched = self.order_book.match_orders()
            if not matched:
                logging.info("No orders matched.")
            else:
                for buy, sell, qty in matched:
                    logging.info(f"Matched {qty} units between buy order {buy.order_id} and sell order {sell.order_id}")
            self.update_gui()
        except Exception as e:
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
            if not matched_orders:
                QMessageBox.information(self, "No Data", "No matched orders to export.")
                logging.info("No matched orders to export.")
                return
            
            df = pd.DataFrame(matched_orders)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.columns = ["Buy Order ID", "Sell Order ID", "Symbol", "Quantity", "Price", "Timestamp"]
            
            writer = pd.ExcelWriter('matched_orders.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Matched Orders', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Matched Orders']
            
            format1 = workbook.add_format({'num_format': '0.00'}) 
            format2 = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
            worksheet.set_column('A:F', 20)
            worksheet.set_column('E:E', 12, format1)
            worksheet.set_column('F:F', 20, format2)
            
            writer.close()
            QMessageBox.information(self, "Export Successful", "Matched orders exported to matched_orders.xlsx.")
            logging.info("Matched orders exported to matched_orders.xlsx.")
        except Exception as e:
            self.show_error("Failed to export to Excel", str(e))
            logging.error(f"Failed to export to Excel: {e}")

    def generate_random_order(self):
        symbol = self.symbol_input.currentText()  # Get the selected symbol
        current_price = self.current_prices[symbol]
        return generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)

    def update_gui(self):
        try:
            with QMutexLocker(self.mutex):
                order_book_state = self.order_book.get_order_book()

                self.update_tree(self.buy_tree, order_book_state['buy_orders'])
                self.update_tree(self.sell_tree, order_book_state['sell_orders'])

                self.update_stock_info()
                self.update_statistics()
                self.update_chart()

                self.status_label.setText("Order Book Updated")
                logging.info("GUI updated successfully")
        except Exception as e:
            self.show_error("Failed to update GUI", str(e))
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderBookGUI()
    window.show()
    sys.exit(app.exec_())
