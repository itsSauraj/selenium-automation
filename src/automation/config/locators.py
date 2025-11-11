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

class ReportMapperKeys:
    """A class to map report types to their download methods."""
    INBOUND_PAGE = "InboundPageSettlementsLocators"
    SETTLEMENT_REPORT = "SettlementReportLocator"
    TRANSACTION_HISTORY_REPORT = "TransactionHistoryReportLocator"
    AUDIT_ORDERS_PAGE = "AuditOrdersPageLocator"


    PAGE_MAP = {
        INBOUND_PAGE: settings.make_url("/Admin/RecyclingOrders.aspx"),
        SETTLEMENT_REPORT: settings.make_url("/Admin/SettlementReport.aspx"),
        TRANSACTION_HISTORY_REPORT: settings.make_url("/Admin/SettlementList.aspx"),
        AUDIT_ORDERS_PAGE: settings.make_url("/Admin/AuditOrders.aspx"),
    }

    @classmethod
    def get_all_keys(cls):
        """Returns all report mapper keys as a list."""
        return [
            cls.INBOUND_PAGE,
            cls.SETTLEMENT_REPORT,
            cls.TRANSACTION_HISTORY_REPORT,
            cls.AUDIT_ORDERS_PAGE,
        ]

    @classmethod
    def get_page_url(cls, key):
        """Returns the URL mapped to the given key."""
        return cls.PAGE_MAP.get(key, None)

report_mapper_locator = ReportMapperKeys()

class InboundPageLocators:
    """
    A class for Inbound Page locators. All locators for this page should be defined here.
    """
    SETTLEMENTS_TAB = (By.ID, "tab_SettlementComplete")
    SEARCH_FIELD = (By.ID, "tb_RecyclingOrderListSearch")

    TABLE_ID = (By.ID, "g_RecyclingOrderList")

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
    SEARCH_FILED = (By.ID, "ag-input-id-60")
    
    CELL_LOCATION = (By.CSS_SELECTOR, "(//*[@col-id='RecyclingOrderAutoName'])[last()]")