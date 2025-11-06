from automation.ui.navigation import Navigation
from automation.utilities.excel_reader import get_navigation_steps
from automation.utilities.logger import logger

class UploadReportsWorkflow:
    def __init__(self, driver):
        self.navigation = Navigation(driver)

    def run(self):
        """Runs the upload reports workflow."""
        logger.info("Starting the upload reports workflow.")

        # Get navigation steps from the Excel file
        steps = get_navigation_steps("Upload")  # Assuming a sheet named "Upload"

        if not steps:
            logger.error("No navigation steps found for the upload workflow.")
            return

        # Execute the navigation steps
        self.navigation.execute_navigation(steps)

        logger.info("Upload reports workflow completed.")
