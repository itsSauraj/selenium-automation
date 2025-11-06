import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Environment variables
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# File paths
DOWNLOAD_PATH = os.path.join(PROJECT_ROOT, os.getenv("DOWNLOAD_PATH", "downloads"))
UPLOAD_PATH = os.path.join(PROJECT_ROOT, os.getenv("UPLOAD_PATH", "uploads"))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, os.getenv("LOG_FILE_PATH", "logs/run.log"))
EXCEL_FILE_PATH = os.path.join(PROJECT_ROOT, os.getenv("EXCEL_FILE_PATH", "data/navigation.xlsx"))
