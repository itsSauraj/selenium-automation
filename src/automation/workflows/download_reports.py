import os

from automation.ui.navigation import Navigation
from automation.ui.page_base import PageBase
from automation.utilities.excel_reader import excel_reader
from automation.utilities.save_download_state import save_state
from automation.utilities.file_manager import create_directory_if_not_exists
from automation.utilities.report_downloader import ReportDownloader
from automation.config.settings import settings
from automation.config.excel_mapper import report_mapper
from automation.config.locators import ( report_mapper_locator, ReportMapperKeys )

from automation.utilities.logger import logger

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
        self.report_keys = report_mapper_locator.get_all_keys()
        self.download_function = ReportDownloader(driver)

    def run(self):
        """Runs the download reports workflow."""
        logger.info("Starting the download reports workflow.")

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

                logger.info(f"Preparing to download report for Order ID: {order_id} - Report Name: {report_name}, Report Type: {report_type}")
                save_state.add(order_id, report_name, downloaded=False, uploaded=False)

                if not report_name:
                    logger.warning(f"Skipping report with no name for Order ID: {order_id}.")
                    continue

                report_name_map = report_mapper.get_report_key(report_name)
                logger.info(f"Report map for report : {report_name} is map: {report_name_map}")
                if report_name_map is None:
                    logger.warning(f"Report name '{report_name}' not recognized. Skipping download.")
                    continue

                if report_name_map == ReportMapperKeys.INBOUND_PAGE:
                    self.download_function.download_inbound_page(
                        locator=ReportMapperKeys.INBOUND_PAGE,
                        report_name=report_name,
                        order_download_path=order_download_path,
                        order_id=order_id,
                        report_type=report_type
                    )
                elif report_name_map == ReportMapperKeys.TRANSACTION_HISTORY_REPORT:
                    self.download_function.download_transaction_report(
                        locator=ReportMapperKeys.TRANSACTION_HISTORY_REPORT, 
                        report_name=report_name, 
                        order_download_path=order_download_path, 
                        order_id=order_id, 
                        report_type=report_type
                    )
                elif report_name_map is ReportMapperKeys.SETTLEMENT_REPORT:
                    continue
                    self.download_function.download_settlement_page(
                        locator=ReportMapperKeys.SETTLEMENT_REPORT,
                        report_name=report_name,
                        order_download_path=order_download_path,
                        order_id=order_id,
                    report_type=report_type
                )

        logger.info("Download reports workflow completed.")