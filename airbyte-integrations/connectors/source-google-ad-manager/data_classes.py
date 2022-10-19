from dataclasses import dataclass


{'Ad unit 1': 'amp-outsider', 
 'Ad unit 2': 'N/A', 
 'Dimension.HOUR': '5', 
 'Dimension.DATE': '2022-10-19', 
 'Ad unit ID 1': '22063950859', 
 'Ad unit ID 2': '-', 
 'Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS': '35', 
 'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': '45150', 
 'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': '399', 
 'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': '108779759', 
 'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': '2409297', 
 'Column.TOTAL_LINE_ITEM_LEVEL_CTR': '0.0088', 
 'Column.TOTAL_CODE_SERVED_COUNT': '65913'}

@dataclass
class AdUnitPerHourItem:
    cpm_cpc_revenue: int
    impressions: int
    eCpm: int
    unfilled_impressions: int
    ad_unit: int
    hour: int
    date: str # need to specify the best date with the format


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
        date=str(row_dict['Dimension.DATE'])
    )
