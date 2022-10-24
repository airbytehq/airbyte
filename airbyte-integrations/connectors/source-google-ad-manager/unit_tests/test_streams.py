#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
# @Todo: is the number of stream increase, separate each stream in a different file and do the same for the tests

from source_google_ad_manager.utils import convert_time_to_dict


def test_convert_time_to_dict(test_date):
    """this test the convert time to dict function"""
    assert convert_time_to_dict(test_date) == {
        "year": 2021,
        "month": 10,
        "day": 1,
    }


def test_ad_unit_per_hour_read_report(ad_unit_per_hour_stream):
    "this should test the read report method for the class ad unit per hour"
    assert ad_unit_per_hour_stream.primary_key == ["ad_unit", "hour", "date"]
    records = ad_unit_per_hour_stream.read_records()
    for record in records:
        assert isinstance(record, dict)
        assert list(record.keys()) == ['cpm_cpc_revenue', 'impressions', 'eCpm', 'unfilled_impressions', 'ad_unit', 'hour', 'date', 'customer_name']


def test_ad_unit_per_hour_generate_report_query(ad_unit_per_hour_stream, test_date):
    """this test the generate_report_query for ad unit per hour

    Args:
        patch_base_class (_type_): _description_
    """
    start_date = end_date = convert_time_to_dict(test_date)
    report_query = ad_unit_per_hour_stream.generate_report_query(start_date=start_date, end_date=end_date)
    expected_report_query = {'reportQuery': {'dimensions': ['AD_UNIT_NAME', 'HOUR', 'DATE'],
                                             'columns': ['TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS',
                                                         'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS',
                                                         'TOTAL_LINE_ITEM_LEVEL_CLICKS',
                                                         'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE',
                                                         'TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM',
                                                         'TOTAL_LINE_ITEM_LEVEL_CTR', 'TOTAL_CODE_SERVED_COUNT'],
                                             'adUnitView': 'HIERARCHICAL',
                                             'dateRangeType': 'CUSTOM_DATE',
                                             'startDate': {'year': start_date["year"], 'month': start_date["month"], 'day': start_date["day"]},
                                             'endDate': {'year': end_date["year"], 'month': end_date["month"], 'day': end_date["day"]}}}
    assert report_query == expected_report_query


def test_ad_unit_per_referrer_generate_report_query(ad_unit_per_referrer_stream, test_date):
    """this wil test generate report query for ad unit per referrer.

    Args:
        patch_base_class (_type_): _description_
    """
    # mock this to return a list of values not make api calls
    # get_custom_targeting_values
    start_date = end_date = convert_time_to_dict(test_date)
    targeting_values = ad_unit_per_referrer_stream.get_custom_targeting_values()
    report_query = ad_unit_per_referrer_stream.generate_report_query(targeting_values, start_date=start_date, end_date=end_date)
    assert report_query == {'reportQuery': {'dimensions': ['ADVERTISER_NAME', 'CUSTOM_CRITERIA', 'AD_UNIT_ID', 'DATE'],
                                            'columns': ['TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE', 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS', 'TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM', 'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS', 'TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS', 'TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS'], 
                                            'adUnitView': 'HIERARCHICAL',
                                            'statement': {'query': 'WHERE CUSTOM_TARGETING_VALUE_ID IN (Referrer 1, Referrer 2, Referrer 3)',  'values': None},
                                            'dateRangeType': 'CUSTOM_DATE',
                                            'startDate': {'year': start_date["year"], 'month': start_date["month"], 'day': start_date["day"]},
                                            'endDate': {'year': end_date["year"], 'month': end_date["month"], 'day': end_date["day"]}}}


def test_ad_unit_per_referrer_read_record(ad_unit_per_referrer_stream):
    """
    test ad unit per referrer read record
    """
    "this should test the read report method for the class ad unit per hour"
    assert ad_unit_per_referrer_stream.primary_key == ["ad_unit", "referrer", "date"]
    records = ad_unit_per_referrer_stream.read_records()
    for record in records:
        assert isinstance(record, dict)
        assert list(record.keys()) == ['ad_unit', 'referrer', 'impressions', 'cpm_cpc_revenue', 'eCpm', 'click', 'date']
