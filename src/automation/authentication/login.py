from selenium.webdriver.common.keys import Keys
from automation.ui.page_base import PageBase
from automation.config.settings import settings
from automation.config.locators import LoginPageLocators, DashboardPageLocators
from automation.utilities.logger import logger

import time

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
        self.send_keys(LoginPageLocators.USERNAME_FIELD, settings.USER_EMAIL)
        
        # Find the password field to send ENTER key
        password_element = self.wait.wait_for_element_to_be_visible(LoginPageLocators.PASSWORD_FIELD)
        if password_element:
            password_element.send_keys(settings.USER_PASSWORD)
            password_element.send_keys(Keys.ENTER)
            logger.info("Successfully submitted login form.")
            self.wait.wait_for_title_contains("Qualify", timeout=15)  # Wait for dashboard to load after login
            dashboard_title = self.get_page_title()
            if dashboard_title:
                logger.info("Login successful, dashboard page loaded.: %s", dashboard_title)
            else:
                logger.error("Login failed or dashboard page did not load.")
        else:
            logger.error("Password field not found. Cannot complete login.")
