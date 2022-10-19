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
    def from_dict(row_dict):
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
