import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from order import Order
from order_book import OrderBook, fetch_current_prices, generate_realistic_order

class OrderBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Order Book Ladder")
        self.order_book = OrderBook()
        self.order_id_counter = 1
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        self.selected_symbol = tk.StringVar(value=self.symbols[0])
        self.current_prices = fetch_current_prices(self.symbols)
        self.setup_ui()
        self.start_auto_update()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(main_frame, bg="black")
        header_frame.pack(fill=tk.X)

        self.price_label = tk.Label(header_frame, text="", font=("Arial", 16), fg="red", bg="black")
        self.price_label.pack(pady=5)

        order_panedwindow = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg="black")
        order_panedwindow.pack(fill=tk.BOTH, expand=True)

        self.buy_frame, self.buy_tree = self.create_treeview(order_panedwindow, "Buy Orders", 'lightblue')
        self.sell_frame, self.sell_tree = self.create_treeview(order_panedwindow, "Sell Orders", 'lightcoral')
        
        order_panedwindow.add(self.buy_frame)
        order_panedwindow.add(self.sell_frame)

        bottom_frame = tk.Frame(main_frame, bg="black")
        bottom_frame.pack(fill=tk.X, pady=10)

        day_range_label = tk.Label(bottom_frame, text="Day's range", font=("Arial", 12), fg="white", bg="black")
        day_range_label.grid(row=0, column=0, padx=10)

        self.low_label = tk.Label(bottom_frame, text="", font=("Arial", 12), fg="white", bg="black")
        self.low_label.grid(row=0, column=1, padx=10)

        self.high_label = tk.Label(bottom_frame, text="", font=("Arial", 12), fg="white", bg="black")
        self.high_label.grid(row=0, column=2, padx=10)

        self.open_label = tk.Label(bottom_frame, text="", font=("Arial", 12), fg="white", bg="black")
        self.open_label.grid(row=0, column=3, padx=10)

        self.prev_close_label = tk.Label(bottom_frame, text="", font=("Arial", 12), fg="white", bg="black")
        self.prev_close_label.grid(row=0, column=4, padx=10)

        self.create_button_frame(main_frame)
        self.create_order_form(main_frame)

        self.status_var = tk.StringVar()
        status_label = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="black", fg="white")
        status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

        self.create_filter_frame(main_frame)
        self.create_statistics_frame(main_frame)
        self.create_chart_frame(main_frame)

    def create_treeview(self, parent, label, color=None):
        frame = tk.Frame(parent, bg="black")
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree = ttk.Treeview(frame, columns=("Price", "Orders", "Qty"), show='headings', yscrollcommand=scroll.set)
        for col in tree["columns"]:
            tree.heading(col, text=col, command=lambda _col=col: self.sort_column(tree, _col, False))
        if color:
            tree.tag_configure('highlight', background='yellow')
            tree.tag_configure('highlight_alt', background='orange')
            tree.tag_configure('color', background=color)
        tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=tree.yview)
        frame.pack(fill=tk.BOTH, expand=True)
        return frame, tree

    def create_button_frame(self, parent):
        frame = tk.Frame(parent, bg="black")
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        buttons = [
            ("Add Random Order", self.add_random_order),
            ("Match Orders", self.match_orders),
            ("Cancel Order", self.cancel_order),
            ("Export to Excel", self.export_to_excel)
        ]
        
        for text, command in buttons:
            button = tk.Button(frame, text=text, command=command, font=("Arial", 12), bg="grey", fg="white")
            button.pack(side=tk.LEFT, padx=5)
        
        return frame

    def create_order_form(self, parent):
        frame = tk.Frame(parent, bg="black")
        frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame, text="Order ID", fg="white", bg="black").grid(row=0, column=0)
        self.order_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.order_id_var).grid(row=0, column=1)

        tk.Label(frame, text="Price", fg="white", bg="black").grid(row=0, column=2)
        self.price_var = tk.DoubleVar()
        tk.Entry(frame, textvariable=self.price_var).grid(row=0, column=3)

        tk.Label(frame, text="Quantity", fg="white", bg="black").grid(row=0, column=4)
        self.quantity_var = tk.IntVar()
        tk.Entry(frame, textvariable=self.quantity_var).grid(row=0, column=5)

        tk.Label(frame, text="Side", fg="white", bg="black").grid(row=1, column=0)
        self.side_var = tk.StringVar(value="buy")
        tk.OptionMenu(frame, self.side_var, "buy", "sell").grid(row=1, column=1)

        tk.Label(frame, text="Type", fg="white", bg="black").grid(row=1, column=2)
        self.type_var = tk.StringVar(value="limit")
        tk.OptionMenu(frame, self.type_var, "limit", "market").grid(row=1, column=3)

        tk.Button(frame, text="Add Order", command=self.add_manual_order, bg="grey", fg="white").grid(row=1, column=4, padx=5)
        tk.Button(frame, text="Cancel Order", command=self.cancel_order, bg="grey", fg="white").grid(row=1, column=5, padx=5)

    def create_filter_frame(self, parent):
        frame = tk.Frame(parent, bg="black")
        frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame, text="Filter Orders", font=("Arial", 12), fg="white", bg="black").grid(row=0, column=0, columnspan=4)

        tk.Label(frame, text="Min Price", fg="white", bg="black").grid(row=1, column=0)
        self.min_price_var = tk.DoubleVar()
        tk.Entry(frame, textvariable=self.min_price_var).grid(row=1, column=1)

        tk.Label(frame, text="Max Price", fg="white", bg="black").grid(row=1, column=2)
        self.max_price_var = tk.DoubleVar()
        tk.Entry(frame, textvariable=self.max_price_var).grid(row=1, column=3)

        tk.Label(frame, text="Min Quantity", fg="white", bg="black").grid(row=2, column=0)
        self.min_qty_var = tk.IntVar()
        tk.Entry(frame, textvariable=self.min_qty_var).grid(row=2, column=1)

        tk.Label(frame, text="Max Quantity", fg="white", bg="black").grid(row=2, column=2)
        self.max_qty_var = tk.IntVar()
        tk.Entry(frame, textvariable=self.max_qty_var).grid(row=2, column=3)

        tk.Button(frame, text="Apply Filter", command=self.apply_filter, bg="grey", fg="white").grid(row=3, column=0, columnspan=4, pady=5)

    def create_statistics_frame(self, parent):
        frame = tk.Frame(parent, bg="black")
        frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame, text="Order Statistics", font=("Arial", 12), fg="white", bg="black").grid(row=0, column=0, columnspan=2)

        tk.Label(frame, text="Total Buy Orders", fg="white", bg="black").grid(row=1, column=0, sticky="w")
        self.total_buy_orders_label = tk.Label(frame, text="0", fg="white", bg="black")
        self.total_buy_orders_label.grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Total Sell Orders", fg="white", bg="black").grid(row=2, column=0, sticky="w")
        self.total_sell_orders_label = tk.Label(frame, text="0", fg="white", bg="black")
        self.total_sell_orders_label.grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Average Buy Price", fg="white", bg="black").grid(row=3, column=0, sticky="w")
        self.avg_buy_price_label = tk.Label(frame, text="0.00", fg="white", bg="black")
        self.avg_buy_price_label.grid(row=3, column=1, sticky="w")

        tk.Label(frame, text="Average Sell Price", fg="white", bg="black").grid(row=4, column=0, sticky="w")
        self.avg_sell_price_label = tk.Label(frame, text="0.00", fg="white", bg="black")
        self.avg_sell_price_label.grid(row=4, column=1, sticky="w")

    def create_chart_frame(self, parent):
        frame = tk.Frame(parent, bg="black")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Order Distribution", font=("Arial", 12), fg="white", bg="black").pack()

        self.fig, self.ax = plt.subplots()
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def generate_random_order(self):
        symbol = self.selected_symbol.get()
        current_price = self.current_prices[symbol]
        return generate_realistic_order(f'{self.order_id_counter}', symbol, current_price)

    def add_manual_order(self):
        try:
            timestamp = int(time.time() * 1000)
            order = Order(
                timestamp=timestamp,
                order_id=self.order_id_var.get(),
                symbol=self.selected_symbol.get(),
                price=self.price_var.get(),
                quantity=self.quantity_var.get(),
                side=self.side_var.get(),
                order_type=self.type_var.get()
            )
            self.order_book.add_order(order)
            self.order_id_counter += 1
            self.update_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add manual order: {e}")

    def cancel_order(self):
        try:
            order_id = self.order_id_var.get()
            result = self.order_book.cancel_order(order_id)
            messagebox.showinfo("Cancel Order", result)
            self.update_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {e}")

    def update_gui(self):
        try:
            order_book_state = self.order_book.get_order_book()
            
            self.update_tree(self.buy_tree, order_book_state['buy_orders'])
            self.update_tree(self.sell_tree, order_book_state['sell_orders'])
            
            self.update_stock_info()
            self.update_statistics()
            self.update_chart()

            self.status_var.set("Order Book Updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update GUI: {e}")

    def update_tree(self, tree, orders):
        tree.delete(*tree.get_children())
        for order in orders:
            tags = ('color',)
            if order.quantity > 10:
                tags = ('highlight', 'color')
            tree.insert('', 'end', values=(order.price, len(orders), order.quantity), tags=tags)

    def update_stock_info(self):
        if self.order_book.last_matched_price is not None:
            last_price = self.order_book.last_matched_price
            current_price = last_price
            price_change = current_price - self.current_prices[self.selected_symbol.get()]
            percent_change = (price_change / self.current_prices[self.selected_symbol.get()]) * 100
            self.price_label.config(text=f"{current_price:.2f}  {price_change:.2f} ({percent_change:.2f}%)", fg="green" if price_change >= 0 else "red")
            self.current_prices[self.selected_symbol.get()] = current_price

    def apply_filter(self):
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        min_qty = self.min_qty_var.get()
        max_qty = self.max_qty_var.get()

        filtered_buy_orders = [order for order in self.order_book.buy_orders if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]
        filtered_sell_orders = [order for order in self.order_book.sell_orders if min_price <= order.price <= max_price and min_qty <= order.quantity <= max_qty]

        self.update_tree(self.buy_tree, filtered_buy_orders)
        self.update_tree(self.sell_tree, filtered_sell_orders)

    def update_statistics(self):
        buy_orders = self.order_book.buy_orders
        sell_orders = self.order_book.sell_orders

        total_buy_orders = len(buy_orders)
        total_sell_orders = len(sell_orders)
        avg_buy_price = sum(order.price for order in buy_orders) / total_buy_orders if total_buy_orders else 0
        avg_sell_price = sum(order.price for order in sell_orders) / total_sell_orders if total_sell_orders else 0

        self.total_buy_orders_label.config(text=str(total_buy_orders))
        self.total_sell_orders_label.config(text=str(total_sell_orders))
        self.avg_buy_price_label.config(text=f"{avg_buy_price:.2f}")
        self.avg_sell_price_label.config(text=f"{avg_sell_price:.2f}")

    def update_chart(self):
        buy_orders = self.order_book.buy_orders
        sell_orders = self.order_book.sell_orders

        buy_prices = [order.price for order in buy_orders]
        buy_quantities = [order.quantity for order in buy_orders]
        sell_prices = [order.price for order in sell_orders]
        sell_quantities = [order.quantity for order in sell_orders]

        self.ax.clear()
        self.ax.bar(buy_prices, buy_quantities, color='green', label='Buy Orders')
        self.ax.bar(sell_prices, sell_quantities, color='red', label='Sell Orders')
        self.ax.set_xlabel('Price')
        self.ax.set_ylabel('Quantity')
        self.ax.set_title('Order Distribution')
        self.ax.legend()
        self.chart_canvas.draw()

    def add_random_order(self):
        try:
            order = self.generate_random_order()
            self.order_book.add_order(order)
            self.order_id_counter += 1
            self.update_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add random order: {e}")

    def match_orders(self):
        try:
            matched = self.order_book.match_orders()
            if not matched:
                print("No orders matched.")
            else:
                for buy, sell, qty in matched:
                    print(f"Matched {qty} units between buy order {buy.order_id} and sell order {sell.order_id}")
            self.update_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to match orders: {e}")

    def search_orders(self, *args):
        try:
            query = self.search_var.get().lower()
            self.filter_tree(self.buy_tree, self.order_book.get_order_book()['buy_orders'], query)
            self.filter_tree(self.sell_tree, self.order_book.get_order_book()['sell_orders'], query)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search orders: {e}")

    def filter_tree(self, tree, orders, query):
        tree.delete(*tree.get_children())
        for order in orders:
            if query in order.order_id.lower() or query in str(order.price).lower():
                tags = ('color',)
                if order.quantity > 10:
                    tags = ('highlight', 'color')
                tree.insert('', 'end', values=(order.price, len(orders), order.quantity), tags=tags)

    def sort_column(self, tree, col, reverse):
        try:
            l = [(tree.set(k, col), k) for k in tree.get_children('')]
            l.sort(reverse=reverse)
            
            for index, (val, k) in enumerate(l):
                tree.move(k, '', index)
            
            tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sort column: {e}")

    def export_to_excel(self):
        try:
            matched_orders = self.order_book.get_order_history()
            if not matched_orders:
                messagebox.showinfo("No Data", "No matched orders to export.")
                return
            
            df = pd.DataFrame(matched_orders)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.columns = ["Buy Order ID", "Sell Order ID", "Symbol", "Quantity", "Price", "Timestamp"]
            
            writer = pd.ExcelWriter('matched_orders.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Matched Orders', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Matched Orders']
            
            # Add some cell formats.
            format1 = workbook.add_format({'num_format': '0.00'}) 
            format2 = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
            worksheet.set_column('A:F', 20)
            worksheet.set_column('E:E', 12, format1)
            worksheet.set_column('F:F', 20, format2)
            
            writer.close()
            messagebox.showinfo("Export Successful", "Matched orders exported to matched_orders.xlsx.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to Excel: {e}")

    def start_auto_update(self):
        def auto_update():
            while True:
                time.sleep(5)  # Update every 5 seconds
                self.update_gui()
        
        threading.Thread(target=auto_update, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderBookGUI(root)
    root.mainloop()
