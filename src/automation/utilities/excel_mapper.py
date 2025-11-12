from  automation.config.settings import settings

class ReportPageMapperKeys:
    """A class to map report types to their download methods."""    
    INBOUND = "INBOUND"
    SETTLEMENT = "SETTLEMENT"
    INVOICE = "INVOICE"
    AUDIT = "AUDIT"

    # Mapping of report types to their respective page URLs
    PAGE_MAP = {
        INBOUND: settings.make_url("/Admin/RecyclingOrders.aspx"),
        SETTLEMENT : settings.make_url("/Admin/SettlementList.aspx"),
        INVOICE: settings.make_url("/Admin/SettlementList.aspx"),
        AUDIT: settings.make_url("/Admin/Recycling/AuditOrders.aspx"),
    }

    @classmethod
    def get_all_keys(cls):
        """Returns all report mapper keys as a list."""
        return [
            cls.INBOUND,
            cls.SETTLEMENT,
            cls.INVOICE,
            cls.AUDIT,
        ]

    @classmethod
    def get_page_url(cls, key):
        """Returns the URL mapped to the given key."""
        return cls.PAGE_MAP.get(key, None)
    
    @classmethod
    def get_key(cls, page: str):
        """Returns the key mapped to the given page URL."""
        for key, _ in cls.PAGE_MAP.items():
            if key == page:
                return key

report_mapper = ReportPageMapperKeys()

class ExcelMapper:
    """A class to map Excel sheet columns to data fields."""

    ACCOUNT_NAME = "ACCOUNT NAME"
    ORDER_ID = "AUTO NAME"
    REPORT_TYPE = "REPORT TYPE"
    REPORT_NAME = "REPORT NAME"
    PRIORITY = "PRIORITY"
    PAGE = "PAGE"

    @classmethod
    def get_all_fields(cls):
        """Returns a list of all data field names."""
        return [
            cls.ACCOUNT_NAME,
            cls.ORDER_ID,
            cls.REPORT_TYPE,
            cls.REPORT_NAME,
            cls.PRIORITY,
            cls.PAGE,
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