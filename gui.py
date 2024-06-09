import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from order import Order
from order_book import OrderBook
import threading

def generate_random_order(order_id):
    timestamp = int(time.time() * 1000)  # current time in milliseconds
    symbol = random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'])
    price = random.uniform(100, 1500) if symbol == 'TSLA' else random.uniform(50, 500)
    quantity = random.randint(1, 100)
    side = random.choice(['buy', 'sell'])
    order_type = random.choice(['limit', 'market', 'iceberg', 'stop_loss', 'stop_limit'])
    stop_price = None
    displayed_quantity = None
    if order_type in ['stop_loss', 'stop_limit']:
        stop_price = random.uniform(45, 1550)
    if order_type == 'iceberg':
        displayed_quantity = random.randint(1, quantity)
    return Order(timestamp=timestamp, order_id=order_id, symbol=symbol, price=price, quantity=quantity, side=side, order_type=order_type, stop_price=stop_price, displayed_quantity=displayed_quantity)

def update_gui():
    order_book.trigger_stop_orders()
    order_book_state = order_book.get_order_book()
    
    # Clear existing entries
    buy_tree.delete(*buy_tree.get_children())
    sell_tree.delete(*sell_tree.get_children())
    history_tree.delete(*history_tree.get_children())

    # Insert buy orders
    for order in order_book_state['buy_orders']:
        tags = ('buy',)
        if order.quantity > 10:
            tags = ('highlight', 'buy')
        buy_tree.insert('', 'end', values=(order.order_id, order.symbol, order.price, order.quantity, order.order_type, order.displayed_quantity), tags=tags)

    # Insert sell orders
    for order in order_book_state['sell_orders']:
        tags = ('sell',)
        if order.quantity > 10:
            tags = ('highlight', 'sell')
        sell_tree.insert('', 'end', values=(order.order_id, order.symbol, order.price, order.quantity, order.order_type, order.displayed_quantity), tags=tags)

    # Update order history
    order_history = order_book.get_order_history()
    for hist in order_history:
        history_tree.insert('', 'end', values=(hist['buy_order_id'], hist['sell_order_id'], hist['symbol'], hist['quantity'], hist['price']))

    status_var.set("Order Book Updated")
    update_chart()

def update_chart():
    buy_orders = order_book.get_order_book()['buy_orders']
    sell_orders = order_book.get_order_book()['sell_orders']

    buy_prices = [order.price for order in buy_orders]
    buy_quantities = [order.quantity for order in buy_orders]
    sell_prices = [order.price for order in sell_orders]
    sell_quantities = [order.quantity for order in sell_orders]

    ax.clear()

    # Plot buy orders
    for i in range(len(buy_prices)):
        if i == 0:
            ax.plot([buy_prices[i], buy_prices[i]], [0, buy_quantities[i]], color='green')
        else:
            ax.plot([buy_prices[i-1], buy_prices[i]], [buy_quantities[i-1], buy_quantities[i]], color='green')
            ax.plot([buy_prices[i], buy_prices[i]], [buy_quantities[i-1], buy_quantities[i]], color='green')

    # Plot sell orders
    for i in range(len(sell_prices)):
        if i == 0:
            ax.plot([sell_prices[i], sell_prices[i]], [0, sell_quantities[i]], color='red')
        else:
            ax.plot([sell_prices[i-1], sell_prices[i]], [sell_quantities[i-1], sell_quantities[i]], color='red')
            ax.plot([sell_prices[i], sell_prices[i]], [sell_quantities[i-1], sell_quantities[i]], color='red')

    ax.set_xlabel('Price')
    ax.set_ylabel('Quantity')
    ax.set_title('Order Book Depth Chart')
    chart_canvas.draw()

def add_random_order():
    global order_id_counter
    order = generate_random_order(f'{order_id_counter}')
    order_book.add_order(order)
    order_id_counter += 1
    update_gui()

def match_orders():
    order_book.match_orders()
    update_gui()

def start_updates():
    global running
    running = True
    update_orders()
    status_var.set("Auto Update Started")

def stop_updates():
    global running
    running = False
    status_var.set("Auto Update Stopped")

def update_orders():
    if running:
        add_random_order()
        root.after(1000, update_orders)

def search_orders(*args):
    query = search_var.get().lower()
    for item in buy_tree.get_children():
        buy_tree.delete(item)
    for item in sell_tree.get_children():
        sell_tree.delete(item)
    
    for order in order_book.get_order_book()['buy_orders']:
        if query in order.order_id.lower() or query in str(order.price).lower():
            tags = ('buy',)
            if order.quantity > 10:
                tags = ('highlight', 'buy')
            buy_tree.insert('', 'end', values=(order.order_id, order.symbol, order.price, order.quantity, order.order_type, order.displayed_quantity), tags=tags)
    
    for order in order_book.get_order_book()['sell_orders']:
        if query in order.order_id.lower() or query in str(order.price).lower():
            tags = ('sell',)
            if order.quantity > 10:
                tags = ('highlight', 'sell')
            sell_tree.insert('', 'end', values=(order.order_id, order.symbol, order.price, order.quantity, order.order_type, order.displayed_quantity), tags=tags)

def sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)
    
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
    
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def open_chart_window():
    chart_window = tk.Toplevel(root)
    chart_window.title("Order Book Depth Chart")
    chart_window.geometry("800x600")

    global fig, ax, chart_canvas
    fig, ax = plt.subplots()
    chart_canvas = FigureCanvasTkAgg(fig, master=chart_window)
    chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    update_chart()

def start_market_simulation():
    def simulate_market():
        for _ in range(1000):  # Adjust this number as needed for stress testing
            add_random_order()
            if not running:
                break
            time.sleep(0.01)  # Adjust the speed of order generation

    global running
    running = True
    threading.Thread(target=simulate_market).start()

order_book = OrderBook()
order_id_counter = 1
running = False

root = tk.Tk()
root.title("Order Book Ladder")

# Create a vertical PanedWindow for the main content
main_panedwindow = tk.PanedWindow(root, orient=tk.VERTICAL)
main_panedwindow.pack(fill=tk.BOTH, expand=True)

# Create horizontal PanedWindow for the order books
order_panedwindow = tk.PanedWindow(main_panedwindow, orient=tk.HORIZONTAL)
main_panedwindow.add(order_panedwindow)

# Buy orders tree with scrollbar
buy_tree_frame = tk.Frame(order_panedwindow)
buy_tree_scroll = ttk.Scrollbar(buy_tree_frame, orient=tk.VERTICAL)
buy_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
buy_tree = ttk.Treeview(buy_tree_frame, columns=("ID", "Symbol", "Price", "Quantity", "Type", "Displayed Quantity"), show='headings', yscrollcommand=buy_tree_scroll.set)
for col in buy_tree["columns"]:
    buy_tree.heading(col, text=col, command=lambda _col=col: sort_column(buy_tree, _col, False))
buy_tree.tag_configure('buy', background='lightblue')
buy_tree.tag_configure('highlight', background='yellow')
buy_tree.tag_configure('highlight_alt', background='orange')
buy_tree.pack(fill=tk.BOTH, expand=True)
buy_tree_scroll.config(command=buy_tree.yview)
order_panedwindow.add(buy_tree_frame)

# Sell orders tree with scrollbar
sell_tree_frame = tk.Frame(order_panedwindow)
sell_tree_scroll = ttk.Scrollbar(sell_tree_frame, orient=tk.VERTICAL)
sell_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
sell_tree = ttk.Treeview(sell_tree_frame, columns=("ID", "Symbol", "Price", "Quantity", "Type", "Displayed Quantity"), show='headings', yscrollcommand=sell_tree_scroll.set)
for col in sell_tree["columns"]:
    sell_tree.heading(col, text=col, command=lambda _col=col: sort_column(sell_tree, _col, False))
sell_tree.tag_configure('sell', background='lightcoral')
sell_tree.tag_configure('highlight', background='yellow')
sell_tree.tag_configure('highlight_alt', background='orange')
sell_tree.pack(fill=tk.BOTH, expand=True)
sell_tree_scroll.config(command=sell_tree.yview)
order_panedwindow.add(sell_tree_frame)

# Order history tree with scrollbar
history_tree_frame = tk.Frame(main_panedwindow)
history_tree_scroll = ttk.Scrollbar(history_tree_frame, orient=tk.VERTICAL)
history_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
history_tree = ttk.Treeview(history_tree_frame, columns=("Buy Order ID", "Sell Order ID", "Symbol", "Quantity", "Price"), show='headings', yscrollcommand=history_tree_scroll.set)
for col in history_tree["columns"]:
    history_tree.heading(col, text=col, command=lambda _col=col: sort_column(history_tree, _col, False))
history_tree.pack(fill=tk.BOTH, expand=True)
history_tree_scroll.config(command=history_tree.yview)
main_panedwindow.add(history_tree_frame)

# Search bar
search_var = tk.StringVar()
search_var.trace("w", search_orders)
search_entry = tk.Entry(root, textvariable=search_var, width=50)
search_entry.pack(padx=10, pady=10)

# Create button frame at the bottom
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=10)

# Add buttons
add_order_button = tk.Button(button_frame, text="Add Random Order", command=add_random_order)
add_order_button.pack(side=tk.LEFT, padx=5)

match_orders_button = tk.Button(button_frame, text="Match Orders", command=match_orders)
match_orders_button.pack(side=tk.LEFT, padx=5)

start_button = tk.Button(button_frame, text="Start Auto Update", command=start_updates)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop Auto Update", command=stop_updates)
stop_button.pack(side=tk.LEFT, padx=5)

simulate_button = tk.Button(button_frame, text="Start Market Simulation", command=start_market_simulation)
simulate_button.pack(side=tk.LEFT, padx=5)

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

# Open chart window
open_chart_window()

root.mainloop()
