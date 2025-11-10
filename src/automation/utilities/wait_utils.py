import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from automation.utilities.logger import logger

class WaitUtils:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def wait_for_element_to_be_visible(self, by_locator, timeout=None):
        """Waits for an element to be visible on the page."""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not visible within {timeout} seconds.")
            return None

    def wait_for_element_to_be_clickable(self, by_locator, timeout=None):
        """Waits for an element to be clickable on the page."""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not clickable within {timeout} seconds.")
            return None

    def wait_for_presence_of_element_located(self, by_locator, timeout=None):
        """Waits for an element to be present in the DOM."""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not present within {timeout} seconds.")
            return None
        
    def wait_for_title_contains(self, title_substring, timeout=None):
        """Waits for the page title to contain a specific substring."""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.title_contains(title_substring)
            )
        except TimeoutException:
            logger.error(f"Page title did not contain '{title_substring}' within {timeout} seconds.")
            return False

    def wait_for_page_load(self, timeout=None):
        """
        Wait until document.readyState == 'complete'.
        Equivalent to waiting for the page to fully load.
        """
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info("Page load complete.")
        except TimeoutException:
            logger.warning("Page did not fully load within the expected timeout.")

    def wait_for_ajax(self, timeout=None):
        """
        Wait until all jQuery AJAX requests are complete.
        Safe even if jQuery is not present.
        """
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return (typeof jQuery === 'undefined') || (jQuery.active === 0);"
                )
            )
            logger.debug("All AJAX requests completed.")
        except TimeoutException:
            logger.warning("AJAX requests did not finish in time (or jQuery not found).")

    def wait_for_download_to_complete(self, download_dir, timeout=60):
        """
        Waits for all Chrome `.crdownload` files to finish downloading in the given directory.
        Returns True when all downloads are done, False if timeout.
        """
        logger.info(f"Waiting for downloads to complete in: {download_dir}")
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                tmp_files = [
                    f for f in os.listdir(download_dir)
                    if f.endswith(".crdownload") or f.endswith(".tmp")
                ]
                if not tmp_files:
                    logger.info("All downloads completed successfully.")
                    return True
            except FileNotFoundError:
                logger.error(f"Download folder not found: {download_dir}")
                return False

            time.sleep(1)

        logger.warning("Download did not complete within timeout.")
        return False
