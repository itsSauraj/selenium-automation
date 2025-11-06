import os
import shutil
from automation.utilities.logger import logger

def create_directory_if_not_exists(directory_path):
    """Creates a directory if it does not already exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")

def move_file(source_path, destination_path):
    """Moves a file from the source path to the destination path."""
    try:
        shutil.move(source_path, destination_path)
        logger.info(f"Moved file from {source_path} to {destination_path}")
    except FileNotFoundError:
        logger.error(f"File not found at source path: {source_path}")
    except Exception as e:
        logger.error(f"An error occurred while moving the file: {e}")
