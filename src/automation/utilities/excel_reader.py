import openpyxl
import pandas as pd
from collections import defaultdict
from automation.config.settings import settings
from automation.utilities.logger import logger
from automation.config.excel_mapper import ExcelMapper

def get_orders_from_excel(sheet_name="Sheet1", custom_fields=None):
    """
    Reads orders and their associated reports from the specified Excel sheet.

    This function reads the Excel file and groups the reports by the 'Order ID' column.
    It returns a dictionary where the keys are the Order IDs and the values are a list
    of reports to be downloaded for that order.

    Args:
        sheet_name (str): The name of the sheet to read from. Defaults to "Sheet1".
        custom_fields (dict, optional): A dictionary to customize field names.
                                        Keys are existing field names and values are custom names.
    # Example of default field names in ExcelMapper:             
    #     ORDER_ID = "AUTO NAME"
    #     REPORT_TYPE = "REPORT TYPE"
    #     REPORT_NAME = "REPORT NAME"
    #     PRIORITY = "PRIORITY"

    Returns:
        defaultdict: A dictionary with Order IDs as keys and a list of report dictionaries as values.
    """

    excel_columns = ExcelMapper()
    if custom_fields is not None:
        excel_columns.set_multiple_custom_fields(custom_fields)

    try:
        df = pd.read_excel(settings.EXCEL_FILE_PATH, sheet_name=sheet_name)

        # Extract unique, non-null order IDs
        if excel_columns.ORDER_ID in df.columns:
            orders = set(df[excel_columns.ORDER_ID].dropna().unique())
        else:
            orders = set()

        logger.info(f"Successfully read {len(orders)} orders from sheet: {sheet_name}")
        return orders

    except FileNotFoundError:
        logger.error(f"Excel file not found at path: {settings.EXCEL_FILE_PATH}")
        return set()
    except KeyError:
        logger.error(f"Sheet '{sheet_name}' not found in the Excel file.")
        return set()
    except Exception as e:
        logger.error(f"An error occurred while reading the Excel file: {e}")
        return set()