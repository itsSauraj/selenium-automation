from selenium.webdriver.common.by import By
from automation.utilities.wait_utils import WaitUtils

class PageBase:
    """
    This class serves as the base for all page objects.
    It contains common methods that can be used across all pages.
    """

    def __init__(self, driver):
        """
        Initializes the PageBase.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WaitUtils(driver)

    def click(self, by_locator):
        """
        Clicks on an element after waiting for it to be clickable.

        Args:
            by_locator: The locator of the element to be clicked.
        """
        element = self.wait.wait_for_element_to_be_clickable(by_locator)
        if element:
            element.click()

    def send_keys(self, by_locator, text):
        """
        Sends keys to an element after waiting for it to be visible.

        Args:
            by_locator: The locator of the element.
            text: The text to be sent.
        """
        element = self.wait.wait_for_element_to_be_visible(by_locator)
        if element:
            element.send_keys(text)

    def get_text(self, by_locator):
        """
        Gets the text of an element after waiting for it to be visible.

        Args:
            by_locator: The locator of the element.

        Returns:
            str: The text of the element, or None if the element is not found.
        """
        element = self.wait.wait_for_element_to_be_visible(by_locator)
        if element:
            return element.text
        return None
    
    def get_page_title(self):
        """
        Gets the title of the current page.

        Returns:
            str: The title of the current page.
        """
        return self.driver.title