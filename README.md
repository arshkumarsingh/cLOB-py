# cLOB-py

cLOB-py is a Continuous Limit Order Book simulation project designed to mimic real-world trading environments. This project allows users to simulate the matching of buy and sell orders, track order history, and visualize order book depth in real-time.

## Features

### v0.2 Updates

- **Symbol Support for Orders**: Orders now include a `symbol` attribute, supporting multiple assets like AAPL, GOOGL, MSFT, AMZN, and TSLA.
- **Realistic Order Generation**: Enhanced order generation with realistic prices and quantities based on the symbol.
- **Enhanced GUI Display**: The GUI displays the `symbol` along with other order details in buy and sell order trees and the order history.
- **Order Matching and History**: Improved matching logic and detailed order history tracking.
- **Market Simulation Mode**: A new mode to stress test the order book with a large volume of random orders.
- **Bug Fixes and Performance Enhancements**: Various fixes and optimizations for better performance and reliability.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/arshkumarsingh/cLOB-py.git
    cd cLOB-py
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the GUI application**:
    ```bash
    python gui.py
    ```

2. **Use the buttons**:
    - **Add Random Order**: Generates and adds a random order to the order book.
    - **Match Orders**: Matches buy and sell orders in the order book.
    - **Start Auto Update**: Begins automatic generation and addition of random orders.
    - **Stop Auto Update**: Stops the automatic generation of orders.
    - **Start Market Simulation**: Initiates a stress test by generating a large number of random orders and updating the order book live.

## Screenshots

![Order Book](screenshots/order_book.png)
![Market Simulation](screenshots/market_simulation.png)

## Contributing

We welcome contributions to the cLOB-py project. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch to your fork.
4. Create a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please open an issue on the [GitHub repository](https://github.com/arshkumarsingh/cLOB-py).

---

### v0.1

For the initial version (v0.1), refer to the [v0.1 release notes](https://github.com/arshkumarsingh/cLOB-py/releases/tag/v0.1).

### v0.2

For the latest version (v0.2), refer to the [v0.2 release notes](https://github.com/arshkumarsingh/cLOB-py/releases/tag/v0.2).

---

We hope you find cLOB-py useful for your order book simulation needs. Happy trading!
