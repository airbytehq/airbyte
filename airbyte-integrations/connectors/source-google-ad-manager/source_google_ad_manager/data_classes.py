from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class CustomBaseModel(BaseModel):
    @staticmethod
    def convert_to_int_or_return_zero(value):
        """convert the value to int or return zero

        Args:
            value (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 0
        return value


class AdUnitPerHourItem(CustomBaseModel):
    cpm_cpc_revenue: int
    impressions: int
    eCpm: int
    unfilled_impressions: int
    ad_unit: str
    hour: int
    date: datetime  # need to specify the best date with the format
    customer_name: str

    @staticmethod
    def from_dict(row_dict) -> "AdUnitPerHourItem":
        """this parse one row of item level from the api to a python object

        Args:
            row_dict (dict): the row of the report

        Returns:
            AdUnitPerHourItem: the python object
        """
        return AdUnitPerHourItem(
            cpm_cpc_revenue=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE')),
            impressions=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')),
            eCpm=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM')),
            unfilled_impressions=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS')),
            ad_unit=row_dict.get('Ad unit 1'),
            hour=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Dimension.HOUR')),
            date=datetime.strptime(row_dict.get('Dimension.DATE'), '%Y-%m-%d'),
            customer_name=row_dict.get('customer_name')
        )


class AdUnitPerReferrerItem(CustomBaseModel):
    ad_unit: str  # should be part of the index
    referrer: str  # should be part of the index
    impressions: int
    cpm_cpc_revenue: int
    eCpm: int
    click: int
    date: datetime  # need to specify the best date with the format # should be part of the index

    @staticmethod
    def from_dict(row_dict) -> "AdUnitPerReferrerItem":
        """this parse one row of item level from the api to a python object

        Args:
            row_dict (dict): the row of the report

        Returns:
            AdUnitPerReferrerItem: the python object
        """
        return AdUnitPerReferrerItem(
            ad_unit=row_dict.get('Ad unit 1'),
            referrer=row_dict.get('Dimension.CUSTOM_CRITERIA').replace("referrer=", ""),
            impressions=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')),
            cpm_cpc_revenue=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE')),
            eCpm=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM')),
            click=AdUnitPerHourItem.convert_to_int_or_return_zero(row_dict.get('Column.TOTAL_LINE_ITEM_LEVEL_CLICKS')),
            date=datetime.strptime(row_dict.get('Dimension.DATE'), '%Y-%m-%d'),
            customer_name=row_dict.get('customer_name')
        )


class ReportStatus(Enum):
    """Handle report status from the google ad manager api

    Args:
        Enum (_type_): _description_
    """
    COMPLETED = "COMPLETED"
    DONE = "DONE"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
