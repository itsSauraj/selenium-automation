class ExcelMapper:
    """A class to map Excel sheet columns to data fields."""

    ORDER_ID = "AUTO_NAME"
    REPORT_TYPE = "REPORT TYPE"
    REPORT_NAME = "REPORT NAME"
    PRIORITY = "PRIORITY"

    @classmethod
    def get_all_fields(cls):
        """Returns a list of all data field names."""
        return [
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


class ReportMapperKeys:
    """A class to map report types to their download methods."""

    SETTLEMENT_REPORT = "Settlement Page"
    TRANSACTION_HISTORY_REPORT = "Through Settlement Page under Transaction History"
    INBOUND_PAGE = "Inbound Order Page"
    AUDIT_ORDERS_PAGE = "Audit Orders Page"