import openpyxl
import pandas as pd
from collections import defaultdict
from automation.config.settings import settings
from automation.utilities.logger import logger
from automation.config.excel_mapper import ExcelMapper


class ExcelReader:
    """A utility class to read data from Excel files."""

    EXCEL_FILE_DATA = None
    SHEET_NAME = "Sheet1"
    COLUMNS_MAPPER = ExcelMapper()


    @classmethod
    def read_excel_file(cls, sheet_name="Sheet1", custom_fields=None):
        """
        Reads the Excel file and loads the specified sheet into a pandas DataFrame.

        Args:
            sheet_name (str): The name of the sheet to read from. Defaults to "Sheet1".

        Returns:
            pd.DataFrame: The DataFrame containing the sheet data.
        """
        
        if sheet_name:
            setattr(cls, "SHEET_NAME", sheet_name)

        if custom_fields is not None:
            cls.COLUMNS_MAPPER.set_multiple_custom_fields(custom_fields)

        try:
            df = pd.read_excel(settings.EXCEL_FILE_PATH, sheet_name=sheet_name)
            columns = cls.COLUMNS_MAPPER.get_all_fields()
            df = df[columns]

            setattr(cls, "EXCEL_FILE_DATA", df)
            logger.info(f"Successfully read Excel file: {settings.EXCEL_FILE_PATH}, Sheet: {sheet_name}")
            return df
        except FileNotFoundError:
            logger.error(f"Excel file not found at path: {settings.EXCEL_FILE_PATH}")
            return None
        except KeyError:
            logger.error(f"Sheet '{sheet_name}' not found in the Excel file.")
            return None
        except Exception as e:
            logger.error(f"An error occurred while reading the Excel file: {e}")
            return None

    @classmethod
    def get_orders_from_excel(cls):
        """
        Reads orders and their associated reports from the specified Excel sheet.

        This function reads the Excel file and groups the reports by the 'Order ID' column.
        It returns a dictionary where the keys are the Order IDs and the values are a list
        of reports to be downloaded for that order.

        Args:
            sheet_name (str): The name of the sheet to read from. Defaults to "Sheet1".
            custom_fields (dict, optional): A dictionary to customize field names.
                                            Keys are existing field names and values are custom names.
        Example of default field names in ExcelMapper:
            ORDER_ID = "AUTO NAME"
            REPORT_TYPE = "REPORT TYPE"
            REPORT_NAME = "REPORT NAME"
            PRIORITY = "PRIORITY"

        Returns:
            defaultdict: A dictionary with Order IDs as keys and a list of report dictionaries as values.
        """

        try:
            if cls.EXCEL_FILE_DATA is None:
                logger.warning("Excel file data is not loaded. Please call read_excel_file() first.")
                return defaultdict(list)

            # Extract unique, non-null order IDs
            if cls.COLUMNS_MAPPER.ORDER_ID in cls.EXCEL_FILE_DATA.columns:
                orders = set(cls.EXCEL_FILE_DATA[cls.COLUMNS_MAPPER.ORDER_ID].dropna().unique())
            else:
                orders = set()

            logger.info(f"Successfully read {len(orders)} orders from sheet: {cls.SHEET_NAME}")
            return orders

        except FileNotFoundError:
            logger.error(f"Excel file not found at path: {settings.EXCEL_FILE_PATH}")
            return set()
        except KeyError:
            logger.error(f"Sheet '{cls.SHEET_NAME}' not found in the Excel file.")
            return set()
        except Exception as e:
            logger.error(f"An error occurred while reading the Excel file: {e}")
            return set()

    @classmethod
    def get_order_data_from_excel(cls, sheet_name="Sheet1", order_id=None, custom_fields=None):
        """
        Reads data from the specified Excel sheet and returns it as a list of dictionaries.

        Each dictionary represents a row in the Excel sheet, with column headers as keys.

        Args:
            sheet_name (str): The name of the sheet to read from. Defaults to "Sheet1".
            order_id (str, optional): If provided, filters the data to only include rows with this Order ID.

        Returns:
            list: A list of dictionaries representing the rows in the Excel sheet.
        """

        if cls.EXCEL_FILE_DATA is None:
            logger.warning("Excel file data is not loaded. Please call read_excel_file() first.")
            return {}

        if order_id is None:
            logger.error("Order ID must be provided to fetch order data.")
            return {}
        
        try:
            # Filter rows by Order ID
            filtered_data = cls.EXCEL_FILE_DATA[
                cls.EXCEL_FILE_DATA[cls.COLUMNS_MAPPER.ORDER_ID] == order_id
            ]

            # Convert filtered DataFrame to list of dictionaries
            order_data = filtered_data.to_dict(orient='records')

            logger.info(f"Successfully fetched data for Order ID: {order_id} from sheet: {sheet_name}")
            return order_data

        except Exception as e:
            logger.error(f"An error occurred while fetching order data: {e}")
            return {}


excel_reader = ExcelReader()