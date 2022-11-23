import pytest
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock
from source_google_ad_manager.streams import AdUnitPerHourReportStream, BaseGoogleAdManagerReportStream, AdUnitPerReferrerReportStream
from source_google_ad_manager.utils import convert_time_to_dict


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(BaseGoogleAdManagerReportStream, "run_report", MagicMock(return_value="fake_id"))
    mocker.patch.object(BaseGoogleAdManagerReportStream, "__abstractmethods__", set())
    BaseGoogleAdManagerReportStream.google_ad_manager_client = MagicMock()
    BaseGoogleAdManagerReportStream.report_downloader = MagicMock()
    BaseGoogleAdManagerReportStream.report_downloader.download_report.return_value = "fake_report"


@pytest.fixture(name="ad_unit_per_hour_stream")
def generate_ad_unit_per_hour_stream(patch_base_class, ad_unit_per_hour_report_df, test_date, mocker):
    start_date = end_date = convert_time_to_dict(test_date)
    google_ad_manager_client = MagicMock()
    mocker.patch.object(AdUnitPerHourReportStream, "build_report_dataframe", MagicMock(return_value=ad_unit_per_hour_report_df))
    start_date = "2022-10-01"
    timezone = "America/Chicago"
    ad_unit_per_hour_stream = AdUnitPerHourReportStream(google_ad_manager_client=google_ad_manager_client,
                                                        customer_name="test_customer_name",
                                                        start_date=start_date,
                                                        timezone=timezone)
    assert ad_unit_per_hour_stream.start_date
    assert ad_unit_per_hour_stream.today_date
    yield ad_unit_per_hour_stream


@pytest.fixture(name="test_date")
def generate_test_date():
    return datetime(2021, 10, 1)


@pytest.fixture(name="ad_unit_per_referrer_stream")
def generate_ad_unit_per_referrer_stream(patch_base_class, ad_unit_per_referrer_report_df, test_date, mocker):
    google_ad_manager_client = MagicMock()
    mocker.patch.object(AdUnitPerReferrerReportStream, "build_report_dataframe", MagicMock(return_value=ad_unit_per_referrer_report_df))
    mocker.patch.object(AdUnitPerReferrerReportStream, "get_custom_targeting_values", MagicMock(return_value=[{"id": "Referrer 1"}, {"id": "Referrer 2"}, {"id": "Referrer 3"}]))
    ad_unit_per_referrer_stream = AdUnitPerReferrerReportStream(google_ad_manager_client=google_ad_manager_client,
                                                                customer_name="test_customer_name",
                                                                start_date="2022-10-01",
                                                                timezone="America/Chicago")
    yield ad_unit_per_referrer_stream


@pytest.fixture(name='ad_unit_per_hour_report_df')
def generate_ad_unit_per_hour_report_file():
    yield pd.DataFrame([{
        'Ad unit 1': 'smartview-shop',
        'Dimension.HOUR': 2,
        'Dimension.DATE': '2022-11-22',
        'Ad unit ID 1': 22234973885,
        'Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS': 0,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 1609,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 3,
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 943590,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 586445,
        'Column.TOTAL_LINE_ITEM_LEVEL_CTR': 0.0019,
        'Column.TOTAL_CODE_SERVED_COUNT': 1801,
        }, {
        'Ad unit 1': 'smartview-shop',
        'Dimension.HOUR': 8,
        'Dimension.DATE': '2022-11-22',
        'Ad unit ID 1': 22234973885,
        'Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS': 0,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 5710,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 13,
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 4700231,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 823158,
        'Column.TOTAL_LINE_ITEM_LEVEL_CTR': 0.0023,
        'Column.TOTAL_CODE_SERVED_COUNT': 6318,
        }, {
        'Ad unit 1': 'amp-shop',
        'Dimension.HOUR': 2,
        'Dimension.DATE': '2022-11-22',
        'Ad unit ID 1': 22063950859,
        'Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS': 16,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 7460,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 62,
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 16260213,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 2179653,
        'Column.TOTAL_LINE_ITEM_LEVEL_CTR': 0.0083,
        'Column.TOTAL_CODE_SERVED_COUNT': 12462,
        }])


@pytest.fixture(name='ad_unit_per_referrer_report_df')
def generate_ad_unit_per_referrer_report_file():
    yield pd.DataFrame([{
        'Dimension.ADVERTISER_NAME': 'shop_Shop',
        'Dimension.CUSTOM_CRITERIA': 'referrer=search',
        'Ad unit ID 1': 22063950859,
        'Dimension.DATE': '2022-11-22',
        'Dimension.ADVERTISER_ID': 5229168415,
        'Dimension.CUSTOM_TARGETING_VALUE_ID': 448229826885,
        'Ad unit 1': 'amp-shop',
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 135450,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 2709,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 4,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 50000,
        'Column.TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS': 1642,
        'Column.TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS': 2709,
        'Column.TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS': 2709,
        }, {
        'Dimension.ADVERTISER_NAME': '-',
        'Dimension.CUSTOM_CRITERIA': 'referrer=smartnews',
        'Ad unit ID 1': 22063950859,
        'Dimension.DATE': '2022-11-22',
        'Dimension.ADVERTISER_ID': -1,
        'Dimension.CUSTOM_TARGETING_VALUE_ID': 448258036235,
        'Ad unit 1': 'amp-shop',
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 16809023,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 11420,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 147,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 1471893,
        'Column.TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS': 8932,
        'Column.TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS': 11395,
        'Column.TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS': 11410,
        }, {
        'Dimension.ADVERTISER_NAME': 'Amazon',
        'Dimension.CUSTOM_CRITERIA': 'referrer=facebook',
        'Ad unit ID 1': 22061790345,
        'Dimension.DATE': '2022-11-22',
        'Dimension.ADVERTISER_ID': 5161608643,
        'Dimension.CUSTOM_TARGETING_VALUE_ID': 448229826846,
        'Ad unit 1': 'mw-shop',
        'Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE': 23021204,
        'Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS': 6027,
        'Column.TOTAL_LINE_ITEM_LEVEL_CLICKS': 0,
        'Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM': 3819679,
        'Column.TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS': 4613,
        'Column.TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS': 5591,
        'Column.TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS': 6027,
        }])
