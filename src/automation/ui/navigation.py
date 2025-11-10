from selenium.webdriver.common.by import By
from automation.ui.page_base import PageBase
from automation.utilities.logger import logger

class Navigation(PageBase):
    """
    This class handles the dynamic navigation based on the instructions from the Excel file.
    """

    def __init__(self, driver):
        """
        Initializes the Navigation class.

        Args:
            driver: The Selenium WebDriver instance.
        """
        super().__init__(driver)

    def execute_step(self, step):
        """Executes a single navigation step."""
        action = step.get("Action")
        locator_type = step.get("LocatorType")
        locator_value = step.get("LocatorValue")
        value = step.get("Value")

        if not action:
            logger.warning("Skipping step due to missing action.")
            return

        logger.info(f"Executing action: {action}")

        by_locator = None
        if locator_type and locator_value:
            by_locator = self._get_locator(locator_type, locator_value)

        if action.lower() == "navigate":
            self.driver.get(value)
        elif action.lower() == "click":
            if by_locator:
                self.click(by_locator)
            else:
                logger.error("Cannot perform click action without a locator.")
        elif action.lower() == "send_keys":
            if by_locator and value is not None:
                self.send_keys(by_locator, value)
            else:
                logger.error("Cannot perform send_keys action without a locator and a value.")
        elif action.lower() == "wait":
            # Implement a generic wait if needed, or use implicit/explicit waits.
            pass
        else:
            logger.warning(f"Unsupported action: {action}")

    def execute_navigation(self, steps):
        """Executes a series of navigation steps."""
        for step in steps:
            self.execute_step(step)

    def _get_locator(self, locator_type, locator_value):
        """
        Constructs a locator tuple from the locator type and value.

        Args:
            locator_type (str): The type of the locator (e.g., 'id', 'name', 'xpath').
            locator_value (str): The value of the locator.

        Returns:
            tuple: A locator tuple (e.g., (By.ID, 'username')).
        """
        if locator_type.lower() == 'id':
            return (By.ID, locator_value)
        elif locator_type.lower() == 'name':
            return (By.NAME, locator_value)
        elif locator_type.lower() == 'xpath':
            return (By.XPATH, locator_value)
        elif locator_type.lower() == 'css':
            return (By.CSS_SELECTOR, locator_value)
        elif locator_type.lower() == 'link_text':
            return (By.LINK_TEXT, locator_value)
        elif locator_type.lower() == 'partial_link_text':
            return (By.PARTIAL_LINK_TEXT, locator_value)
        elif locator_type.lower() == 'class_name':
            return (By.CLASS_NAME, locator_value)
        elif locator_type.lower() == 'tag_name':
            return (By.TAG_NAME, locator_value)
        else:
            logger.error(f"Unsupported locator type: {locator_type}")
            return None
