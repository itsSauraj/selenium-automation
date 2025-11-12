from  automation.config import settings
from automation.utilities.logger import logger
from automation.config.locators import ReportMapperKeys

class ExcelMapper:
    """A class to map Excel sheet columns to data fields."""

    ACCOUNT_NAME = "ACCOUNT NAME"
    ORDER_ID = "AUTO NAME"
    REPORT_TYPE = "REPORT TYPE"
    REPORT_NAME = "REPORT NAME"
    PRIORITY = "PRIORITY"

    @classmethod
    def get_all_fields(cls):
        """Returns a list of all data field names."""
        return [
            cls.ACCOUNT_NAME,
            cls.ORDER_ID,
            cls.REPORT_TYPE,
            cls.REPORT_NAME,
            cls.PRIORITY,
        ]

    @classmethod
    def set_custom_field(cls, field_name, custom_name):
        """
          Sets a custom name for a given field.
          Args:
              field_name (str): The name of the field to customize.
              custom_name (str): The custom name to set for the field.
          Raises:
              ValueError: If the field_name does not exist in the class.
        """
        if hasattr(cls, field_name):
            setattr(cls, field_name, custom_name)
        else:
            raise ValueError(f"Field '{field_name}' does not exist in ExcelMapper.")
        
    @classmethod
    def set_multiple_custom_fields(cls, custom_fields):
        """
        Sets multiple custom field names based on a dictionary input.
        
        Args:
            custom_fields (dict): A dictionary where keys are existing field names
                                  and values are the custom names to set.
        """
        for field_name, custom_name in custom_fields.items():
            cls.set_custom_field(field_name, custom_name)

class ReportMapper:
    """A class to map report types to their download methods."""

    mapping = {
        # Settlement Reports
        "Data Erasure Report": ReportMapperKeys.SETTLEMENT_REPORT,
        "Settlement Report": ReportMapperKeys.SETTLEMENT_REPORT,
        "Settlement Report - ALL ASSETS": ReportMapperKeys.SETTLEMENT_REPORT,
        "SUSTAINABILITY REPORT": ReportMapperKeys.SETTLEMENT_REPORT,
        "SUSTAINABILITY REPORT-1": ReportMapperKeys.SETTLEMENT_REPORT,
        "Test - Settlement": ReportMapperKeys.SETTLEMENT_REPORT,
        "Certificate of Recycling": ReportMapperKeys.SETTLEMENT_REPORT,
        "Settlement Report": ReportMapperKeys.SETTLEMENT_REPORT,

        # Transaction History Reports
        "AP Invoice / AR Invoice": ReportMapperKeys.TRANSACTION_HISTORY_REPORT,

        # Audit Orders Reports
        "Audit Report Excel": ReportMapperKeys.AUDIT_ORDERS_PAGE,
        
        # Inbound Page Reports
        "Bill of Lading": ReportMapperKeys.INBOUND_PAGE,
        "Data Destruction Report": ReportMapperKeys.INBOUND_PAGE,
        "Picture Report": ReportMapperKeys.INBOUND_PAGE,
        "Receiving Report": ReportMapperKeys.INBOUND_PAGE,
        "Settlement Summary": ReportMapperKeys.INBOUND_PAGE,
        "Receiving Summary Report": ReportMapperKeys.INBOUND_PAGE,
    }
    mapping = {k.lower(): v for k, v in mapping.items()}

    def group_by_report_type(self, report_type: str):
      grouped = []
      for report_name, mapped_type in self.mapping.items():
          if mapped_type == report_type:
              grouped.append(report_name)
      return grouped


    def get_report_key(self, report_name: str):
      return self.mapping.get(report_name.lower(), None)

report_mapper = ReportMapper()