from pydantic import BaseModel
from datetime import datetime


class AdUnitPerHourItem(BaseModel):
    cpm_cpc_revenue: int
    impressions: int
    eCpm: int
    unfilled_impressions: int
    ad_unit: str
    hour: int
    date: datetime  # need to specify the best date with the format

    @staticmethod
    def from_dict(row_dict) -> "AdUnitPerHourItem":
        """this parse one row of item level from the api to a python object

        Args:
            row_dict (dict): the row of the report

        Returns:
            AdUnitPerHourItem: the python object
        """
        return AdUnitPerHourItem(
            cpm_cpc_revenue=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE']),
            impressions=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS']),
            eCpm=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM']),
            unfilled_impressions=int(row_dict['Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS']),
            ad_unit=row_dict['Ad unit 1'],
            hour=int(row_dict['Dimension.HOUR']),
            date=datetime.strptime(row_dict['Dimension.DATE'], '%Y-%m-%d')
        )


class AdUnitPerReferrerItem(BaseModel):
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
            ad_unit=row_dict['Ad unit 1'],
            referrer=row_dict['Dimension.CUSTOM_CRITERIA'].replace("referrer=", ""),
            impressions=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS']),
            cpm_cpc_revenue=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE']),
            eCpm=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM']),
            click=int(row_dict['Column.TOTAL_LINE_ITEM_LEVEL_CLICKS']),
            date=datetime.strptime(row_dict['Dimension.DATE'], '%Y-%m-%d')
        )
