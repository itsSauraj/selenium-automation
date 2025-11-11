import os

from urllib.parse import urljoin

from pydantic_settings import BaseSettings
from pydantic import HttpUrl
from typing import Optional

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class Settings(BaseSettings):
    """Configuration settings for the automation framework."""
    # Environment variables
    BASE_URL: HttpUrl
    USER_EMAIL: str
    USER_PASSWORD: str

    # File paths
    DOWNLOAD_PATH: str = os.path.join(PROJECT_ROOT, "downloads")
    UPLOAD_PATH: str = os.path.join(PROJECT_ROOT, "uploads")
    LOG_FILE_PATH: str = os.path.join(PROJECT_ROOT, "logs/run.log")
    EXCEL_FILE_PATH: str = os.path.join(PROJECT_ROOT, "data/navigation.xlsx")
    SESSION_STORAGE_PATH: str = os.path.join(PROJECT_ROOT, "browser/state.json")

    class Config:
        env_file = os.path.join(PROJECT_ROOT, ".env")
        env_file_encoding = "utf-8"

    def set(self, key: str, value):
        """Update any setting dynamically at runtime.
        Args:
            key (str): The setting key to update.
            value: The new value for the setting.
        Raises:
            AttributeError: If the key does not correspond to any setting.
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"Invalid setting key: '{key}'")
        
    def make_url(self, route: str) -> str:
        """
        Safely join BASE_URL with a route path.

        Example:
        make_url("/Admin/RecyclingOrders.aspx")
        -> "https://example.com/Admin/RecyclingOrders.aspx"
        """
        return urljoin(str(self.BASE_URL), route)
    
    def join_url(self, base: str, query: str) -> str:
        """
        Safely join 2 urls with query params
        
        Example:
        join_url("https://example.com/route.aspx", "?orderId=00000")
        -> "https://example.com/route.aspx?orderId=00000"
        """
        return urljoin(str(base), str(query))

"""Create a singleton settings instance to be used across the framework."""
settings = Settings()