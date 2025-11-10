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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from automation.config.excel_mapper import report_mapper
from automation.config.locators import ( report_mapper_locator, ReportMapperKeys, 
    InboundPageLocators, AuditReportsMapper, TransactionalPageLoaders, SettlementReportLocators )

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
                    self.download_function.download_settlement_page(
                        locator=ReportMapperKeys.SETTLEMENT_REPORT,
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
        """
        FINAL WORKING VERSION
        Handles RazorERP modal lifecycle perfectly across multiple downloads.
        Ensures overlays are cleaned, dialogs reset, and no click intercepts happen.
        """

        logger.info(f"--- Starting download process for Order ID: {order_id}, Report: {report_name}, Type: {report_type} ---")

        # --- Step 0: Validation ---
        if locator is None or locator != ReportMapperKeys.INBOUND_PAGE:
            logger.error("Invalid locator provided.")
            return False
        if not self.driver or not report_mapper.get_report_key(report_name) or not report_type:
            logger.error("Invalid arguments or missing report info.")
            return False

        # --- Step 1: Ensure correct page ---
        page_url = report_mapper_locator.get_page_url(report_mapper_locator.INBOUND_PAGE)
        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(5)
            self.driver.execute_script("""
                const el = document.getElementById('gritter-notice-wrapper');
                if (el) { el.style.display = 'none'; el.style.visibility = 'hidden'; }
            """)
            logger.info("Navigated to inbound page and cleared notification overlays.")

        # --- Step 2: Open Settlements tab ---
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.wait.wait_for_overlay_to_disappear(timeout=5)
            self.click(InboundPageLocators.SETTLEMENTS_TAB)
            time.sleep(4)
            logger.info("Clicked 'Settlements' tab successfully.")
        except Exception as e:
            logger.warning(f"Settlements tab click intercepted. Retrying via JS: {e}")
            self.driver.execute_script("arguments[0].click();", self.driver.find_element(*InboundPageLocators.SETTLEMENTS_TAB))
            time.sleep(3)

        # --- Step 3: Search for order ---
        orders_search_field = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD, timeout=20)
        if not orders_search_field:
            logger.error("Search field not found.")
            return False

        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", orders_search_field)
            orders_search_field.click()
            self.driver.execute_script("""
                const el = arguments[0];
                el.value = '';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, orders_search_field)
            time.sleep(0.5)
            orders_search_field.send_keys(order_id)
            orders_search_field.send_keys(Keys.ENTER)
            logger.info(f"Searched for order ID: {order_id}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Failed to search for order {order_id}: {e}")
            return False

        # --- Step 4: Select checkbox ---
        order_element = self.wait.wait_for_element_to_be_visible((By.CSS_SELECTOR, f"td[title='{order_id}']"), timeout=30)
        if not order_element:
            logger.error(f"Order ID '{order_id}' not found.")
            return False

        row = order_element.find_element(By.XPATH, "./ancestor::tr[1]")
        checkbox = row.find_element(By.XPATH, ".//td[1]//input[@type='checkbox']")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(1)
        logger.info(f"Selected checkbox for Order ID: {order_id}")
        logger.debug(self.driver.execute_script("return !!($('#div_ReportsContainer').data('uiDialog')?.isOpen)"))
        logger.debug(self.driver.execute_script("return typeof window.initializeReportModal"))

        if not self.driver.execute_script("return $('#div_ReportsContainer').length"):
            logger.warning("Modal element missing. Reloading page to reset RazorERP context.")
            self.driver.refresh()
            time.sleep(8)
            self.wait.wait_for_overlay_to_disappear(timeout=10)

        # --- Step 5: Open modal ---
        download_button = self.wait.wait_for_element_to_be_visible(
            InboundPageLocators.STANDARD_DOWNLOAD_BUTTON if report_type.lower() == "standard"
            else InboundPageLocators.DOWNLOAD_BUTTON_NEW, timeout=15)
        if not download_button:
            logger.error("Download button not found.")
            return False

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", download_button)
        try:
            download_button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", download_button)
        logger.info("Clicked Print/Download button; waiting for modal.")
        logger.debug(self.driver.execute_script("return $('#div_ReportsContainer').length"))

        time.sleep(4)

        # --- Step 6: Wait for modal ---
        reports_container = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD_SETTLEMENTS, timeout=20)
        if not reports_container:
            logger.error("Reporting Station modal didn't appear.")
            self.driver.save_screenshot(f"screenshots/modal_missing_{order_id}.png")
            return False

        self.driver.execute_script("""
            document.querySelectorAll('.ui-dialog, .ui-dialog-content, #div_ReportsContainer').forEach(el => {
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.style.opacity = '1';
                el.style.zIndex = '99999';
                el.style.pointerEvents = 'auto';
            });
        """)
        logger.info("Modal forced visible for checkbox accessibility.")
        time.sleep(1)

        # --- Step 7: Select report checkboxes ---
        parts = ["cb", "Doc", report_name]
        last_part = "_".join(word.capitalize() for word in parts[-1].split())
        report_id = "_".join([*parts[:-1], last_part])
        report_checkbox = self.wait.wait_for_element_to_be_visible((By.ID, report_id), timeout=15)
        if not report_checkbox:
            logger.error(f"Report checkbox {report_id} not found.")
            return False

        parent_div = report_checkbox.find_element(By.XPATH, "./ancestor::div[contains(@class,'print-dialog-doctype')]")
        for cb in parent_div.find_elements(By.XPATH, ".//input[@type='checkbox']"):
            try:
                if not cb.is_selected():
                    cb.click()
            except Exception as e:
                logger.warning(f"Could not select checkbox {cb.get_attribute('id')}: {e}")
        logger.info(f"Selected all related checkboxes for '{report_name}'.")

        # --- Step 8: Trigger download ---
        final_download_button = self.wait.wait_for_element_to_be_visible(
            (By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/preceding-sibling::*[1]"), timeout=15
        )
        if not final_download_button:
            logger.error("Final download button not found.")
            return False

        final_download_button.click()
        logger.info(f"Download initiated for report '{report_name}' of type '{report_type}'.")
        save_state.add(order_id, report_name, downloaded=True, uploaded=False)
        time.sleep(15)

        # --- Step 9: Close modal ---
        try:
            close_button = self.wait.wait_for_element_to_be_clickable(
                (By.XPATH, "//button[.//span[normalize-space(text())='Close']]"), timeout=10
            )
            if close_button:
                close_button.click()
                logger.info("Modal closed successfully via normal button click.")
            else:
                raise TimeoutException("Close button not clickable.")
        except Exception as e:
            logger.warning(f"Modal close failed ({e}), using JS fallback.")
            self.driver.execute_script("""
                document.querySelectorAll('.ui-dialog-titlebar-close, button.ui-dialog-titlebar-close')
                    .forEach(btn => btn.click());
            """)
        time.sleep(2)

        # --- Step 10: Modal cleanup + re-initialize RazorERP JS ---
        self.driver.execute_script("""
            if (window.jQuery) {
                // Destroy old instance
                const dlg = jQuery('#div_ReportsContainer');
                try { dlg.dialog('destroy'); } catch(e) {}
                dlg.remove();
            }

            // Clean up overlays
            document.querySelectorAll('.ui-widget-overlay, .ui-dialog, .ui-dialog-content').forEach(el => el.remove());
            document.body.style.overflow = '';
            document.body.style.position = '';

            // 💡 Re-run RazorERP's modal setup JS to reattach handlers
            if (window.initializeReportModal) {
                console.log('Reinitializing RazorERP modal via initializeReportModal()');
                window.initializeReportModal();
            } else {
                // fallback: trigger jQuery ready again to rebuild dialogs
                if (window.jQuery) jQuery(document).trigger('ready');
            }
        """)
        logger.info("Modal cleaned, removed, and RazorERP modal JS reinitialized for next cycle.")
        time.sleep(2)



        # --- Step 11: Wait for grid stabilization ---
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "table#RecyclingOrderList tbody tr")) > 0
            )
            logger.info("Page grid stabilized and ready for next search.")
        except Exception as e:
            logger.warning(f"Grid reload wait skipped: {e}")
        time.sleep(2)

        # --- Step 12: Deselect checkbox ---
        try:
            if checkbox.is_selected():
                checkbox.click()
                logger.info("Deselected checkbox after download.")
        except Exception as e:
            logger.debug(f"Failed to deselect checkbox cleanly: {e}")

        logger.info(f"--- Completed download process for Order ID: {order_id}, Report: {report_name} ---")
        return True

    def download_transaction_report(self, locator=None, report_name=None, order_download_path=None, order_id=None, report_type=None):

        if locator is None and locator != ReportMapperKeys.TRANSACTION_HISTORY_REPORT:
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

        page_url = report_mapper_locator.get_page_url(report_mapper_locator.TRANSACTION_HISTORY_REPORT)

        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(2)
            self.driver.execute_script("""
                const el = document.getElementById('gritter-notice-wrapper');
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                }
            """)
            
        time.sleep(2)
        
        orders_search_field = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.SEARCH_FIELD)
        if orders_search_field:
            orders_search_field.send_keys(order_id)
            time.sleep(2)
            orders_search_field.send_keys(Keys.ENTER)
            time.sleep(2)
            order_element = self.wait.wait_for_element_to_be_visible((By.CSS_SELECTOR, f"td[title='{order_id}']"), timeout=30)
            
            if order_element:
                self.actions.double_click(order_element)
                time.sleep(2)
                tabs = self.driver.window_handles
                primary = tabs[0]
                redirected = tabs[1]
                
                self.driver.switch_to.window(redirected)
                redirect_url = self.driver.current_url
                
                self.driver.close()
                self.driver.switch_to.window(primary)
                self.driver.get(redirect_url)
                time.sleep(2)
                
                sales_transaction_order = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.SALES_ORDER_HISTORY, timeout=30)
                
                if sales_transaction_order:
                    logger.info("Settle Table Found")
                    link = sales_transaction_order.get_attribute("href")
                    self.driver.get(link)
                    time.sleep(3)
                    invoices_tab = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.INVOICE_TAB)
                    
                    if invoices_tab:
                        invoices_tab.click()
                        time.sleep(1)
                        checkbox = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.INVOICE_TAB_TABLE_CHECKBOX)
                        checkbox.click()
                        
                        if report_type.lower() == 'standard':
                            download_button = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.STANDARD_DOWNLOAD_BUTTON)
                            download_button.click()
                            time.sleep(2)
                            
                            dialog_checkbox = self.wait.wait_for_element_to_be_visible(TransactionalPageLoaders.AR_REPORT_CHECKBOX)
                            dialog_checkbox.click()
                            time.sleep(1)
                            
                            final_download_button = self.wait.wait_for_element_to_be_visible((By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/preceding-sibling::*[1]"), timeout=2)
                            final_download_button.click()
                            logger.info(f"Download Button Clicked for report {report_name}")
                        else:
                            logger.warning("This type of report download is not Implented. Skipping...")
                else:
                    logger.error("Unable to load page")
                    
    def download_audit_report(self, locator=None, report_name=None, order_download_path=None, order_id=None, report_type=None):

        if locator is None and locator != ReportMapperKeys.AUDIT_ORDERS_PAGE:
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

        page_url = report_mapper_locator.get_page_url(report_mapper_locator.AUDIT_ORDERS_PAGE)
        
        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(2)
            self.driver.execute_script("""
                const el = document.getElementById('gritter-notice-wrapper');
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                }
            """)
            
        time.sleep(2)
        
        search_filed = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.SEARCH_FILED)
        if search_filed:
            search_filed.clear()
            search_filed.send_keys(order_id)
            time.sleep(2)
            search_filed.send_keys(Keys.ENTER)
            time.sleep(2)
            
            table_cell = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.CELL_LOCATION, timeout=10)
            if table_cell:
                table_cell.click()
                time.sleep(2)
                
                table_cell.send_keys(Keys.CONTROL, 'a')    