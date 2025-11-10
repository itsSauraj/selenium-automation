import os
from automation.authentication.session_manager import SessionManager
from automation.authentication.login import LoginPage
from automation.workflows.download_reports import DownloadReportsWorkflow
from automation.config.settings import settings
from automation.utilities.logger import logger

""" FOR DEBUGGING PURPOSES ONLY """
from automation.utilities.file_manager import create_directory_if_not_exists

def main():
    """Main function to run the automation."""
    # Remove old state file to ensure a fresh start
    if os.path.exists(settings.SESSION_STORAGE_PATH):
        os.remove(settings.SESSION_STORAGE_PATH)
        logger.info(f"Removed old session file: {settings.SESSION_STORAGE_PATH}")

    session_manager = SessionManager()
    driver = session_manager.start_session()

    if not driver:
        logger.error("Failed to start WebDriver session. Exiting.")
        return

    try:
        LOGGED_IN = False
        # Perform login
        while not LOGGED_IN:
            login_page = LoginPage(driver)
            login_page.login()
            if login_page.ATTEMPT >= login_page.RETRIES:
                logger.error("Maximum login attempts reached. Exiting.")
                session_manager.restart_session()
                driver = session_manager.start_session()
            else:
                LOGGED_IN = True

        # Run the download workflow
        download_workflow = DownloadReportsWorkflow(driver)
        download_workflow.run()

    except Exception as e:
        logger.error(f"An unexpected error occurred during the automation: {e}")

    except KeyboardInterrupt:
        create_directory_if_not_exists("screenshots")
        driver.save_screenshot("screenshots/final_state.png")
        session_manager.end_session()
        logger.info("Automation interrupted by user.")
    finally:
        # End the session
        create_directory_if_not_exists("screenshots")
        driver.save_screenshot("screenshots/final_state.png")
        session_manager.end_session()
        logger.info("Automation script finished.")

if __name__ == "__main__":
    main()