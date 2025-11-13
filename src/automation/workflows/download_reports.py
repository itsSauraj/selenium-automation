import os

from automation.ui.navigation import Navigation
from automation.ui.page_base import PageBase
from automation.utilities.excel_reader import excel_reader
from automation.utilities.save_download_state import save_state
from automation.utilities.file_manager import (
    create_directory_if_not_exists,
    check_if_folder_exists,
    remove_directory
)
from automation.utilities.report_downloader import ReportDownloader
from automation.config.settings import settings
from automation.utilities.excel_mapper import ReportPageMapperKeys, report_mapper
from automation.utilities.save_download_state import save_state

from automation.utilities.logger import logger
# from .upload_reports import UploadReportsWorkflow

class DownloadReportsWorkflow(PageBase):
    """
    This workflow handles the downloading of reports based on the data in the Excel file.
    """

    CUSTOM_FIELDS = None

    def __init__(self, driver = None):
        """
        Initializes the DownloadReportsWorkflow.

        Args:
            driver: The Selenium WebDriver instance.
        """
        super().__init__(driver)
        self.navigation = Navigation(driver)
        excel_reader.read_excel_file(sheet_name="Sheet1", custom_fields=self.CUSTOM_FIELDS)
        self.report_keys = report_mapper.get_all_keys()
        self.download_function = ReportDownloader(driver)
        self.save_state = save_state

    def run(self):
        """Runs the download reports workflow."""
        logger.info("Starting the download reports workflow.")

        last_downloaded_order = self.save_state.get_last_entry()

        print(f"Last downloaded order: {last_downloaded_order}")
        try:
            if last_downloaded_order.get("order_id"):
                logger.info(f"Resuming from last downloaded order ID: {last_downloaded_order.get('order_id')}")
        except Exception:
            logger.info("No previous download state found, starting fresh.")

        # return

        # Get data from the Excel file
        orders = excel_reader.get_orders_from_excel()

        if not orders:
            logger.error("No orders found in the Excel file.")
            return

        for order_id in orders:            
            logger.info(f"Setting up download for Order ID: {order_id}")
            reports_download_path = os.path.join(settings.DOWNLOAD_PATH, str(order_id))
            create_directory_if_not_exists(reports_download_path)

            self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": reports_download_path
            })

            if not order_id:
                logger.warning("Skipping row with no Order ID.")
                continue

            logger.info(f"Processing order: {order_id}")
            order_data = excel_reader.get_order_data_from_excel(order_id=order_id)

            if not order_data:
                logger.warning(f"No data found for Order ID: {order_id}. Skipping.")
                continue

            # Create a directory for the order
            order_download_path = os.path.join(settings.DOWNLOAD_PATH, str(order_id))
            create_directory_if_not_exists(order_download_path)

            for report_data in order_data:
                report_name = report_data.get(excel_reader.COLUMNS_MAPPER.REPORT_NAME)
                report_type = report_data.get(excel_reader.COLUMNS_MAPPER.REPORT_TYPE)
                page = report_data.get(excel_reader.COLUMNS_MAPPER.PAGE)

                logger.info(f"Preparing to download report for Order ID: {order_id} - Report Name: {report_name}, Report Type: {page}")
                save_state.add(order_id, report_name, downloaded=False, uploaded=False)

                if not report_name:
                    logger.warning(f"Skipping report with no name for Order ID: {order_id}.")
                    continue

                report_name_map = report_mapper.get_key(page)
                logger.info(f"Report map for report : {report_name} is map: {report_name_map}")
                if report_name_map is None:
                    logger.warning(f"Report name '{report_name}' not recognized. Skipping download.")
                    continue

                if report_name_map == ReportPageMapperKeys.INBOUND:
                    self.download_function.download_inbound_page(
                        locator=ReportPageMapperKeys.INBOUND,
                        report_name=report_name,
                        download_path=order_download_path,
                        order_id=order_id,
                        report_type=report_type
                    )
                elif report_name_map == ReportPageMapperKeys.INVOICE:
                    self.download_function.download_transaction_report(
                        locator=ReportPageMapperKeys.INVOICE, 
                        report_name=report_name, 
                        download_path=order_download_path,
                        order_id=order_id, 
                        report_type=report_type
                    )
                elif report_name_map is ReportPageMapperKeys.SETTLEMENT:
                    self.download_function.download_settlement_page(
                        locator=ReportPageMapperKeys.SETTLEMENT,
                        report_name=report_name,
                        download_path=order_download_path,
                        order_id=order_id,
                        report_type=report_type
                )
                elif report_name_map is ReportPageMapperKeys.AUDIT:
                    self.download_function.download_audit_report(
                        locator=ReportPageMapperKeys.AUDIT,
                        report_name=report_name,
                        download_path=order_download_path,
                        order_id=order_id,
                        report_type=report_type
                    )
                else:
                    logger.warning(f"No download method defined for report type: {report_name_map}")

            # DownloadReportsWorkflow

        logger.info("Download reports workflow completed.")