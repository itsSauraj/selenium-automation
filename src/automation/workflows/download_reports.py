import os
from automation.ui.navigation import Navigation, PageNavigation
from automation.utilities.excel_reader import get_orders_from_excel
from automation.utilities.file_manager import create_directory_if_not_exists
from automation.config.settings import settings
from automation.utilities.logger import logger

class DownloadReportsWorkflow:
    """
    This workflow handles the downloading of reports based on the orders defined in the Excel file.
    """

    def __init__(self, driver):
        """
        Initializes the DownloadReportsWorkflow.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.navigation = Navigation(driver)

    def run(self):
        """Runs the download reports workflow."""
        logger.info("Starting the download reports workflow.")

        # Get orders from the Excel file
        orders = get_orders_from_excel()

        if not orders:
            logger.error("No orders found in the Excel file.")
            return

        for order_id, reports in orders.items():
            logger.info(f"Processing order: {order_id}")

            # Create a directory for the order
            order_download_path = os.path.join(settings.DOWNLOAD_PATH, str(order_id))
            create_directory_if_not_exists(order_download_path)

            for report in reports:
                report_name = report.get("Report Name")
                page_location = report.get("Page Location")

                logger.info(f"Downloading report: '{report_name}' from page: '{page_location}'")

                # The following is a placeholder for the actual navigation and download logic.
                # You will need to update this part with the actual steps to download the report.

                # 1. Navigate to the page location.
                #    This might involve a series of clicks and navigations.
                #    You can use the self.navigation.execute_step() method for this.

                # 2. Find the report link or button and click it to download.

                # 3. The downloaded file will be saved to the default download directory of the browser.
                #    You will need to move the file to the order_download_path.

                # Example of how you might use the navigation module:
                # self.navigation.execute_step({"Action": "navigate", "Value": "https://example.com/some-page"})
                # self.navigation.execute_step({"Action": "click", "LocatorType": "xpath", "LocatorValue": f"//a[text()='{report_name}']"})

        logger.info("Download reports workflow completed.")