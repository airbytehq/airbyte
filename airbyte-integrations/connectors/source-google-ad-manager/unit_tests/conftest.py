import pytest
from datetime import datetime
from unittest.mock import MagicMock
from source_google_ad_manager.streams import AdUnitPerHourReportStream, BaseGoogleAdManagerReportStream, AdUnitPerReferrerReportStream
from source_google_ad_manager.utils import convert_time_to_dict
from io import BytesIO


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
def generate_ad_unit_per_referrer_stream(patch_base_class, test_date, mocker):
    start_date = end_date = convert_time_to_dict(test_date)
    google_ad_manager_client = MagicMock()
    fake_ad_unit_per_referrer_response = BytesIO(b"""\
Column.TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS,Column.TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM,Column.TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS,Ad unit 1,Dimension.CUSTOM_CRITERIA,Dimension.DATE,Column.TOTAL_LINE_ITEM_LEVEL_CLICKS
,0,0,1,1,Ad unit 1,Referrer 1,2021-10-01,1
1,1,0,1,0,Ad unit 1,Referrer 2,2021-10-01,1
1,1,0,1,0,Ad unit 1,Referrer 3,2021-10-01,1""")
    mocker.patch.object(AdUnitPerReferrerReportStream, "download_report", MagicMock(return_value=fake_ad_unit_per_referrer_response))
    mocker.patch.object(AdUnitPerReferrerReportStream, "get_custom_targeting_values", MagicMock(return_value=[{"id": "Referrer 1"}, {"id": "Referrer 2"}, {"id": "Referrer 3"}]))
    ad_unit_per_referrer_stream = AdUnitPerReferrerReportStream(google_ad_manager_client=google_ad_manager_client,
                                                                customer_name="test_customer_name",
                                                                start_date="2022-10-01",
                                                                timezone="America/Chicago")
    yield ad_unit_per_referrer_stream

