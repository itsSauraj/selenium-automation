from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from automation.utilities.logger import logger

class WaitUtils:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def wait_for_element_to_be_visible(self, by_locator):
        """Waits for an element to be visible on the page."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not visible within {self.timeout} seconds.")
            return None

    def wait_for_element_to_be_clickable(self, by_locator):
        """Waits for an element to be clickable on the page."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not clickable within {self.timeout} seconds.")
            return None

    def wait_for_presence_of_element_located(self, by_locator):
        """Waits for an element to be present in the DOM."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(by_locator)
            )
        except TimeoutException:
            logger.error(f"Element with locator {by_locator} was not present within {self.timeout} seconds.")
            return None
