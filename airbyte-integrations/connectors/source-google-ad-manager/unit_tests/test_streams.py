#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from http import HTTPStatus
from tracemalloc import start
from unittest.mock import MagicMock
from source_google_ad_manager.utils import convert_time_to_dict
import pytest
from source_google_ad_manager.streams import AdUnitPerHourReportStream, BaseGoogleAdManagerReportStream, AdUnitPerReferrerReportStream
from io import BytesIO
# todo : fixtures should go to the conftest.py file

@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(BaseGoogleAdManagerReportStream, "run_report", MagicMock(return_value="fake_id"))
    mocker.patch.object(BaseGoogleAdManagerReportStream, "__abstractmethods__", set())
    BaseGoogleAdManagerReportStream.google_ad_manager_client = MagicMock()
    BaseGoogleAdManagerReportStream.report_downloader = MagicMock()


@pytest.fixture(name="ad_unit_per_hour_stream")
def generate_ad_unit_per_hour_stream(patch_base_class, test_date, mocker):
    start_date = end_date = convert_time_to_dict(test_date)
    google_ad_manager_client = MagicMock()
    fake_ad_unit_per_hour_response = BytesIO(b"""\
Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS,Ad unit 1,Dimension.HOUR,Dimension.DATE
0,0,0,1,0,Ad unit 1,0,2021-10-01
1,1,0,1,0,Ad unit 1,1,2021-10-01
1,1,0,1,0,Ad unit 1,2,2021-10-01""")
    mocker.patch.object(AdUnitPerHourReportStream, "download_report", MagicMock(return_value=fake_ad_unit_per_hour_response))
    ad_unit_per_hour_stream = AdUnitPerHourReportStream(google_ad_manager_client=google_ad_manager_client,
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        customer_name="test_customer_name")
    yield ad_unit_per_hour_stream


@pytest.fixture(name="test_date")
def generate_test_date():
    return datetime(2021, 10, 1)


@pytest.fixture(name="ad_unit_per_referrer_stream")
def generate_ad_unit_per_referrer_stream(patch_base_class, test_date, mocker):
    start_date = end_date = convert_time_to_dict(test_date)
    google_ad_manager_client = MagicMock()
    fake_ad_unit_per_referrer_response = BytesIO(b"""\
Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS,Ad unit 1,Dimension.CUSTOM_CRITERIA,Dimension.DATE,Column.TOTAL_LINE_ITEM_LEVEL_CLICKS
0,0,0,1,0,Ad unit 1,Referrer 1,2021-10-01,1
1,1,0,1,0,Ad unit 1,Referrer 2,2021-10-01,1
1,1,0,1,0,Ad unit 1,Referrer 3,2021-10-01,1""")
    mocker.patch.object(AdUnitPerReferrerReportStream, "download_report", MagicMock(return_value=fake_ad_unit_per_referrer_response))
    mocker.patch.object(AdUnitPerReferrerReportStream, "get_custom_targeting_values", MagicMock(return_value=[{"id": "Referrer 1"}, {"id": "Referrer 2"}, {"id": "Referrer 3"}]))
    ad_unit_per_referrer_stream = AdUnitPerReferrerReportStream(google_ad_manager_client=google_ad_manager_client,
                                                                start_date=start_date,
                                                                end_date=end_date,
                                                                customer_name="test_customer_name")
    yield ad_unit_per_referrer_stream


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
