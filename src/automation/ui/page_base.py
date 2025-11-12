from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from automation.utilities.logger import logger
import time
from automation.utilities.wait_utils import WaitUtils
from automation.utilities.action_utils import Actions
from selenium.webdriver.common.keys import Keys

class PageBase:
    """
    This class serves as the base for all page objects.
    It contains common methods that can be used across all pages.
    """

    def __init__(self, driver):
        """
        Initializes the PageBase.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WaitUtils(driver)
        self.actions = Actions(driver)

    def click(self, by_locator):
        """
        Clicks on an element after waiting for it to be clickable.

        Args:
            by_locator: The locator of the element to be clicked.
        """
        element = self.wait.wait_for_element_to_be_clickable(by_locator)
        if element:
            element.click()

    def send_keys(self, by_locator, text):
        """
        Sends keys to an element after waiting for it to be visible.

        Args:
            by_locator: The locator of the element.
            text: The text to be sent.
        """
        element = self.wait.wait_for_element_to_be_visible(by_locator)
        if element:
            element.send_keys(text)

    def get_text(self, by_locator):
        """
        Gets the text of an element after waiting for it to be visible.

        Args:
            by_locator: The locator of the element.

        Returns:
            str: The text of the element, or None if the element is not found.
        """
        element = self.wait.wait_for_element_to_be_visible(by_locator)
        if element:
            return element.text
        return None
    
    def get_page_title(self):
        """
        Gets the title of the current page.

        Returns:
            str: The title of the current page.
        """
        return self.driver.title
    
    def safe_click(self, locator, timeout=15, scroll=True):
        """
        Wait until clickable, try click; on intercept hide overlays and retry once.
        locator: tuple (By.*, value)
        """
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            if scroll:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            try:
                el.click()
                return el
            except ElementClickInterceptedException:
                logger.warning("Click intercepted, attempting to clear overlays and retry.")
                self.close_known_overlays()
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click()
                return el
        except TimeoutException:
            logger.error(f"Element not clickable: {locator}")
            return None

    def close_known_overlays(self):
        """Hide known blocking overlays/popups used by the app."""
        self.driver.execute_script("""
            const selectors = [
                '.recycling-orders-popup-inner',
                '#gritter-notice-wrapper',
                '.ui-widget-overlay',
                '.modal-backdrop'   // add any other overlay selectors here
            ];
            selectors.forEach(s => {
                document.querySelectorAll(s).forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                });
            });
        """)

    def clear_input(self, element_or_locator, timeout=5):
        """Robustly clear an input or contenteditable element.

        Accepts either a Selenium WebElement or a locator tuple (By, value).
        Strategy:
        - If locator provided, wait for visibility.
        - Try element.clear()
        - If value remains, use JS to set value/innerText to '' and dispatch input/change
        - Fallback to sending CTRL+A + BACKSPACE
        Returns True if element is empty after attempts, False otherwise.
        """
        from selenium.webdriver.remote.webelement import WebElement
        el = None
        try:
            if isinstance(element_or_locator, tuple):
                el = self.wait.wait_for_element_to_be_visible(element_or_locator, timeout=timeout)
            elif isinstance(element_or_locator, WebElement):
                el = element_or_locator
            else:
                logger.warning("clear_input received unsupported type: %s", type(element_or_locator))
                return False

            if not el:
                return False

            # Try native clear first
            try:
                el.clear()
            except Exception:
                # ignore and continue to JS fallback
                pass

            time.sleep(0.05)

            # Check current content (value or innerText)
            remaining = self.driver.execute_script(
                "return arguments[0].value !== undefined ? arguments[0].value : (arguments[0].innerText || '');",
                el,
            )

            if remaining:
                # JS: clear and dispatch events so frameworks (React/Vue) pick it up
                try:
                    self.driver.execute_script(
                        """
                        const el = arguments[0];
                        if (el.value !== undefined) {
                            el.value = '';
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        } else {
                            el.innerText = '';
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                        """,
                        el,
                    )
                except Exception:
                    logger.debug("JS clear failed, will try keyboard fallback.")

            # verify again
            time.sleep(0.05)
            remaining = self.driver.execute_script(
                "return arguments[0].value !== undefined ? arguments[0].value : (arguments[0].innerText || '');",
                el,
            )

            if remaining:
                # keyboard fallback: Ctrl+A + Backspace
                try:
                    el.send_keys(Keys.CONTROL, 'a')
                    el.send_keys(Keys.BACKSPACE)
                except Exception:
                    # some elements may not accept keys - ignore
                    pass

            # final check
            remaining = self.driver.execute_script(
                "return arguments[0].value !== undefined ? arguments[0].value : (arguments[0].innerText || '');",
                el,
            )

            return not bool(remaining)
        except Exception as e:
            logger.warning(f"clear_input failed: {e}")
            return False