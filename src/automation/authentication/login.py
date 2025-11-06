from selenium.webdriver.common.keys import Keys
from automation.ui.page_base import PageBase
from automation.config.settings import USERNAME, PASSWORD
from automation.config.locators import LoginPageLocators
from automation.utilities.logger import logger

class LoginPage(PageBase):
    """
    This class represents the login page and contains methods to interact with it.
    """

    def __init__(self, driver):
        """
        Initializes the LoginPage.

        Args:
            driver: The Selenium WebDriver instance.
        """
        super().__init__(driver)

    def login(self):
        """Performs the login action by entering credentials and pressing ENTER."""
        logger.info("Attempting to log in.")
        self.send_keys(LoginPageLocators.USERNAME_FIELD, USERNAME)
        
        # Find the password field to send ENTER key
        password_element = self.wait.wait_for_element_to_be_visible(LoginPageLocators.PASSWORD_FIELD)
        if password_element:
            password_element.send_keys(PASSWORD)
            password_element.send_keys(Keys.ENTER)
            logger.info("Entered password and pressed ENTER.")
        else:
            logger.error("Password field not found. Cannot complete login.")

        logger.info("Login action initiated.")

        # Add verification for successful login, e.g., check for a dashboard element
        # For now, we assume login is successful after initiating the action.