#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from jsonschema import validate
from source_amazon_ads import SourceAmazonAds
from source_amazon_ads.schemas.profile import AccountInfo, Profile
from source_amazon_ads.streams import AttributionReportProducts

from .utils import read_full_refresh


def setup_responses(
    profiles_response=None,
    attribution_report_response=None,
):
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "access_token", "expires_in": 10},
    )
    if profiles_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/v2/profiles",
            body=profiles_response,
        )
    if attribution_report_response:
        responses.add(
            responses.POST,
            "https://advertising-api.amazon.com/attribution/report",
            body=attribution_report_response,
        )


def get_stream_by_name(streams, stream_name):
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise Exception(f"Expected stream {stream_name} not found")


@pytest.mark.parametrize(
    ("stream_name", "report_type"),
    [
        ("attribution_report_products", "PRODUCTS"),
        ("attribution_report_performance_adgroup", "PERFORMANCE_ADGROUP"),
        ("attribution_report_performance_campaign", "PERFORMANCE_CAMPAIGN"),
        ("attribution_report_performance_creative", "PERFORMANCE_CREATIVE"),
    ],
)
@responses.activate
def test_attribution_report_schema(config, profiles_response, attribution_report_response, stream_name, report_type):
    # custom start date
    config["start_date"] = "2022-09-03"

    setup_responses(profiles_response=profiles_response, attribution_report_response=attribution_report_response(report_type))

    source = SourceAmazonAds()
    streams = source.streams(config)

    profile_stream = get_stream_by_name(streams, "profiles")
    attribution_report_stream = get_stream_by_name(streams, stream_name)
    schema = attribution_report_stream.get_json_schema()
    schema["additionalProperties"] = False

    profile_records = list(read_full_refresh(profile_stream))
    attribution_records = list(read_full_refresh(attribution_report_stream))
    assert len(attribution_records) == len(profile_records) * len(json.loads(attribution_report_response(report_type)).get("reports"))

    for record in attribution_records:
        validate(schema=schema, instance=record)


@pytest.mark.parametrize(
    ("stream_name", "report_type"),
    [
        ("attribution_report_products", "PRODUCTS"),
        ("attribution_report_performance_adgroup", "PERFORMANCE_ADGROUP"),
        ("attribution_report_performance_campaign", "PERFORMANCE_CAMPAIGN"),
        ("attribution_report_performance_creative", "PERFORMANCE_CREATIVE"),
    ],
)
@responses.activate
def test_attribution_report_with_pagination(mocker, config, profiles_response, attribution_report_response, stream_name, report_type):
    profiles = json.loads(profiles_response)
    # use only single profile
    profiles_response = json.dumps([profiles[0]])

    setup_responses(profiles_response=profiles_response)

    source = SourceAmazonAds()
    streams = source.streams(config)

    attribution_report_stream = get_stream_by_name(streams, stream_name)
    attribution_data = json.loads(attribution_report_response(report_type))

    def _callback(request: requests.PreparedRequest):
        attribution_data["cursorId"] = None
        request_data = json.loads(request.body)

        if request_data["count"] > 0:
            mocker.patch("source_amazon_ads.streams.attribution_report.AttributionReport.page_size", 0)
            attribution_data["cursorId"] = "next_page_token"

        return 200, {}, json.dumps(attribution_data)

    responses.add_callback(
        responses.POST,
        "https://advertising-api.amazon.com/attribution/report",
        content_type="application/json",
        callback=_callback,
    )

    attribution_records = list(read_full_refresh(attribution_report_stream))

    # request should be called 2 times for a single profile
    assert len(attribution_records) == 2 * len(attribution_data.get("reports"))


@freeze_time("2022-05-15 12:00:00")
def test_attribution_report_slices(config):

    profiles = [
        Profile(profileId=1, timezone="America/Los_Angeles", accountInfo=AccountInfo(id="1", type="seller", marketplaceStringId="")),
        Profile(profileId=2, timezone="America/Los_Angeles", accountInfo=AccountInfo(id="1", type="seller", marketplaceStringId="")),
    ]

    stream = AttributionReportProducts(config, profiles=profiles)
    slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

    assert slices == [
        {'profileId': 1, 'startDate': '20220514', 'endDate': '20220515'},
        {'profileId': 2, 'startDate': '20220514', 'endDate': '20220515'}
    ]

    config["start_date"] = pendulum.from_format("2022-05-01", "YYYY-MM-DD").date()
    stream = AttributionReportProducts(config, profiles=profiles)
    slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert slices == [
        {'profileId': 1, 'startDate': '20220501', 'endDate': '20220515'},
        {'profileId': 2, 'startDate': '20220501', 'endDate': '20220515'}
    ]

    config["start_date"] = pendulum.from_format("2022-01-01", "YYYY-MM-DD").date()
    stream = AttributionReportProducts(config, profiles=profiles)
    slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert slices == [
        {'profileId': 1, 'startDate': '20220214', 'endDate': '20220515'},
        {'profileId': 2, 'startDate': '20220214', 'endDate': '20220515'}
    ]
