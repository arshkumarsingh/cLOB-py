# cLOB-py: Centralized Limit Order Book in Python

</a>
    <a href="[https://github.com/arshkumarsingh/cLOB-py/blob/LICENSE]">
    <img src="https://img.shields.io/github/license/arshkumarsingh/cLOB-py"/>
</a>

## Repo Stats

![Alt](https://repobeats.axiom.co/api/embed/109bbd3a3002d66cea2ad9243f78cbea720c219a.svg "Repobeats analytics image")


Welcome to **cLOB-py**, a comprehensive and efficient Centralized Limit Order Book implementation in Python. This project offers a robust solution for managing and visualizing buy and sell orders across various financial symbols, providing an intuitive GUI and powerful backend functionalities.

## Features

- **Order Management**: Add, match, and cancel buy and sell orders with ease.
- **User Authentication**: Secure user management with role-based access.
- **Data Export**: Export matched orders to Excel for further analysis.
- **Real-Time Filtering**: Apply price and quantity filters to view specific orders.
- **Visual Analytics**: Generate statistics and visualize order distributions with interactive charts.
- **Logging**: Comprehensive logging for auditing and troubleshooting.

## Installation

To set up and run cLOB-py on your local machine, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/arshkumarsingh/cLOB-py.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd cLOB-py
   ```

3. **Install Dependencies**:
   Make sure you have Python installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python main_window.py
   ```

## Project Structure

- **main_window.py**: The main graphical user interface (GUI) for managing and visualizing orders.
- **order.py**: Defines the `Order` class, encapsulating order properties and validation logic.
- **order_book.py**: Manages the order book operations, including adding, matching, and canceling orders, and maintains order history.
- **custom_order_dialog.py**: Provides a dialog interface for creating custom orders.
- **user.py**: Handles user creation, authentication, and role management.

## Usage

### Adding Orders

- **Manual Orders**: Click "Add Custom Order" in the toolbar to input order details manually.
- **Random Orders**: Click "Add Random Order" to generate random buy and sell orders.

### Matching Orders

- Click the "Match Orders" button to execute order matching based on price and quantity.

### Canceling Orders

- Enter the order ID in the designated input field and click "Cancel Order" to remove an order.

### Exporting Data

- Click "Export to Excel" to save matched orders to an Excel file for analysis.

### Filtering Orders

- Specify the price and quantity range in the filter section and click "Apply Filter" to refine order visibility.

## Logging

cLOB-py maintains detailed logs for all operations, enhancing transparency and aiding in debugging:

- **custom_order_dialog.log**
- **order_book.log**
- **order_book_gui.log**
- **user.log**

## Dependencies

- Python 3.6+
- PyQt5
- Redis
- bcrypt
- pandas
- matplotlib

## Contributing

Contributions are welcome! Feel free to fork the repository, make improvements, and submit a pull request. Please ensure your changes adhere to the project's coding standards and include appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any inquiries or support, please reach out to [your-email@example.com].

---

We hope cLOB-py serves as a valuable tool for your trading and financial analysis needs. Happy trading!
