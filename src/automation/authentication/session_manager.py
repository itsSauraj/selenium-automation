from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from automation.config.settings import DOWNLOAD_PATH
from automation.utilities.logger import logger

class SessionManager:
    """
    This class manages the WebDriver session, including starting and ending the session.
    """

    def __init__(self):
        """
        Initializes the SessionManager.
        """
        self.driver = None

    def start_session(self):
        """
        Starts a new WebDriver session with custom Chrome options.

        This method configures Chrome to:
        - Download files to the specified DOWNLOAD_PATH without prompting the user.
        - Allow multiple file downloads automatically.
        """
        try:
            logger.info("Starting a new WebDriver session.")

            # Configure Chrome options
            chrome_options = webdriver.ChromeOptions()
            prefs = {
                "download.default_directory": DOWNLOAD_PATH,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Use webdriver-manager to automatically download and manage the chromedriver
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.maximize_window()
            return self.driver
        except Exception as e:
            logger.error(f"An error occurred while starting the WebDriver session: {e}")
            return None

    def end_session(self):
        """Ends the current WebDriver session."""
        if self.driver:
            logger.info("Ending the WebDriver session.")
            self.driver.quit()
            self.driver = None