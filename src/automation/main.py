from automation.authentication.session_manager import SessionManager
from automation.authentication.login import LoginPage
from automation.workflows.download_reports import DownloadReportsWorkflow
from automation.config.settings import settings
from automation.utilities.logger import logger

def main():
    """Main function to run the automation."""
    session_manager = SessionManager()
    driver = session_manager.start_session()

    if not driver:
        logger.error("Failed to start WebDriver session. Exiting.")
        return

    try:
        # Navigate to the base URL
        driver.get(str(settings.BASE_URL))

        # Perform login
        login_page = LoginPage(driver)
        login_page.login()

        # Run the download workflow
        download_workflow = DownloadReportsWorkflow(driver)
        download_workflow.run()

    except Exception as e:
        logger.error(f"An unexpected error occurred during the automation: {e}")
    finally:
        # End the session
        session_manager.end_session()
        logger.info("Automation script finished.")

if __name__ == "__main__":
    main()