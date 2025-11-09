from selenium.webdriver.common.by import By

class LoginPageLocators:
    """
    A class for login page locators. All login page locators should be defined here.
    """
    USERNAME_FIELD = (By.NAME, "email")
    PASSWORD_FIELD = (By.NAME, "password")

class DashboardPageLocators:
    """
    A class for dashboard page locators. All dashboard page locators should be defined here.
    """
    DASHBOARD_TITLE = (By.TAG_NAME, "title")