#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import re
from base64 import b64decode
from datetime import timedelta
from functools import partial
from unittest import mock

import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from pendulum import Date
from pytest import raises
from requests.exceptions import ConnectionError
from source_amazon_ads.schemas.profile import AccountInfo, Profile
from source_amazon_ads.source import CONFIG_DATE_FORMAT
from source_amazon_ads.streams import (
    SponsoredBrandsCampaigns,
    SponsoredBrandsReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayCampaigns,
    SponsoredDisplayReportStream,
    SponsoredProductCampaigns,
    SponsoredProductsReportStream,
)
from source_amazon_ads.streams.report_streams.report_streams import (
    RecordType,
    ReportGenerationFailure,
    ReportGenerationInProgress,
    TooManyRequests,
)

from .utils import read_incremental

"""
METRIC_RESPONSE is gzip compressed binary representing this string:
[
  {
    "campaignId": 214078428,
    "campaignName": "sample-campaign-name-214078428",
    "adGroupId": "6490134",
    "adId": "665320125",
    "targetId": "791320341",
    "asin": "G000PSH142",
    "advertisedAsin": "G000PSH142",
    "keywordBid": "511234974",
    "keywordId": "965783021"
  },
  {
    "campaignId": 44504582,
    "campaignName": "sample-campaign-name-44504582",
    "adGroupId": "6490134",
    "adId": "665320125",
    "targetId": "791320341",
    "asin": "G000PSH142",
    "advertisedAsin": "G000PSH142",
    "keywordBid": "511234974",
    "keywordId": "965783021"
  },
  {
    "campaignId": 509144838,
    "campaignName": "sample-campaign-name-509144838",
    "adGroupId": "6490134",
    "adId": "665320125",
    "targetId": "791320341",
    "asin": "G000PSH142",
    "advertisedAsin": "G000PSH142",
    "keywordBid": "511234974",
    "keywordId": "965783021"
  },
  {
    "campaignId": 231712082,
    "campaignName": "sample-campaign-name-231712082",
    "adGroupId": "6490134",
    "adId": "665320125",
    "targetId": "791320341",
    "asin": "G000PSH142",
    "advertisedAsin": "G000PSH142",
    "keywordBid": "511234974",
    "keywordId": "965783021"
  },
  {
    "campaignId": 895306040,
    "campaignName": "sample-campaign-name-895306040",
    "adGroupId": "6490134",
    "adId": "665320125",
    "targetId": "791320341",
    "asin": "G000PSH142",
    "advertisedAsin": "G000PSH142",
    "keywordBid": "511234974",
    "keywordId": "965783021"
  }
]
"""
METRIC_RESPONSE = b64decode(
    """
    H4sIAAAAAAAACuWSPWvDMBCGd/8KoTmGu9PJkrq1S5olBDqWDqIWwbRxgu
    02hJD/HjX+ooUMXutBg95Hzwle7jUR4hyPEPLd7w6+2JarXD4IQgZjmezi
    N1z7XYhY1vH+GdI+TsuYp4MkO8vny2r/dbhNlBk7QMUj6+JMKwIk3YPGV9
    vQtNA4jFAxDlZdlD9gCQCbl2dkGud9h6op6pA/3n3zEU7HfZU/FbfhGpEU
    O8N/cPu1y7SxCghlhJfFnZ6YNbC2NKWm3plPSxocMls1aZsGaT49kUKDBN
    PWaZDm05N1WkEGDFN6sr30/3pK3q5AhIPlyAUAAA==
"""
)
METRICS_COUNT = 5

METRIC_RESPONSE_WITHOUT_ASIN_PK = b64decode(
    """
    H4sIAAAAAAAAClXMvQrCMBQF4L1PETIbyM1v4+giLr6AOAQTStH+ECsi4r
    t7aZOKwx3u+TjnVBHyxiOEXnw3+rbpD4FuSe205IYrvvnHo+8iMr3jf4us
    xKzHnK0lmls+7NPwGOdFapTjINXPcmy0FByELjD51MRpQesAUSooeI2v55
    DCrp1ZAwipnF1HMy9lZ7StJRdAET/V+Qv1VRgd7AAAAA==
"""
)


def setup_responses(init_response=None, init_response_products=None, init_response_brands=None, status_response=None, metric_response=None):
    if init_response:
        responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), body=init_response, status=202)
    if init_response_products:
        responses.add(
            responses.POST,
            re.compile(r"https://advertising-api.amazon.com/reporting/reports"),
            body=init_response_products,
            status=200,
        )
        responses.add(
            responses.POST,
            re.compile(r"https://advertising-api.amazon.com/reporting/reports"),
            body=init_response_products,
            status=200,
        )
    if init_response_brands:
        responses.add(
            responses.POST, re.compile(r"https://advertising-api.amazon.com/v2/hsa/[a-zA-Z]+/report"), body=init_response_brands, status=202
        )
    if status_response:
        responses.add(
            responses.GET,
            re.compile(r"https://advertising-api.amazon.com/reporting/reports/[^/]+$"),
            body=status_response,
        )
        responses.add(
            responses.GET,
            re.compile(r"https://advertising-api.amazon.com/v2/reports/[^/]+$"),
            body=status_response,
        )
        responses.add(
            responses.GET,
            re.compile(r"https://advertising-api.amazon.com/reporting/reports"),
            body=status_response,
        )
    if metric_response:
        responses.add(
            responses.GET,
            "https://advertising-api-test.amazon.com/v1/reports/amzn1.sdAPI.v1.m1.61022EEC.2ac27e60-665c-46b4-b5a9-d72f216cc8ca/download",
            body=metric_response,
        )


REPORT_INIT_RESPONSE = """
{"reportId":"amzn1.sdAPI.v1.m1.61022EEC.2ac27e60-665c-46b4-b5a9-d72f216cc8ca","recordType":"campaigns","status":"IN_PROGRESS","statusDetails":"Generating report"}
"""

REPORT_STATUS_RESPONSE = """
{"reportId":"amzn1.sdAPI.v1.m1.61022EEC.2ac27e60-665c-46b4-b5a9-d72f216cc8ca","status":"SUCCESS","statusDetails":"Report successfully generated","location":"https://advertising-api-test.amazon.com/v1/reports/amzn1.sdAPI.v1.m1.61022EEC.2ac27e60-665c-46b4-b5a9-d72f216cc8ca/download","fileSize":144}
"""


def make_profiles(profile_type="seller"):
    return [
        Profile(
            profileId=1,
            timezone="America/Los_Angeles",
            accountInfo=AccountInfo(marketplaceStringId="", id="", type=profile_type),
        )
    ]


@responses.activate
def test_display_report_stream(config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()

    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)

    profiles = make_profiles(profile_type="vendor")
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice["profile"] = profiles[0]
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    # Skip asins record for vendor profiles
    assert len(metrics) == METRICS_COUNT * (len(stream.metrics_map) - 1)


@pytest.mark.parametrize(
    ("profiles", "stream_class", "url_pattern", "expected"),
    [
        (
            make_profiles(),
            SponsoredDisplayReportStream,
            r"https://advertising-api.amazon.com/sd/([a-zA-Z]+)/report",
            True,
        ),
        (
            make_profiles(profile_type="vendor"),
            SponsoredDisplayReportStream,
            r"https://advertising-api.amazon.com/sd/([a-zA-Z]+)/report",
            False,
        ),
    ],
)
@responses.activate
def test_stream_report_body_metrics(config, profiles, stream_class, url_pattern, expected):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        init_response_products=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    stream = stream_class(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
    for call in responses.calls:
        create_report_pattern = re.compile(url_pattern)
        for match in create_report_pattern.finditer(call.request.url):
            record_type = match.group(1)
            request_body = call.request.body
            request_metrics = json.loads(request_body.decode("utf-8"))["metrics"]
            if record_type == RecordType.PRODUCTADS or record_type == RecordType.ASINS:
                assert ("sku" in request_metrics) == expected
            else:
                assert "sku" not in request_metrics


@responses.activate
def test_products_report_stream(config):
    setup_responses(
        init_response_products=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles(profile_type="vendor")

    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "2021-07-25", "retry_count": 3}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_products_report_stream_without_pk(config):
    setup_responses(
        init_response_products=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE_WITHOUT_ASIN_PK,
    )

    profiles = make_profiles(profile_type="vendor")

    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "2021-07-25", "retry_count": 3}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]

    assert len(metrics) == len(stream.metrics_map)


@responses.activate
def test_brands_report_stream(config):
    setup_responses(
        init_response_brands=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()

    stream = SponsoredBrandsReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_brands_video_report_stream(config):
    setup_responses(
        init_response_brands=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()

    stream = SponsoredBrandsVideoReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_display_report_stream_init_failure(mocker, config):
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    responses.add(
        responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), json={"error": "some error"}, status=400
    )

    sleep_mock = mocker.patch("time.sleep")
    with pytest.raises(Exception):
        [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]

    assert sleep_mock.call_count == 4
    assert len(responses.calls) == 5


@responses.activate
def test_display_report_stream_init_http_exception(mocker, config):
    mocker.patch("time.sleep", lambda x: None)
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), body=ConnectionError())

    with raises(ConnectionError):
        _ = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(responses.calls) == 10


@responses.activate
def test_display_report_stream_init_too_many_requests(mocker, config):
    mocker.patch("time.sleep", lambda x: None)
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), json={}, status=429)

    with raises(TooManyRequests):
        _ = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(responses.calls) == 10


@pytest.mark.parametrize(
    ("modifiers", "expected"),
    [
        (
            [
                (lambda x: x <= 5, "SUCCESS", None),
            ],
            5,
        ),
        (
            [
                (lambda x: x > 5, "SUCCESS", None),
            ],
            10,
        ),
        (
            [
                (lambda x: x > 5, None, "2021-01-02 06:04:05"),
            ],
            ReportGenerationInProgress,
        ),
        (
            [
                (lambda x: x >= 1 and x <= 5, "FAILURE", None),
                (lambda x: x >= 6 and x <= 10, None, "2021-01-02 03:23:05"),
                (lambda x: x >= 11, "SUCCESS", "2021-01-02 03:24:06"),
            ],
            15,
        ),
        (
            [
                (lambda x: True, "FAILURE", None),
                (lambda x: x >= 10, None, "2021-01-02 06:04:05"),
                (lambda x: x >= 15, None, "2021-01-02 09:04:05"),
                (lambda x: x >= 20, None, "2021-01-02 12:04:05"),
                (lambda x: x >= 25, None, "2021-01-02 15:04:05"),
                (lambda x: x >= 30, None, "2021-01-02 18:04:05"),
            ],
            ReportGenerationFailure,
        ),
    ],
)
@responses.activate
def test_display_report_stream_backoff(mocker, config, modifiers, expected):
    mocker.patch("time.sleep")
    setup_responses(init_response=REPORT_INIT_RESPONSE, metric_response=METRIC_RESPONSE)

    with freeze_time("2021-01-02 03:04:05") as frozen_time:

        class StatusCallback:
            count: int = 0

            def __call__(self, request):
                self.count += 1
                response = REPORT_STATUS_RESPONSE.replace("SUCCESS", "IN_PROGRESS")

                for index, status, time in modifiers:
                    if index(self.count):
                        if status:
                            response = response.replace("IN_PROGRESS", status)
                        if time:
                            frozen_time.move_to(time)
                return (200, {}, response)

        callback = StatusCallback()
        responses.add_callback(responses.GET, re.compile(r"https://advertising-api.amazon.com/v2/reports/[^/]+$"), callback=callback)
        profiles = make_profiles()
        stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
        stream_slice = {"profile": profiles[0], "reportDate": "20210725"}

        if isinstance(expected, int):
            list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
            assert callback.count == expected
        elif issubclass(expected, Exception):
            with pytest.raises(expected):
                list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))


@freeze_time("2021-07-30 04:26:08")
@responses.activate
def test_display_report_stream_slices_full_refresh(config):
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    slices = list(stream.stream_slices(SyncMode.full_refresh, cursor_field=stream.cursor_field))
    assert slices == [{"profile": profiles[0], "reportDate": "20210729"}]


@freeze_time("2021-07-30 04:26:08")
@responses.activate
def test_display_report_stream_slices_incremental(config):
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_state = {str(profiles[0].profileId): {"reportDate": "20210725"}}
    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state=stream_state))
    assert slices == [
        {"profile": profiles[0], "reportDate": "20210725"},
        {"profile": profiles[0], "reportDate": "20210726"},
        {"profile": profiles[0], "reportDate": "20210727"},
        {"profile": profiles[0], "reportDate": "20210728"},
        {"profile": profiles[0], "reportDate": "20210729"},
    ]

    stream_state = {str(profiles[0].profileId): {"reportDate": "20210730"}}
    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state=stream_state))
    assert slices == [None]

    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state={}))
    assert slices == [{"profile": profiles[0], "reportDate": "20210729"}]

    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field=None, stream_state={}))
    assert slices == [{"profile": profiles[0], "reportDate": "20210729"}]


@freeze_time("2021-08-01 04:00:00")
def test_get_start_date(config):
    profiles = make_profiles()

    config["start_date"] = pendulum.from_format("2021-07-10", CONFIG_DATE_FORMAT).date()
    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    assert stream.get_start_date(profiles[0], {}) == Date(2021, 7, 10)
    config["start_date"] = pendulum.from_format("2021-05-10", CONFIG_DATE_FORMAT).date()
    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    assert stream.get_start_date(profiles[0], {}) == Date(2021, 6, 1)

    profile_id = str(profiles[0].profileId)
    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    assert stream.get_start_date(profiles[0], {profile_id: {"reportDate": "2021-08-10"}}) == Date(2021, 8, 10)
    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    assert stream.get_start_date(profiles[0], {profile_id: {"reportDate": "2021-05-10"}}) == Date(2021, 6, 1)

    config.pop("start_date")
    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    assert stream.get_start_date(profiles[0], {}) == Date(2021, 7, 31)


@freeze_time("2021-08-01 04:00:00")
def test_stream_slices_different_timezones(config):
    profile1 = Profile(profileId=1, timezone="America/Los_Angeles", accountInfo=AccountInfo(marketplaceStringId="", id="", type="seller"))
    profile2 = Profile(profileId=2, timezone="UTC", accountInfo=AccountInfo(marketplaceStringId="", id="", type="seller"))
    stream = SponsoredProductsReportStream(config, [profile1, profile2], authenticator=mock.MagicMock())
    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state={}))
    assert slices == [{"profile": profile1, "reportDate": "2021-07-31"}, {"profile": profile2, "reportDate": "2021-08-01"}]


def test_stream_slices_lazy_evaluation(config):
    with freeze_time("2022-06-01T23:50:00+00:00") as frozen_datetime:
        config["start_date"] = pendulum.from_format("2021-05-10", CONFIG_DATE_FORMAT).date()
        profile1 = Profile(profileId=1, timezone="UTC", accountInfo=AccountInfo(marketplaceStringId="", id="", type="seller"))
        profile2 = Profile(profileId=2, timezone="UTC", accountInfo=AccountInfo(marketplaceStringId="", id="", type="seller"))

        stream = SponsoredProductsReportStream(config, [profile1, profile2], authenticator=mock.MagicMock())
        stream.REPORTING_PERIOD = 5

        slices = []
        for _slice in stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field):
            slices.append(_slice)
            frozen_datetime.tick(delta=timedelta(minutes=10))

        assert slices == [
            {"profile": profile1, "reportDate": "2022-05-27"},
            {"profile": profile2, "reportDate": "2022-05-28"},
            {"profile": profile1, "reportDate": "2022-05-28"},
            {"profile": profile2, "reportDate": "2022-05-29"},
            {"profile": profile1, "reportDate": "2022-05-29"},
            {"profile": profile2, "reportDate": "2022-05-30"},
            {"profile": profile1, "reportDate": "2022-05-30"},
            {"profile": profile2, "reportDate": "2022-05-31"},
            {"profile": profile1, "reportDate": "2022-05-31"},
            {"profile": profile2, "reportDate": "2022-06-01"},
            {"profile": profile1, "reportDate": "2022-06-01"},
            {"profile": profile2, "reportDate": "2022-06-02"},
            {"profile": profile1, "reportDate": "2022-06-02"},
        ]


def test_get_date_range_lazy_evaluation():
    get_date_range = partial(SponsoredProductsReportStream.get_date_range, SponsoredProductsReportStream)

    with freeze_time("2022-06-01T12:00:00+00:00") as frozen_datetime:
        date_range = list(get_date_range(start_date=Date(2022, 5, 29), timezone="UTC"))
        assert date_range == ["2022-05-29", "2022-05-30", "2022-05-31", "2022-06-01"]

        date_range = list(get_date_range(start_date=Date(2022, 6, 1), timezone="UTC"))
        assert date_range == ["2022-06-01"]

        date_range = list(get_date_range(start_date=Date(2022, 6, 2), timezone="UTC"))
        assert date_range == []

        date_range = []
        for date in get_date_range(start_date=Date(2022, 5, 29), timezone="UTC"):
            date_range.append(date)
            frozen_datetime.tick(delta=timedelta(hours=3))
        assert date_range == ["2022-05-29", "2022-05-30", "2022-05-31", "2022-06-01", "2022-06-02"]


@responses.activate
def test_read_incremental_without_records(config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=b64decode("H4sIAAAAAAAAAIuOBQApu0wNAgAAAA=="),
    )

    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())

    with freeze_time("2021-01-02 12:00:00") as frozen_datetime:
        state = {}
        reportDates = ["20210102", "20210102", "20210102", "20210103", "20210104", "20210105"]
        for reportDate in reportDates:
            records = list(read_incremental(stream, state))
            assert state == {"1": {"reportDate": reportDate}}
            assert records == []
            frozen_datetime.tick(delta=timedelta(days=1))


@responses.activate
def test_read_incremental_with_records(config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())

    with freeze_time("2021-01-02 12:00:00") as frozen_datetime:
        state = {}
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210102"}}
        assert {r["reportDate"] for r in records} == {"20210102"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210102"}}
        assert {r["reportDate"] for r in records} == {"20210102", "20210103"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210102"}}
        assert {r["reportDate"] for r in records} == {"20210102", "20210103", "20210104"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210103"}}
        assert {r["reportDate"] for r in records} == {"20210102", "20210103", "20210104", "20210105"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210104"}}
        assert {r["reportDate"] for r in records} == {"20210103", "20210104", "20210105", "20210106"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210105"}}
        assert {r["reportDate"] for r in records} == {"20210104", "20210105", "20210106", "20210107"}


@responses.activate
def test_read_incremental_without_records_start_date(config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=b64decode("H4sIAAAAAAAAAIuOBQApu0wNAgAAAA=="),
    )

    profiles = make_profiles()
    config["start_date"] = pendulum.from_format("2020-12-25", CONFIG_DATE_FORMAT).date()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())

    with freeze_time("2021-01-02 12:00:00") as frozen_datetime:
        state = {}
        reportDates = ["20201231", "20210101", "20210102", "20210103", "20210104"]
        for reportDate in reportDates:
            records = list(read_incremental(stream, state))
            assert state == {"1": {"reportDate": reportDate}}
            assert records == []
            frozen_datetime.tick(delta=timedelta(days=1))


@responses.activate
def test_read_incremental_with_records_start_date(config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()
    config["start_date"] = pendulum.from_format("2020-12-25", CONFIG_DATE_FORMAT).date()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())

    with freeze_time("2021-01-02 12:00:00") as frozen_datetime:
        state = {}
        records = list(read_incremental(stream, state))

        assert state == {"1": {"reportDate": "20201231"}}
        assert {r["reportDate"] for r in records} == {
            "20201225",
            "20201226",
            "20201227",
            "20201228",
            "20201229",
            "20201230",
            "20201231",
            "20210101",
            "20210102",
        }

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210101"}}
        assert {r["reportDate"] for r in records} == {"20201231", "20210101", "20210102", "20210103"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210102"}}
        assert {r["reportDate"] for r in records} == {"20210101", "20210102", "20210103", "20210104"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210103"}}
        assert {r["reportDate"] for r in records} == {"20210102", "20210103", "20210104", "20210105"}

        frozen_datetime.tick(delta=timedelta(days=1))
        records = list(read_incremental(stream, state))
        assert state == {"1": {"reportDate": "20210104"}}
        assert {r["reportDate"] for r in records} == {"20210103", "20210104", "20210105", "20210106"}


@pytest.mark.parametrize(
    "state_filter, stream_class",
    [
        (
            ["enabled", "archived", "paused"],
            SponsoredBrandsCampaigns,
        ),
        (
            ["enabled"],
            SponsoredBrandsCampaigns,
        ),
        (
            None,
            SponsoredBrandsCampaigns,
        ),
        (
            ["enabled", "archived", "paused"],
            SponsoredProductCampaigns,
        ),
        (
            ["enabled"],
            SponsoredProductCampaigns,
        ),
        (
            None,
            SponsoredProductCampaigns,
        ),
        (
            ["enabled", "archived", "paused"],
            SponsoredDisplayCampaigns,
        ),
        (
            ["enabled"],
            SponsoredDisplayCampaigns,
        ),
        (
            None,
            SponsoredDisplayCampaigns,
        ),
    ],
)
def test_streams_state_filter(mocker, config, state_filter, stream_class):
    profiles = make_profiles()
    mocker.patch.object(stream_class, "state_filter", new_callable=mocker.PropertyMock, return_value=state_filter)

    stream = stream_class(config, profiles)
    params = stream.request_params(stream_state=None, stream_slice=None, next_page_token=None)
    if "stateFilter" in params:
        assert params["stateFilter"] == ",".join(state_filter)
    else:
        assert state_filter is None


@responses.activate
@pytest.mark.parametrize(
    "custom_record_types, flag_match_error",
    [
        (
                ["campaigns"],
                True
        ),
        (
                ["campaigns", "adGroups"],
                True
        ),
        (
                [],
                False
        ),
        (
                ["invalid_record_type"],
                True
        )
    ]
)
def test_display_report_stream_with_custom_record_types(config_gen, custom_record_types, flag_match_error):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()

    stream = SponsoredDisplayReportStream(config_gen(report_record_types=custom_record_types), profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    records = list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
    for record in records:
        if record['recordType'] not in custom_record_types:
            if flag_match_error:
                assert False


@responses.activate
@pytest.mark.parametrize(
    "custom_record_types, expected_record_types, flag_match_error",
    [
        (
                ["campaigns"],
                ["campaigns"],
                True
        ),
        (
                ["asins_keywords"],
                ["asins_keywords"],
                True
        ),
        (
                ["asins_targets"],
                ["asins_targets"],
                True
        ),
        (
                ["campaigns", "adGroups"],
                ["campaigns", "adGroups"],
                True
        ),
        (
                [],
                [],
                False
        ),
        (
                ["invalid_record_type"],
                [],
                True
        )
    ]
)
def test_products_report_stream_with_custom_record_types(config_gen, custom_record_types, expected_record_types, flag_match_error):
    setup_responses(
        init_response_products=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles(profile_type="vendor")

    stream = SponsoredProductsReportStream(config_gen(report_record_types=custom_record_types), profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "2021-07-25", "retry_count": 3}
    records = list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
    for record in records:
        print(record)
        if record['recordType'] not in expected_record_types:
            if flag_match_error:
                assert False


@responses.activate
@pytest.mark.parametrize(
    "custom_record_types, expected_record_types, flag_match_error",
    [
        (
                ["campaigns"],
                ["campaigns"],
                True
        ),
        (
                ["asins"],
                ["asins"],
                True
        ),
        (
                ["campaigns", "adGroups"],
                ["campaigns", "adGroups"],
                True
        ),
        (
                [],
                [],
                False
        ),
        (
                ["invalid_record_type"],
                [],
                True
        )
    ]
)
def test_brands_video_report_with_custom_record_types(config_gen, custom_record_types, expected_record_types, flag_match_error):
    setup_responses(
        init_response_brands=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    profiles = make_profiles()

    stream = SponsoredBrandsVideoReportStream(config_gen(report_record_types=custom_record_types), profiles, authenticator=mock.MagicMock())
    stream_slice = {"profile": profiles[0], "reportDate": "20210725"}
    records = list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
    for record in records:
        print(record)
        if record['recordType'] not in expected_record_types:
            if flag_match_error:
                assert False
