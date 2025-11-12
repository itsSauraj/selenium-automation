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

def check_if_folder_exists(folder_path):
    """Checks if a folder exists at the given path."""
    exists = os.path.exists(folder_path) and os.path.isdir(folder_path)
    logger.info(f"Folder exists at {folder_path}: {exists}")
    return exists

def remove_directory(directory_path):
    """Removes a directory and all its contents."""
    try:
        shutil.rmtree(directory_path)
        logger.info(f"Removed directory: {directory_path}")
    except FileNotFoundError:
        logger.error(f"Directory not found at path: {directory_path}")
    except Exception as e:
        logger.error(f"An error occurred while removing the directory: {e}")