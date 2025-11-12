import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.ui.page_base import PageBase
from automation.ui.navigation import Navigation
from automation.config.locators import InboundPageLocators, report_mapper_locator, ReportMapperKeys
from automation.config.excel_mapper import report_mapper
from automation.utilities.logger import logger
from automation.utilities.file_manager import get_files_in_directory, create_directory_if_not_exists


class UploadReportsWorkflow(PageBase):
    """Handles uploading of reports for given recycling orders."""

    def __init__(self, driver):
        super().__init__(driver)
        self.navigation = Navigation(driver)

    def upload_reports(self, order_id: str, upload_dir: str) -> bool:
        """
        Uploads all report files for a given order.
        Returns True if successful, False otherwise.
        """
        logger.info(f"🚀 Starting upload for Order ID: {order_id}")

        # --- Step 1️⃣: Ensure correct page ---
        try:
            page_url = report_mapper_locator.get_page_url(ReportMapperKeys.INBOUND_PAGE)
            if self.driver.current_url != page_url:
                self.driver.get(page_url)
                time.sleep(5)
                self.driver.execute_script("""
                    const el = document.getElementById('gritter-notice-wrapper');
                    if (el) { el.style.display = 'none'; el.style.visibility = 'hidden'; }
                """)
                logger.info("✅ Navigated to inbound page and cleared overlays.")
        except Exception as e:
            logger.error(f"❌ Failed to open Inbound page: {e}")
            return False

        # --- Step 2️⃣: Open 'Settlements' tab ---
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.wait.wait_for_overlay_to_disappear(timeout=5)
            self.click(InboundPageLocators.SETTLEMENTS_TAB)
            logger.info("✅ Clicked 'Settlements' tab successfully.")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"⚠️ Settlements tab click intercepted, retrying via JS: {e}")
            try:
                tab_elem = self.driver.find_element(*InboundPageLocators.SETTLEMENTS_TAB)
                self.driver.execute_script("arguments[0].click();", tab_elem)
                time.sleep(2)
            except Exception as e2:
                logger.error(f"❌ Failed to open Settlements tab: {e2}")
                return False

        # --- Step 3️⃣: Search for the order ---
        try:
            search_field = self.wait.wait_for_element_to_be_visible(InboundPageLocators.SEARCH_FIELD, timeout=10)
            search_field.clear()
            time.sleep(0.5)
            search_field.send_keys(order_id)
            time.sleep(0.5)
            search_field.send_keys(Keys.ENTER)
            logger.info(f"🔍 Searched for Order ID: {order_id}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Failed to search for order {order_id}: {e}")
            return False

        # --- Step 4️⃣: Select order checkbox ---
        try:
            order_elem = self.wait.wait_for_element_to_be_visible(
                (By.CSS_SELECTOR, f"td[title='{order_id}']"), timeout=20
            )
            if not order_elem:
                logger.error(f"❌ Order '{order_id}' not found in table.")
                return False

            row = order_elem.find_element(By.XPATH, "./ancestor::tr[1]")
            checkbox = row.find_element(By.XPATH, ".//td[1]//input[@type='checkbox']")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)

            if not checkbox.is_selected():
                checkbox.click()
            logger.info("✅ Order checkbox selected.")
        except Exception as e:
            logger.error(f"❌ Failed to select checkbox for order {order_id}: {e}")
            return False

        # --- Step 5️⃣: Click 'Change' button ---
        try:
            change_btn = self.wait.wait_for_element_to_be_clickable((By.ID, "bt_Change"), timeout=10)
            change_btn.click()
            logger.info("✅ Clicked 'Change' button.")
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Failed to click 'Change' button: {e}")
            return False

        # --- Step 6️⃣: Open 'Files' tab ---
        try:
            files_tab = self.wait.wait_for_element_to_be_visible(
                (By.XPATH, "//a[@href='#tab_RecyclingFiles']"), timeout=10
            )
            self.driver.execute_script("arguments[0].click();", files_tab)
            logger.info("✅ Opened 'Files' tab successfully.")
            time.sleep(3)

            # Ensure Files tab actually loaded
            if "RecyclingFiles" not in self.driver.page_source:
                logger.warning("⚠️ Files tab content not loaded properly.")
        except Exception as e:
            logger.error(f"❌ Failed to open 'Files' tab: {e}")
            return False

        # --- Step 7️⃣: Wait for modal to appear ---
        try:
            modal = self.wait.wait_for_element_to_be_visible(
                (By.CSS_SELECTOR, "div.modal-dialog"), timeout=30
            )
            logger.info("✅ Upload modal appeared.")
        except Exception as e:
            logger.error(f"❌ Upload modal did not appear — upload button might have failed: {e}")
            self._capture_debug(order_id)
            return False

        # --- Step 8️⃣: Locate upload input and upload files ---
        try:
            # Expose hidden input if necessary
            self.driver.execute_script("""
                const input = document.querySelector("input[type='file'][name='files[]']");
                if (input) {
                    input.style.display = 'block';
                    input.removeAttribute('hidden');
                    input.classList.remove('d-none');
                }
            """)
            time.sleep(1)

            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][name='files[]']")
            if not file_input:
                logger.error("❌ Upload input not found — check locator or iframe.")
                self._capture_debug(order_id)
                return False

            files_to_upload = get_files_in_directory(upload_dir)
            if not files_to_upload:
                logger.warning(f"⚠️ No files found in directory: {upload_dir}")
                return False

            for file_path in files_to_upload:
                logger.info(f"⬆️ Uploading file: {os.path.basename(file_path)}")
                file_input.send_keys(file_path)
                time.sleep(1.5)

            logger.info("✅ All files uploaded successfully.")
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            self._capture_debug(order_id)
            return False

        # --- Step 9️⃣: Save / Confirm upload ---
        try:
            save_btn = self.wait.wait_for_element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Save') or contains(text(),'Upload')]"),
                timeout=10
            )
            save_btn.click()
            logger.info("💾 Clicked 'Save/Upload' button.")
        except Exception as e:
            logger.warning(f"⚠️ Save/Upload button not found or not clickable: {e}")

        time.sleep(3)
        logger.info(f"✅ Upload completed for Order ID: {order_id}")
        return True

    # --- Helper: capture screenshot + page source for debugging ---
    def _capture_debug(self, order_id: str):
        try:
            create_directory_if_not_exists("screenshots")
            screenshot_path = f"screenshots/upload_debug_{order_id}.png"
            html_path = f"screenshots/upload_debug_{order_id}.html"

            self.driver.save_screenshot(screenshot_path)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)

            logger.info(f"🧩 Debug artifacts saved: {screenshot_path}, {html_path}")
        except Exception as e:
            logger.error(f"❌ Failed to capture debug artifacts: {e}")
