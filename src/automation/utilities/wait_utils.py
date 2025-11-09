from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from automation.utilities.logger import logger

class WaitUtils:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def wait_for_element_to_be_visible(self, by_locator, timeout=None):
        """Waits for an element to be visible on the page."""
        timeout = timeout if timeout else self.timeout

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not visible within {timeout} seconds.")
            return None

    def wait_for_element_to_be_clickable(self, by_locator, timeout=None):
        """Waits for an element to be clickable on the page."""
        timeout = timeout if timeout else self.timeout

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not clickable within {timeout} seconds.")
            return None

    def wait_for_presence_of_element_located(self, by_locator, timeout=None):
        """Waits for an element to be present in the DOM."""
        timeout = timeout if timeout else self.timeout

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not present within {timeout} seconds.")
            return None
        
    def wait_for_title_contains(self, title_substring, timeout=None):
        """Waits for the page title to contain a specific substring."""
        timeout = timeout if timeout else self.timeout

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.title_contains(title_substring)
            )
        except TimeoutException:
            logger.error(f"Page title did not contain '{title_substring}' within {timeout} seconds.")
            return False
