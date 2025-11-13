import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.ui.page_base import PageBase
from automation.utilities.save_download_state import save_state
from selenium.common.exceptions import TimeoutException
from automation.utilities.excel_mapper import ReportPageMapperKeys, report_mapper
from automation.config.locators import ( 
    InboundPageLocators, 
    AuditReportsMapper, 
    TransactionalPageLoaders, 
    SettlementReportLocators 
    )

from automation.utilities.logger import logger

class ReportDownloader(PageBase):
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


    def download_inbound_page(
        self, 
        locator=None,
        report_name=None,
        download_path=None, 
        order_id=None,
        report_type=None,
    ):
        """
        Handles RazorERP modal lifecycle perfectly across multiple downloads.
        Ensures overlays are cleaned, dialogs reset, and no click intercepts happen.
        """

        logger.info(f"Starting download process for Order ID: {order_id}, Report: {report_name}, Type: {report_type}")

        # --- Step 0: Validation ---
        if locator is None or locator != ReportPageMapperKeys.INBOUND:
            logger.error("Invalid locator provided.")
            return False

        # --- Step 1: Ensure correct page ---
        page_url = report_mapper.get_page_url(locator)
        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(2)
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
            time.sleep(2)
            logger.info("Clicked 'Settlements' tab successfully.")
        except Exception as e:
            logger.warning(f"Settlements tab click intercepted. Retrying via JS: {e}")
            self.driver.execute_script("arguments[0].click();", self.driver.find_element(*InboundPageLocators.SETTLEMENTS_TAB))
            return False

        # --- Step 3: Search for order ---
        orders_search_field = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD, timeout=20)
        if not orders_search_field:
            logger.error("Search field not found.")
            return False

        try:
            try:
                self.clear_input(orders_search_field)
            except Exception:
                try:
                    orders_search_field.clear()
                except Exception:
                    pass

            time.sleep(1)
            orders_search_field.send_keys(order_id)
            time.sleep(1)
            orders_search_field.send_keys(Keys.ENTER)
            logger.info(f"Searched for order ID: {order_id}")
            time.sleep(2)
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

        if not self.driver.execute_script("return $('#div_ReportsContainer').length"):
            logger.warning("Modal element missing. Reloading page to reset RazorERP context.")
            self.driver.refresh()
            time.sleep(4)
            return self.download_inbound_page(
                locator=locator,
                report_name=report_name,
                download_path=download_path,
                order_id=order_id,
                report_type=report_type
            )

        # --- Step 5: Open modal ---
        download_button = self.wait.wait_for_element_to_be_visible(
            InboundPageLocators.STANDARD_DOWNLOAD_BUTTON if report_type.lower() == "standard"
            else InboundPageLocators.DOWNLOAD_BUTTON_NEW, timeout=15)
        if not download_button:
            logger.error("Download button not found.")
            return False

        try:
            download_button.click()
            time.sleep(1)
        except Exception:
            self.driver.execute_script("arguments[0].click();", download_button)
        logger.info("Clicked Print/Download button; waiting for modal.")

        time.sleep(1)

        # --- Step 6: Wait for modal ---
        reports_container = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD_SETTLEMENTS, timeout=10)
        if not reports_container:
            logger.error("Reporting Station modal didn't appear.")
            self.driver.save_screenshot(f"screenshots/modal_missing_{order_id}.png")
            return False

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
        nested_checkboxes = parent_div.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for cb in nested_checkboxes:
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

        for cb in nested_checkboxes:
            try:
                if cb.is_selected():
                    cb.click()
            except Exception as e:
                logger.warning(f"Could not deselect checkbox {cb.get_attribute('id')}: {e}")

        save_state.add(order_id, report_name, downloaded=True, uploaded=False)
        time.sleep(1)

        # --- Step 9: Close modal ---
        try:
            close_button = self.wait.wait_for_element_to_be_visible(
                (By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/following-sibling::*[1]")
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
        return True

    def download_transaction_report(
        self, 
        locator=None,
        report_name=None,
        download_path=None, 
        order_id=None,
        report_type=None,
    ):

        if locator is None and locator != ReportPageMapperKeys.INVOICE:
            logger.error("Invalid locator provided for downloading inbound page report.")
            return False

        if self.driver is None:
            logger.error("Invalid driver provided for downloading inbound page report.")
            return False
        
        if report_type is None:
            logger.error("Invalid report type provided for downloading inbound page report.")
            return False

        page_url = report_mapper.get_page_url(locator)

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
                            time.sleep(10)
                            
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
                    
    def download_audit_report(
        self, 
        locator=None,
        report_name=None,
        download_path=None, 
        order_id=None,
        report_type=None,
    ):

        if locator is None and locator != ReportPageMapperKeys.AUDIT:
            logger.error("Invalid locator provided for downloading inbound page report.")
            return False

        if self.driver is None:
            logger.error("Invalid driver provided for downloading inbound page report.")
            return False
        
        if report_type is None:
            logger.error("Invalid report type provided for downloading inbound page report.")
            return False

        page_url = report_mapper.get_page_url(locator)
        
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
        
        search_field = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.SEARCH_FIELD)
        if search_field:
            try:
                self.clear_input(search_field)
            except Exception:
                try:
                    search_field.clear()
                except Exception:
                    pass

            search_field.send_keys(order_id)
            time.sleep(2)
            search_field.send_keys(Keys.ENTER)
            time.sleep(2)
            
            table_cell = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.CELL_LOCATION, timeout=10)
            if table_cell:
                table_cell.click()
                time.sleep(2)

                download_button = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.PRINT_BUTTON)
                download_button.click()
                time.sleep(2)
    
                checkbox_audit_report = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.CHECKBOX_AUDIT_REPORT)
                checkbox_include_drives = self.wait.wait_for_element_to_be_visible(AuditReportsMapper.CHECBOX_INCLUDE_DRIVES)

                if checkbox_audit_report and not checkbox_audit_report.is_selected():
                    checkbox_audit_report.click()
                    time.sleep(1)
                
                if checkbox_include_drives and not checkbox_include_drives.is_selected():
                    checkbox_include_drives.click()
                    time.sleep(1)

                download_button = self.wait.wait_for_element_to_be_visible((
                    By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/preceding-sibling::*[1]"), timeout=10)
                if download_button:
                    download_button.click()
                    logger.info(f"Download initiated for Audit report '{report_name}' of type '{report_type}'.")
                    time.sleep(2)
                    save_state.add(order_id, report_name, downloaded=True, uploaded=False)
                    return True
            else:
                logger.error(f"Order ID '{order_id}' not found in Audit Reports.")
                return False
        else:
            logger.error("Search field not found.")
            return False   

    def download_settlement_page(
        self, 
        locator=None,
        report_name=None,
        download_path=None, 
        order_id=None,
        report_type=None,
    ):
        """
        Handles RazorERP modal lifecycle perfectly across multiple downloads.
        Ensures overlays are cleaned, dialogs reset, and no click intercepts happen.
        """

        logger.info(f"Starting download process for Order ID: {order_id}, Report: {report_name}, Type: {report_type}")

        # --- Step 0: Validation ---
        if locator is None or locator != ReportPageMapperKeys.SETTLEMENT:
            logger.error("Invalid locator provided.")
            return False

        # --- Step 1: Ensure correct page ---
        page_url = report_mapper.get_page_url(locator)

        if self.driver.current_url != page_url:
            self.driver.get(page_url)
            time.sleep(5)
            self.driver.execute_script("""
                const el = document.getElementById('gritter-notice-wrapper');
                if (el) { el.style.display = 'none'; el.style.visibility = 'hidden'; }
            """)
            logger.info("Navigated to settlement report page and cleared notification overlays.")

        # --- Step 3: Search for order ---
        orders_search_field = self.wait.wait_for_element_to_be_visible(SettlementReportLocators.SEARCH_FIELD, timeout=20)
        if not orders_search_field:
            logger.error("Search field not found.")
            return False

        try:
            try:
                self.clear_input(orders_search_field)
            except Exception:
                try:
                    orders_search_field.clear()
                except Exception:
                    pass

            time.sleep(1)
            orders_search_field.send_keys(order_id)
            time.sleep(2)
            orders_search_field.send_keys(Keys.ENTER)
            logger.info(f"Searched for order ID: {order_id}")
            time.sleep(2)
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

        if not self.driver.execute_script("return $('#div_ReportsContainer').length"):
            logger.warning("Modal element missing. Reloading page to reset RazorERP context.")
            self.driver.refresh()
            time.sleep(4)
            return self.download_inbound_page(
                locator=locator,
                report_name=report_name,
                download_path=download_path,
                order_id=order_id,
                report_type=report_type
            )
        
        download_button = self.wait.wait_for_element_to_be_visible(
            SettlementReportLocators.STANDARD_DOWNLOAD_BUTTON if report_type.lower() == "standard"
            else SettlementReportLocators.DOWNLOAD_BUTTON_NEW, timeout=15)
        if not download_button:
            logger.error("Download button not found.")
            return False

        try:
            download_button.click()
            time.sleep(2)
        except Exception:
            self.driver.execute_script("arguments[0].click();", download_button)
        logger.info("Clicked Print/Download button; waiting for modal.")

        time.sleep(2)

        # --- Step 6: Wait for modal ---
        if report_type.lower() == "standard":
            reports_container = self.wait.wait_for_element_to_be_visible(SettlementReportLocators.REPORTS_LIST_CONTAINER, timeout=10)
            if not reports_container:
                logger.error("Reporting Station modal didn't appear.")
                self.driver.save_screenshot(f"screenshots/modal_missing_{order_id}.png")
                return False

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
            nested_checkboxes = parent_div.find_elements(By.XPATH, ".//input[@type='checkbox']")
            for cb in nested_checkboxes:
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

            for cb in nested_checkboxes:
                try:
                    if cb.is_selected():
                        cb.click()
                except Exception as e:
                    logger.warning(f"Could not deselect checkbox {cb.get_attribute('id')}: {e}")

            save_state.add(order_id, report_name, downloaded=True, uploaded=False)
            time.sleep(1)

            # --- Step 9: Close modal ---
            try:
                close_button = self.wait.wait_for_element_to_be_visible(
                    (By.XPATH, "//*[@id='dlgPrint_ButtonPreview']/following-sibling::*[1]")
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
            return True
        else:
            logger.info(f"Handling PRINT/NEW download for {report_name}")
            reports_container = self.wait.wait_for_element_to_be_visible((By.ID, SettlementReportLocators.MODAL_ID), timeout=10)
            if not reports_container:
                logger.error("Reporting Station modal didn't appear.")
                self.driver.save_screenshot(f"screenshots/modal_missing_{order_id}_{report_name}.png")
                return False

            time.sleep(1)

            # Search for the report
            search_field = self.wait.wait_for_element_to_be_visible(SettlementReportLocators.SEARCH_FIELD_NEW, timeout=10)
            if not search_field:
                logger.error("Search field in modal not found.")
                self.driver.save_screenshot(f"screenshots/search_missing_{order_id}_{report_name}.png")
                return False

            search_field.clear()
            search_field.send_keys(report_name)
            time.sleep(1)
            search_field.send_keys(Keys.ENTER)
            time.sleep(1)
            logger.info(f"Entered report name '{report_name}' in search field and pressed enter")

            # Assume the first matching item is selected or click it
            # Perhaps there's a list, click the first item
            try:
                # Find the report item, perhaps by text
                report_item = self.wait.wait_for_element_to_be_visible((By.XPATH, f"//*[contains(text(), '{report_name}')]"), timeout=10)
                if report_item:
                    report_item.click()
                    logger.info(f"Clicked report item '{report_name}'")
                    time.sleep(1)
                else:
                    logger.error(f"Report '{report_name}' not found in the list.")
                    self.driver.save_screenshot(f"screenshots/report_not_found_{order_id}_{report_name}.png")
                    return False
            except Exception as e:
                logger.error(f"Failed to select report '{report_name}': {e}")
                self.driver.save_screenshot(f"screenshots/select_error_{order_id}_{report_name}.png")
                return False

            # Now, trigger download, perhaps there's a download button in the modal
            final_download_button = self.wait.wait_for_element_to_be_visible(
                (By.XPATH, "//button[contains(text(), 'Download')]"), timeout=10
            )
            if not final_download_button:
                logger.error("Download button in modal not found.")
                self.driver.save_screenshot(f"screenshots/download_btn_missing_{order_id}_{report_name}.png")
                return False

            try:
                self.driver.execute_script("arguments[0].click();", final_download_button)
            except Exception as e:
                logger.warning(f"Download button JS click failed ({e})")
                final_download_button.click()
            logger.info(f"Download initiated for report '{report_name}' of type '{report_type}'.")

            save_state.add(order_id, report_name, downloaded=True, uploaded=False)
            time.sleep(1)

            # Close modal
            try:
                close_button = self.wait.wait_for_element_to_be_visible(
                    (By.XPATH, "//button[@title='Close']")
                )
                if close_button:
                    close_button.click()
                    logger.info("Modal closed successfully.")
                else:
                    raise TimeoutException("Close button not clickable.")
            except Exception as e:
                logger.warning(f"Modal close failed ({e}), using JS fallback.")
                self.driver.execute_script("""
                    document.querySelectorAll('.ui-dialog-titlebar-close, button.ui-dialog-titlebar-close')
                        .forEach(btn => btn.click());
                """)
            time.sleep(2)
            return True
