from selenium.webdriver import ActionChains

class Actions:
    
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.actions = ActionChains(driver)
    
    def double_click(self, element):
        self.actions.double_click(element).perform()