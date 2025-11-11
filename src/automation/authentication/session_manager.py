import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from automation.config.settings import settings
from automation.utilities.logger import logger

class SessionManager:
    """
    This class manages the WebDriver session, including starting, ending,
    and persisting session data.
    """

    def __init__(self):
        """
        Initializes the SessionManager.
        """
        self.driver = None

    def start_session(self):
        """
        Starts a new WebDriver session with custom Chrome options.
        """
        try:
            logger.info("Starting a new WebDriver session.")
            chrome_options = webdriver.ChromeOptions()
            prefs = {
                # "download.default_directory": settings.DOWNLOAD_PATH,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_setting_values.automatic_downloads": 1,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
            }
            # chrome_options.add_argument("--headless=new")  #only if want to run as headless
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--force-device-scale-factor=0.75")
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.maximize_window()
            self.load_session()
            return self.driver
        except Exception as e:
            logger.error(f"An error occurred while starting the WebDriver session: {e}")
            return None

    def load_session(self):
        """
        Loads session data from the JSON file for the current base URL.
        """
        self.driver.get(str(settings.BASE_URL))
        self.driver.refresh()

    def end_session(self):
        """Saves session data and ends the current WebDriver session."""
        if self.driver:
            logger.info("Ending the WebDriver session.")
            self.driver.quit()
            self.driver = None

    def restart_session(self):
        """Restarts the WebDriver session."""
        self.end_session()
        return self.start_session()