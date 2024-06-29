import pandas as pd
import logging

def export_orders_to_excel(matched_orders, filename='matched_orders.xlsx'):
    """
    Export matched orders to an Excel file.

    Args:
        matched_orders (list): List of matched orders.
        filename (str, optional): Name of the Excel file. Defaults to 'matched_orders.xlsx'.

    Returns:
        str: Success message if export is successful, error message otherwise.
    """
    # Check if there are any matched orders to export
    if not matched_orders:
        logging.info("No matched orders to export.")
        print("No matched orders to export.")
        return "No matched orders to export."

    # Convert matched orders to a DataFrame
    df = pd.DataFrame(matched_orders)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Set column names for the DataFrame
    df.columns = ["Buy Order ID", "Sell Order ID", "Symbol", "Quantity", "Price", "Timestamp"]

    try:
        # Create an ExcelWriter object
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        
        # Write the DataFrame to an Excel sheet
        df.to_excel(writer, sheet_name='Matched Orders', index=False)

        # Access the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Matched Orders']

        # Add number and date formats to the worksheet columns
        format1 = workbook.add_format({'num_format': '0.00'})  # Format for decimal numbers
        format2 = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})  # Format for dates
        worksheet.set_column('A:F', 20)  # Set column width for all columns
        worksheet.set_column('E:E', 12, format1)  # Set column width and format for quantity column
        worksheet.set_column('F:F', 20, format2)  # Set column width and format for timestamp column

        # Close the ExcelWriter object
        writer.close()
        
        # Log success message
        logging.info(f"Matched orders exported to {filename}.")
        print(f"Matched orders exported to {filename}.")
        
        # Return success message
        return f"Matched orders exported to {filename}."
    
    except Exception as e:
        # Log error message
        logging.error(f"Failed to export to Excel: {e}")
        print(f"Failed to export to Excel: {e}")
        
        # Return error message
        return f"Failed to export to Excel: {e}"
