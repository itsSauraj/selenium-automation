from selenium.webdriver.common.by import By
from automation.config.settings import settings

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
    
class InboundPageLocators:
    """
    A class for Inbound Page locators. All locators for this page should be defined here.
    """
    SETTLEMENTS_TAB = (By.ID, "tab_SettlementComplete")
    SEARCH_FIELD = (By.ID, "tb_RecyclingOrderListSearch")
    SEARCH_FIELD_SETTLEMENTS = (By.ID, "div_PrintDialog")

    ORDER_CHECKBOX = (By.XPATH, "//table[@id='g_RecyclingOrderList']//tr[2]/td[1]//input[@type='checkbox']")

    STANDARD_DOWNLOAD_BUTTON = (By.XPATH, "//button[normalize-space(text())='Print/Download']")
    DOWNLOAD_BUTTON_NEW = (By.XPATH, "//button[normalize-space(text())='Print/Download New']")

    REPORTS_LIST_CONTAINER = (By.ID, "div_ReportsContainer")

    FILTER_DROPDOWN = (By.XPATH, "//select[@id='filter']")
    
    
class TransactionalPageLoaders:
    """
        A class for Inbound Page locators. All locators for this page should be defined here.
    """
    SEARCH_FIELD = (By.ID, "tb_Search_All")
    
    SALES_ORDER_HISTORY = (By.ID, "a_RecyclingOrder_LinkedSalesOrder")
    INVOICE_TAB = (By.ID, "tab_Invoice")
    
    # INVOICE_TAB_TABLE = (By.ID, "jqg_SalesOrderReceive_Invoices")
    INVOICE_TAB_TABLE_CHECKBOX = (By.XPATH, "//table[@id='jqg_SalesOrderReceive_Invoices']//tr[2]/td[1]//input[@type='checkbox']")
    
    STANDARD_DOWNLOAD_BUTTON = (By.ID, "bt_PrintDownloadInvoicePdf")
    DOWNLOAD_BUTTON_NEW = (By.ID, "bt_OpenReportPrintDialog")
    
    AR_REPORT_CHECKBOX = (By.ID, "cb_Doc_AR_Invoice")
    
class AuditReportsMapper:
    SEARCH_FIELD = (By.XPATH, "//*[@aria-label='Order # Filter Input']")
    
    CELL_LOCATION = (By.XPATH, "(//*[@col-id='RecyclingOrderAutoName'])[last()]")

    PRINT_BUTTON = (By.ID, "bt_PrintDownload")
    
    # CHECKBOX_LOCATOR
    CHECKBOX_AUDIT_REPORT = (By.ID, "cb_Doc_Audit_Report_Excel")
    CHECBOX_INCLUDE_DRIVES = (By.ID, "includeHardDrives")

class SettlementReportLocators:
    """
    A class for Settlement Report locators. All locators for this page should be defined here.
    """
    SEARCH_FIELD = (By.ID, "tb_Search_All")
    
    STANDARD_DOWNLOAD_BUTTON = (By.XPATH, "//button[normalize-space(text())='Print/Download']")
    DOWNLOAD_BUTTON_NEW = (By.XPATH, "//button[normalize-space(text())='Print/Download New']")

    REPORTS_LIST_CONTAINER = (By.ID, "div_ReportsContainer")

    # TYPE => NEW
    # Search here...
    MODAL_ID = "div_PrintDialogSettlementNew"
    SEARCH_FIELD_NEW = (By.XPATH, "//input[@placeholder='Search here...']")
