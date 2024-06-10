# cLOB-py: Centralized Limit Order Book in Python

</a>
    <a href="[https://github.com/arshkumarsingh/cLOB-py/blob/LICENSE]">
    <img src="https://img.shields.io/github/license/arshkumarsingh/cLOB-py"/>
</a>
Welcome to **cLOB-py**, a sophisticated centralized limit order book (LOB) system implemented in Python. This project simulates a real-world trading environment, allowing you to create, manage, and match buy and sell orders efficiently. 

## Features

### Core Functionalities
- **Order Creation:** Supports both manual and random order creation with various parameters like price, quantity, side (buy/sell), and order type (limit/market).
- **Order Matching:** Efficiently matches buy and sell orders based on price and timestamp, ensuring the best possible trades.
- **Order Cancellation:** Allows users to cancel existing orders from the order book.
- **Order Book State:** Maintains a comprehensive record of all active buy and sell orders.
- **Order History:** Keeps a detailed history of matched orders.

### Advanced Under-the-Hood Features
- **Efficient Data Structures:** Utilizes heaps for maintaining buy and sell orders, ensuring optimal time complexity for insertion and retrieval operations.
- **Thread-Safe Operations:** Implements mutex locks to ensure thread-safe updates to the order book state and GUI.
- **Logging:** Comprehensive logging of all major events like order additions, cancellations, and matches for audit and debugging purposes.
- **Realistic Order Generation:** Generates realistic random orders based on current market prices and other parameters.

### Graphical User Interface
- **Real-time Updates:** GUI updates every 5 seconds to reflect the current state of the order book.
- **Order Book Display:** Separate tree views for buy and sell orders, showing price, order count, and quantity.
- **Order Form:** Easy-to-use form for adding manual orders with input fields for order ID, price, quantity, side, and type.
- **Statistics:** Displays statistics like total buy/sell orders and average buy/sell prices.
- **Charts:** Visual representation of order distributions using bar charts.

## Getting Started
![pyqt](https://github.com/arshkumarsingh/cLOB-py/assets/66940182/9da778af-759e-4d77-a421-36b127acde72)

### Prerequisites
- Python 3.x
- PyQt5
- Pandas
- Matplotlib

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/arshkumarsingh/cLOB-py
    cd cLOB-py
    ```
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application
1. Navigate to the project directory:
    ```bash
    cd /path/to/cLOB-py
    ```
2. Execute the main GUI script:
    ```bash
    python gui.py
    ```

## Project Structure

```plaintext
cLOB-py/
├── gui.py                 # Main GUI application
├── order.py               # Order class definition
├── order_book.py          # Order book implementation
├── requirements.txt       # Required packages
└── README.md              # Project documentation
```

### `order.py`
Defines the `Order` class with attributes like timestamp, order ID, symbol, price, quantity, side, and order type. Includes methods for initialization and representation.

### `order_book.py`
Implements the `OrderBook` class, managing buy and sell orders using heaps, matching orders, maintaining order history, and providing utility functions for order validation and realistic order generation.

### `gui.py`
Contains the `OrderBookGUI` class which provides a comprehensive graphical interface for interacting with the order book. Features include real-time updates, order form, order book display, filtering options, statistics display, and order distribution charts.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your improvements.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
Special thanks to all contributors and the open-source community for their valuable support.

---

Feel free to explore and enhance the functionalities of **cLOB-py**. Happy trading!

