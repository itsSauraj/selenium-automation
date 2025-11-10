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
        self.RETRIES = 3
        self.ATTEMPT = 0

    def login(self):
        """Performs the login action by entering credentials and pressing ENTER."""
        hard_reload(self.driver)
        time.sleep(2)
        self.ATTEMPT += 1
        
        # Check if already logged in by checking page title
        if "Qualify" in self.get_page_title():
            logger.info("Already logged in. Skipping login process.")
            return

        logger.info("Attempting to log in.")
        self.send_keys(LoginPageLocators.USERNAME_FIELD, settings.USER_EMAIL)
        
        # Find the password field to send ENTER key
        password_element = self.wait.wait_for_element_to_be_visible(LoginPageLocators.PASSWORD_FIELD)
        if password_element:
            password_element.send_keys(settings.USER_PASSWORD)
            password_element.send_keys(Keys.ENTER)
            logger.info("Successfully submitted login form.")
            self.wait.wait_for_title_contains("Qualify", timeout=15)  # Wait for dashboard to load after login
            dashboard_title = self.get_page_title().strip().split(' ')
            if "Qualify" in dashboard_title:
                logger.info("Login successful, dashboard page loaded.: %s", dashboard_title)
            else:
                if self.ATTEMPT < self.RETRIES:
                    logger.warning("Login failed, retrying... Attempt %d of %d", self.ATTEMPT, self.RETRIES)
                    self.login()
                else:
                    logger.error("Login failed or dashboard page did not load.")
                    self.driver.save_screenshot("screenshots/login_failed.png")
                self.login()
        else:
            logger.error("Password field not found. Cannot complete login.")

def hard_reload(driver):
    """Performs a hard reload by clearing cache, cookies, and storage."""
    driver.execute_cdp_cmd("Network.clearBrowserCache", {})
    driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    driver.execute_cdp_cmd("Page.reload", {"ignoreCache": True})
