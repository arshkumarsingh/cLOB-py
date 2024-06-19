import pandas as pd
import logging

def export_orders_to_excel(matched_orders, filename='matched_orders.xlsx'):
    if not matched_orders:
        logging.info("No matched orders to export.")
        return "No matched orders to export."

    df = pd.DataFrame(matched_orders)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.columns = ["Buy Order ID", "Sell Order ID", "Symbol", "Quantity", "Price", "Timestamp"]

    try:
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Matched Orders', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Matched Orders']

        format1 = workbook.add_format({'num_format': '0.00'}) 
        format2 = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        worksheet.set_column('A:F', 20)
        worksheet.set_column('E:E', 12, format1)
        worksheet.set_column('F:F', 20, format2)

        writer.close()
        logging.info(f"Matched orders exported to {filename}.")
        return f"Matched orders exported to {filename}."
    except Exception as e:
        logging.error(f"Failed to export to Excel: {e}")
        return f"Failed to export to Excel: {e}"
