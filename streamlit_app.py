import streamlit as st
import pandas as pd
from order_book import OrderBook, fetch_current_prices, generate_realistic_order
from user import User
import excel_exporter
from order import Order

# Initialize the order book
order_book = OrderBook()

# Sample data for symbols
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
current_prices = fetch_current_prices(symbols)

# Streamlit app layout
st.title("Order Book Management System")

# User login
st.sidebar.header("User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
role = st.sidebar.selectbox("Role", ["admin", "trader", "viewer"])

if st.sidebar.button("Login"):
    user = User(username, password, role)
    st.session_state['user'] = user
    st.sidebar.success(f"Logged in as {username}")

if 'user' in st.session_state:
    st.sidebar.write(f"Welcome, {st.session_state['user'].username}")

# Adding a custom order
st.header("Add Custom Order")
with st.form(key='add_order_form'):
    order_id = st.text_input("Order ID")
    symbol = st.selectbox("Symbol", symbols)
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", min_value=1)
    side = st.selectbox("Side", ["buy", "sell"])
    order_type = st.selectbox("Type", ["limit", "market"])
    add_order_button = st.form_submit_button("Add Order")

    if add_order_button:
        timestamp = int(pd.Timestamp.now().timestamp() * 1000)
        order = Order(timestamp, order_id, symbol, price, quantity, side, order_type)
        order_book.add_order(order)
        st.success(f"Order {order_id} added successfully.")

# Display the order book
st.header("Order Book")
order_book_data = order_book.get_order_book()
buy_orders_df = pd.DataFrame([order.__dict__ for _, _, order in order_book_data['buy_orders']])
sell_orders_df = pd.DataFrame([order.__dict__ for _, _, order in order_book_data['sell_orders']])
st.subheader("Buy Orders")
st.table(buy_orders_df)
st.subheader("Sell Orders")
st.table(sell_orders_df)

# Match orders
if st.button("Match Orders"):
    matched_orders = order_book.match_orders()
    st.success(f"Matched {len(matched_orders)} orders.")
    for buy, sell, qty in matched_orders:
        st.write(f"Matched {qty} units between buy order {buy.order_id} and sell order {sell.order_id}")

# Export matched orders to Excel
if st.button("Export Matched Orders to Excel"):
    matched_orders = order_book.get_order_history()
    result = excel_exporter.export_orders_to_excel(matched_orders)
    st.success(result)
