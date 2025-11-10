import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.ui.navigation import Navigation
from automation.ui.page_base import PageBase
from automation.utilities.excel_reader import excel_reader
from automation.utilities.save_download_state import save_state
from automation.utilities.file_manager import create_directory_if_not_exists
from automation.config.settings import settings
from automation.config.excel_mapper import report_mapper
from automation.config.locators import report_mapper_locator, ReportMapperKeys, InboundPageLocators
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
        self.download_function = ReportsDownloader(driver)

        # save_state.load() # TODO: Add load method if needed in future

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
                logger.info(f"Preparing to download report for Order ID: {order_id}")
                save_state.add(order_id, report_data.get(excel_reader.COLUMNS_MAPPER.REPORT_NAME), downloaded=False, uploaded=False)

                report_name = report_data.get(excel_reader.COLUMNS_MAPPER.REPORT_NAME)
                report_type = report_data.get(excel_reader.COLUMNS_MAPPER.REPORT_TYPE)

                if not report_name:
                    logger.warning(f"Skipping report with no name for Order ID: {order_id}.")
                    continue

                logger.info(f"Downloading report: {report_name} of type: {report_type} for Order ID: {order_id}")

                if report_mapper.get_report_key(report_name) is None:
                    logger.warning(f"Report name '{report_name}' not recognized. Skipping download.")
                    continue

                if report_mapper.get_report_key(report_name) is ReportMapperKeys.INBOUND_PAGE:
                    self.download_function.download_inbound_page(
                        locator=ReportMapperKeys.INBOUND_PAGE,
                        report_name=report_name,
                        order_download_path=order_download_path,
                        order_id=order_id,
                        report_type=report_type
                    )

        logger.info("Download reports workflow completed.")


class ReportsDownloader(PageBase):
    """
    A class to handle downloading specific reports.
    """

    def __init__(self, driver):
        """
        Initializes the LoginPage.

        Args:
            driver: The Selenium WebDriver instance.
        """
        super().__init__(driver)


    def download_inbound_page(self, locator=None, report_name=None, order_download_path=None, order_id=None, report_type=None):

        # TODO: Implement the decorator based check here
        if locator is None and locator != ReportMapperKeys.INBOUND_PAGE:
            logger.error("Invalid locator provided for downloading inbound page report.")
            return False

        if self.driver is None:
            logger.error("Invalid driver provided for downloading inbound page report.")
            return False
        
        if report_mapper.get_report_key(report_name) is None:
            logger.error("Invalid report name provided for downloading inbound page report.")
            return False

        if report_type is None:
            logger.error("Invalid report type provided for downloading inbound page report.")
            return False

        page_url = report_mapper_locator.get_page_url(report_mapper_locator.INBOUND_PAGE)

        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(5)
            self.driver.execute_script("""
                const el = document.getElementById('gritter-notice-wrapper');
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                }
            """)

        self.click(InboundPageLocators.SETTLEMENTS_TAB)
        time.sleep(5)
        
        orders_search_field = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD)
        if orders_search_field:
            orders_search_field.send_keys(order_id)
            time.sleep(2)
            orders_search_field.send_keys(Keys.ENTER)
            time.sleep(5)
            order_element = self.wait.wait_for_element_to_be_visible((By.CSS_SELECTOR, f"td[title='{order_id}']"), timeout=30)

            if order_element:
                order_checkbox = self.wait.wait_for_element_to_be_visible(InboundPageLocators.ORDER_CHECKBOX)
                if order_checkbox:
                    order_checkbox.click()
                    time.sleep(2)
                    if order_checkbox.is_selected() == False:
                        order_checkbox.click()
                        time.sleep(2)

                    if report_type.lower() == "standard":
                        download_button = self.wait.wait_for_element_to_be_visible(InboundPageLocators.STANDARD_DOWNLOAD_BUTTON)
                        if download_button:
                            download_button.click()
                            self.wait.wait_for_element_to_be_visible(InboundPageLocators.REPORTS_LIST_CONTAINER)

                            parts = ["cb", "Doc", report_name]
                            last_part = "_".join(word.capitalize() for word in parts[-1].split())
                            report_id = "_".join([*parts[:-1], last_part])

                            report_check_box = self.wait.wait_for_element_to_be_visible((By.ID, report_id))

                            parent_div = report_check_box.find_element(By.XPATH, "./ancestor::div[contains(@class, 'print-dialog-doctype')]")

                            # Find ALL checkboxes inside that parent section (including nested ones)
                            related_checkboxes = parent_div.find_elements(By.XPATH, ".//input[@type='checkbox']")

                            # 4️⃣ Loop through and check each one
                            for checkbox in related_checkboxes:
                                try:
                                    if not checkbox.is_selected():
                                        checkbox.click()
                                except Exception as e:
                                    logger.error(f"Error selecting checkbox: {e}")

                            # final_download_button = self.wait.wait_for_element_to_be_visible((By.XPATH, "//button[.//span[normalize-space(text())='Download']]"))
                            final_download_button = self.wait.wait_for_element_to_be_visible((By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/preceding-sibling::*[1]"), timeout=10)
                            if final_download_button:
                                final_download_button.click()
                                time.sleep(30)  # Wait for download to initiate
                                logger.info(f"Download initiated for report: {report_name} of type: {report_type} for Order ID: {order_id}")
                                save_state.add(order_id, report_name, downloaded=True, uploaded=False)
                                
                            else:
                                logger.error("Final download button not found. Cannot complete download.")
                        else:
                            logger.error("Download button not found. Cannot complete download.")
                    else:
                        download_button = self.wait.wait_for_element_to_be_visible(InboundPageLocators.DOWNLOAD_BUTTON_NEW)
                else:
                    logger.error("Order checkbox not found. Cannot complete download.")
        else:
            logger.error("Search field not found. Cannot complete search.")
