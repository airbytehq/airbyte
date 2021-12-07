#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import re
from base64 import b64decode
from unittest import mock

import pytest
import responses
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from pytest import raises
from requests.exceptions import ConnectionError
from source_amazon_ads.schemas.profile import AccountInfo, Profile
from source_amazon_ads.spec import AmazonAdsConfig
from source_amazon_ads.streams import (
    SponsoredBrandsReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayReportStream,
    SponsoredProductsReportStream,
)
from source_amazon_ads.streams.report_streams.report_streams import ReportGenerationFailure, ReportGenerationInProgress, TooManyRequests

"""
METRIC_RESPONSE is gzip compressed binary representing this string:
[
  {
    "campaignId": 214078428,
    "campaignName": "sample-campaign-name-214078428"
  },
  {
    "campaignId": 44504582,
    "campaignName": "sample-campaign-name-44504582"
  },
  {
    "campaignId": 509144838,
    "campaignName": "sample-campaign-name-509144838"
  },
  {
    "campaignId": 231712082,
    "campaignName": "sample-campaign-name-231712082"
  },
  {
    "campaignId": 895306040,
    "campaignName": "sample-campaign-name-895306040"
  }
]
"""
METRIC_RESPONSE = b64decode(
    """
H4sIAAAAAAAAAIvmUlCoBmIFBaXkxNyCxMz0PM8UJSsFI0MTA3MLEyMLHVRJv8TcVKC0UjGQn5Oq
CxPWzQOK68I1KQE11ergMNrExNTAxNTCiBSTYXrwGmxqYGloYmJhTJKb4ZrwGm1kbGhuaGRAmqPh
mvAabWFpamxgZmBiQIrRcE1go7liAYX9dsTHAQAA
"""
)
METRICS_COUNT = 5


def setup_responses(init_response=None, init_response_products=None, init_response_brands=None, status_response=None, metric_response=None):
    if init_response:
        responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), body=init_response, status=202)
    if init_response_products:
        responses.add(
            responses.POST,
            re.compile(r"https://advertising-api.amazon.com/v2/sp/[a-zA-Z]+/report"),
            body=init_response_products,
            status=202,
        )
    if init_response_brands:
        responses.add(
            responses.POST, re.compile(r"https://advertising-api.amazon.com/v2/hsa/[a-zA-Z]+/report"), body=init_response_brands, status=202
        )
    if status_response:
        responses.add(
            responses.GET,
            re.compile(r"https://advertising-api.amazon.com/v2/reports/[^/]+$"),
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
def test_display_report_stream(test_config):
    setup_responses(
        init_response=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()

    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)
    updated_state = stream.get_updated_state(None, stream_slice)
    assert updated_state == stream_slice

    profiles = make_profiles(profile_type="vendor")
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    # Skip asins record for vendor profiles
    assert len(metrics) == METRICS_COUNT * (len(stream.metrics_map) - 1)


@responses.activate
def test_products_report_stream(test_config):
    setup_responses(
        init_response_products=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles(profile_type="vendor")

    stream = SponsoredProductsReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725", "retry_count": 3}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_brands_report_stream(test_config):
    setup_responses(
        init_response_brands=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()

    stream = SponsoredBrandsReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_brands_video_report_stream(test_config):
    setup_responses(
        init_response_brands=REPORT_INIT_RESPONSE,
        status_response=REPORT_STATUS_RESPONSE,
        metric_response=METRIC_RESPONSE,
    )

    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()

    stream = SponsoredBrandsVideoReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    metrics = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(metrics) == METRICS_COUNT * len(stream.metrics_map)


@responses.activate
def test_display_report_stream_init_failure(mocker, test_config):
    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    responses.add(
        responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), json={"error": "some error"}, status=400
    )

    with pytest.raises(Exception):
        [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]


@responses.activate
def test_display_report_stream_init_http_exception(mocker, test_config):
    mocker.patch("time.sleep", lambda x: None)
    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), body=ConnectionError())

    with raises(ConnectionError):
        _ = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(responses.calls) == 5


@responses.activate
def test_display_report_stream_init_too_many_requests(mocker, test_config):
    mocker.patch("time.sleep", lambda x: None)
    config = AmazonAdsConfig(**test_config)
    profiles = make_profiles()
    stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
    stream_slice = {"reportDate": "20210725"}
    responses.add(responses.POST, re.compile(r"https://advertising-api.amazon.com/sd/[a-zA-Z]+/report"), json={}, status=429)

    with raises(TooManyRequests):
        _ = [m for m in stream.read_records(SyncMode.incremental, stream_slice=stream_slice)]
    assert len(responses.calls) == 5


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
                (lambda x: x > 5, None, "2021-01-02 03:34:05"),
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
                (lambda x: x >= 10, None, "2021-01-02 03:34:05"),
                (lambda x: x >= 15, None, "2021-01-02 04:04:05"),
                (lambda x: x >= 20, None, "2021-01-02 04:34:05"),
                (lambda x: x >= 25, None, "2021-01-02 05:04:05"),
                (lambda x: x >= 30, None, "2021-01-02 05:34:05"),
            ],
            ReportGenerationFailure,
        ),
    ],
)
@responses.activate
def test_display_report_stream_backoff(mocker, test_config, modifiers, expected):
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
        config = AmazonAdsConfig(**test_config)
        profiles = make_profiles()
        stream = SponsoredDisplayReportStream(config, profiles, authenticator=mock.MagicMock())
        stream_slice = {"reportDate": "20210725"}

        if isinstance(expected, int):
            list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))
            assert callback.count == expected
        elif issubclass(expected, Exception):
            with pytest.raises(expected):
                list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))


@freeze_time("2021-07-30 04:26:08")
@responses.activate
def test_display_report_stream_slices_full_refresh(test_config):
    config = AmazonAdsConfig(**test_config)
    stream = SponsoredDisplayReportStream(config, None, authenticator=mock.MagicMock())
    slices = stream.stream_slices(SyncMode.full_refresh, cursor_field=stream.cursor_field)
    assert slices == [{"reportDate": "20210730"}]


@freeze_time("2021-07-30 04:26:08")
@responses.activate
def test_display_report_stream_slices_incremental(test_config):
    config = AmazonAdsConfig(**test_config)
    stream = SponsoredDisplayReportStream(config, None, authenticator=mock.MagicMock())
    stream_state = {"reportDate": "20210726"}
    slices = stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state=stream_state)
    assert slices == [
        {"reportDate": "20210723"},
        {"reportDate": "20210724"},
        {"reportDate": "20210725"},
        {"reportDate": "20210726"},
        {"reportDate": "20210727"},
        {"reportDate": "20210728"},
        {"reportDate": "20210729"},
        {"reportDate": "20210730"},
    ]
    stream_state = {"reportDate": "20210730"}
    slices = stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state=stream_state)
    assert slices == [
        {"reportDate": "20210727"},
        {"reportDate": "20210728"},
        {"reportDate": "20210729"},
        {"reportDate": "20210730"},
    ]

    stream_state = {"reportDate": "20210731"}
    slices = stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state=stream_state)
    assert slices == [
        {"reportDate": "20210728"},
        {"reportDate": "20210729"},
        {"reportDate": "20210730"},
    ]

    slices = stream.stream_slices(SyncMode.incremental, cursor_field=stream.cursor_field, stream_state={})
    assert slices == [{"reportDate": "20210730"}]

    slices = stream.stream_slices(SyncMode.incremental, cursor_field=None, stream_state={})
    assert slices == [{"reportDate": "20210730"}]
