import openpyxl
from collections import defaultdict
from automation.config.settings import EXCEL_FILE_PATH
from automation.utilities.logger import logger

def get_orders_from_excel(sheet_name="Sheet1"):
    """
    Reads orders and their associated reports from the specified Excel sheet.

    This function reads the Excel file and groups the reports by the 'Order ID' column.
    It returns a dictionary where the keys are the Order IDs and the values are a list
    of reports to be downloaded for that order.

    Args:
        sheet_name (str): The name of the sheet to read from. Defaults to "Sheet1".

    Returns:
        defaultdict: A dictionary with Order IDs as keys and a list of report dictionaries as values.
    """
    try:
        workbook = openpyxl.load_workbook(EXCEL_FILE_PATH)
        sheet = workbook[sheet_name]
        
        orders = defaultdict(list)
        headers = [cell.value for cell in sheet[1]]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = dict(zip(headers, row))
            order_id = row_data.get("Order ID")
            if order_id:
                orders[order_id].append(row_data)

        logger.info(f"Successfully read {len(orders)} orders from sheet: {sheet_name}")
        return orders

    except FileNotFoundError:
        logger.error(f"Excel file not found at path: {EXCEL_FILE_PATH}")
        return defaultdict(list)
    except KeyError:
        logger.error(f"Sheet '{sheet_name}' not found in the Excel file.")
        return defaultdict(list)
    except Exception as e:
        logger.error(f"An error occurred while reading the Excel file: {e}")
        return defaultdict(list)