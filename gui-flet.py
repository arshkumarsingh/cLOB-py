import flet as ft
import random
import time
from order import Order
from order_book import OrderBook

def generate_random_order(order_id):
    timestamp = int(time.time() * 1000)  # current time in milliseconds
    price = random.randint(90, 110)
    quantity = random.randint(1, 20)
    side = random.choice(['buy', 'sell'])
    order_type = random.choice(['limit', 'market', 'iceberg', 'stop_loss', 'stop_limit'])
    stop_price = None
    displayed_quantity = None
    if order_type in ['stop_loss', 'stop_limit']:
        stop_price = random.randint(85, 115)
    if order_type == 'iceberg':
        displayed_quantity = random.randint(1, quantity)
    return Order(timestamp=timestamp, order_id=order_id, price=price, quantity=quantity, side=side, order_type=order_type, stop_price=stop_price, displayed_quantity=displayed_quantity)

def main(page: ft.Page):
    order_book = OrderBook()
    order_id_counter = 1
    running = False

    def update_gui():
        order_book.trigger_stop_orders()
        order_book_state = order_book.get_order_book()

        buy_list.controls.clear()
        sell_list.controls.clear()
        history_list.controls.clear()
        liquidity_list.controls.clear()

        for order in order_book_state['buy_orders']:
            color = "blue" if order.quantity <= 10 else "yellow"
            buy_list.controls.append(ft.ListTile(title=ft.Text(order.order_id), subtitle=ft.Text(f"Price: {order.price}, Quantity: {order.quantity}, Type: {order.order_type}"), text_color=color))

        for order in order_book_state['sell_orders']:
            color = "red" if order.quantity <= 10 else "yellow"
            sell_list.controls.append(ft.ListTile(title=ft.Text(order.order_id), subtitle=ft.Text(f"Price: {order.price}, Quantity: {order.quantity}, Type: {order.order_type}"), text_color=color))

        order_history = order_book.get_order_history()
        for hist in order_history:
            history_list.controls.append(ft.ListTile(title=ft.Text(f"Buy Order ID: {hist[0]}, Sell Order ID: {hist[1]}, Quantity: {hist[2]}, Price: {hist[3]}")))

        liquidity_pool = order_book.get_liquidity_pool()
        for price, liquidity in sorted(liquidity_pool.items()):
            liquidity_list.controls.append(ft.ListTile(title=ft.Text(f"Price: {price}, Buy Liquidity: {liquidity['buy']}, Sell Liquidity: {liquidity['sell']}")))

        page.update()

    def add_random_order(e):
        nonlocal order_id_counter
        order = generate_random_order(f'{order_id_counter}')
        order_book.add_order(order)
        order_id_counter += 1
        update_gui()

    def match_orders(e):
        order_book.match_orders()
        update_gui()

    def start_updates(e):
        nonlocal running
        running = True
        update_orders()

    def stop_updates(e):
        nonlocal running
        running = False

    def update_orders():
        if running:
            add_random_order(None)
            page.timer(1000, update_orders)

    def search_orders(e):
        query = search_box.value.lower()
        buy_list.controls.clear()
        sell_list.controls.clear()
        for order in order_book.get_order_book()['buy_orders']:
            if query in order.order_id.lower() or query in str(order.price).lower():
                color = "blue" if order.quantity <= 10 else "yellow"
                buy_list.controls.append(ft.ListTile(title=ft.Text(order.order_id), subtitle=ft.Text(f"Price: {order.price}, Quantity: {order.quantity}, Type: {order.order_type}"), text_color=color))
        for order in order_book.get_order_book()['sell_orders']:
            if query in order.order_id.lower() or query in str(order.price).lower():
                color = "red" if order.quantity <= 10 else "yellow"
                sell_list.controls.append(ft.ListTile(title=ft.Text(order.order_id), subtitle=ft.Text(f"Price: {order.price}, Quantity: {order.quantity}, Type: {order.order_type}"), text_color=color))

    buy_list = ft.ListView(expand=1)
    sell_list = ft.ListView(expand=1)
    history_list = ft.ListView(expand=1)
    liquidity_list = ft.ListView(expand=1)

    search_box = ft.TextField(hint_text="Search orders...", on_change=search_orders)
    status_bar = ft.Text("")

    page.add(
        ft.Column([
            ft.Row([
                ft.Container(
                    content=buy_list,
                    border=ft.border.all(1, "blue"),
                    border_radius=5,
                    padding=10,
                    expand=True,
                ),
                ft.Container(
                    content=sell_list,
                    border=ft.border.all(1, "red"),
                    border_radius=5,
                    padding=10,
                    expand=True,
                ),
            ]),
            ft.Container(
                content=history_list,
                border=ft.border.all(1, "black"),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Container(
                content=liquidity_list,
                border=ft.border.all(1, "green"),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            search_box,
            ft.Row([
                ft.ElevatedButton("Add Random Order", on_click=add_random_order),
                ft.ElevatedButton("Match Orders", on_click=match_orders),
                ft.ElevatedButton("Start Updates", on_click=start_updates),
                ft.ElevatedButton("Stop Updates", on_click=stop_updates),
            ]),
            status_bar,
        ])
    )

ft.app(target=main)
