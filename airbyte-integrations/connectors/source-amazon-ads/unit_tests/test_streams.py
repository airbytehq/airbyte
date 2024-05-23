#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from jsonschema import validate
from source_amazon_ads import SourceAmazonAds


def setup_responses(
    profiles_response=None,
    portfolios_response=None,
    campaigns_response=None,
    adgroups_response=None,
    targeting_response=None,
    product_ads_response=None,
    generic_response=None,
    creatives_response=None,
    post_response=None,
):
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "alala", "expires_in": 10},
    )
    if profiles_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/v2/profiles",
            body=profiles_response,
        )
    if portfolios_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/v2/portfolios/extended",
            body=portfolios_response,
        )
    if campaigns_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/sd/campaigns",
            body=campaigns_response,
        )
    if adgroups_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/sd/adGroups",
            body=adgroups_response,
        )
    if targeting_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/sd/targets",
            body=targeting_response,
        )
    if product_ads_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/sd/productAds",
            body=product_ads_response,
        )
    if creatives_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/sd/creatives",
            body=creatives_response,
        )
    if generic_response:
        responses.add(
            responses.GET,
            f"https://advertising-api.amazon.com/{generic_response}",
            json=[],
        )
    if post_response:
        responses.add(
            responses.POST,
            f"https://advertising-api.amazon.com/{post_response}",
            json={},
        )


def get_all_stream_records(stream, stream_slice=None):
    records = stream.read_records(SyncMode.full_refresh, stream_slice=stream_slice)
    return [r for r in records]


def get_stream_by_name(streams, stream_name):
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise Exception(f"Expected stream {stream_name} not found")


@responses.activate
def test_streams_profile(config, profiles_response):
    setup_responses(profiles_response=profiles_response)

    source = SourceAmazonAds()
    streams = source.streams(config)

    profile_stream = get_stream_by_name(streams, "profiles")
    schema = profile_stream.get_json_schema()
    records = get_all_stream_records(profile_stream)
    assert len(responses.calls) == 2
    assert len(profile_stream._profiles) == 4
    assert len(records) == 4
    expected_records = json.loads(profiles_response)
    for record, expected_record in zip(records, expected_records):
        validate(schema=schema, instance=record)
        assert record == expected_record


@responses.activate
def test_streams_portfolios(config, profiles_response, portfolios_response):
    setup_responses(profiles_response=profiles_response, portfolios_response=portfolios_response)

    source = SourceAmazonAds()
    streams = source.streams(config)

    portfolio_stream = get_stream_by_name(streams, "portfolios")
    schema = portfolio_stream.get_json_schema()
    records = get_all_stream_records(portfolio_stream)
    assert len(responses.calls) == 6
    assert len(records) == 8
    expected_records = json.loads(portfolios_response)
    for record, expected_record in zip(records, expected_records):
        validate(schema=schema, instance=record)
        assert record == expected_record


@responses.activate
def test_streams_campaigns_4_vendors(config, profiles_response, campaigns_response):
    profiles_response = json.loads(profiles_response)
    for profile in profiles_response:
        profile["accountInfo"]["type"] = "vendor"
    profiles_response = json.dumps(profiles_response)
    setup_responses(profiles_response=profiles_response, campaigns_response=campaigns_response)

    source = SourceAmazonAds()
    streams = source.streams(config)
    profile_stream = get_stream_by_name(streams, "profiles")
    campaigns_stream = get_stream_by_name(streams, "sponsored_display_campaigns")
    profile_records = get_all_stream_records(profile_stream)
    campaigns_records = get_all_stream_records(campaigns_stream)
    assert len(campaigns_records) == len(profile_records) * len(json.loads(campaigns_response))


@pytest.mark.parametrize(
    ("page_size"),
    [1, 2, 5, 1000000],
)
@responses.activate
def test_streams_campaigns_pagination(mocker, config, profiles_response, campaigns_response, page_size):
    mocker.patch("source_amazon_ads.streams.common.SubProfilesStream.page_size", page_size)
    profiles_response = json.loads(profiles_response)
    for profile in profiles_response:
        profile["accountInfo"]["type"] = "vendor"
    profiles_response = json.dumps(profiles_response)
    setup_responses(profiles_response=profiles_response)

    source = SourceAmazonAds()
    streams = source.streams(config)
    profile_stream = get_stream_by_name(streams, "profiles")
    campaigns_stream = get_stream_by_name(streams, "sponsored_display_campaigns")
    campaigns = json.loads(campaigns_response)

    def campaigns_paginated_response_cb(request):
        query = urlparse(request.url).query
        query = parse_qs(query)
        start_index, count = (int(query.get(f, [0])[0]) for f in ["startIndex", "count"])
        response_body = campaigns[start_index : start_index + count]
        return (200, {}, json.dumps(response_body))

    responses.add_callback(
        responses.GET,
        "https://advertising-api.amazon.com/sd/campaigns",
        content_type="application/json",
        callback=campaigns_paginated_response_cb,
    )
    profile_records = get_all_stream_records(profile_stream)

    campaigns_records = get_all_stream_records(campaigns_stream)
    assert len(campaigns_records) == len(profile_records) * len(json.loads(campaigns_response))


@pytest.mark.parametrize(("status_code"), [HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED])
@responses.activate
def test_streams_campaigns_pagination_403_error(mocker, status_code, config, profiles_response, campaigns_response):
    setup_responses(profiles_response=profiles_response)
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/sd/campaigns",
        json={"message": "msg"},
        status=status_code,
    )
    source = SourceAmazonAds()
    streams = source.streams(config)
    campaigns_stream = get_stream_by_name(streams, "sponsored_display_campaigns")

    with pytest.raises(requests.exceptions.HTTPError):
        get_all_stream_records(campaigns_stream)


@responses.activate
def test_streams_campaigns_pagination_403_error_expected(mocker, config, profiles_response, campaigns_response):
    setup_responses(profiles_response=profiles_response)
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/sd/campaigns",
        json={"code": "403", "details": "details", "requestId": "xxx"},
        status=403,
    )
    source = SourceAmazonAds()
    streams = source.streams(config)
    campaigns_stream = get_stream_by_name(streams, "sponsored_display_campaigns")

    campaigns_records = get_all_stream_records(campaigns_stream)
    assert campaigns_records == []


@pytest.mark.parametrize(
    ("stream_name", "endpoint"),
    [
        ("sponsored_display_ad_groups", "sd/adGroups"),
        ("sponsored_display_product_ads", "sd/productAds"),
        ("sponsored_display_targetings", "sd/targets"),
        ("sponsored_display_creatives", "sd/creatives"),
    ],
)
@responses.activate
def test_streams_displays(
    config, stream_name, endpoint, profiles_response, adgroups_response, targeting_response, product_ads_response, creatives_response
):
    setup_responses(
        profiles_response=profiles_response,
        adgroups_response=adgroups_response,
        targeting_response=targeting_response,
        product_ads_response=product_ads_response,
        creatives_response=creatives_response,
    )

    source = SourceAmazonAds()
    streams = source.streams(config)
    test_stream = get_stream_by_name(streams, stream_name)

    records = get_all_stream_records(test_stream)
    assert len(records) == 4
    schema = test_stream.get_json_schema()
    for r in records:
        validate(schema=schema, instance=r)
    assert any([endpoint in call.request.url for call in responses.calls])


@pytest.mark.parametrize(
    ("stream_name", "endpoint"),
    [
        ("sponsored_brands_campaigns", "sb/v4/campaigns/list"),
        ("sponsored_brands_ad_groups", "sb/v4/adGroups/list"),
        ("sponsored_brands_keywords", "sb/keywords"),
        ("sponsored_product_campaigns", "sp/campaigns/list"),
        ("sponsored_product_ad_groups", "sp/adGroups/list"),
        ("sponsored_product_keywords", "sp/keywords/list"),
        ("sponsored_product_negative_keywords", "sp/negativeKeywords/list"),
        ("sponsored_product_ads", "sp/productAds/list"),
        ("sponsored_product_targetings", "sp/targets/list"),
    ],
)
@responses.activate
def test_streams_brands_and_products(config, stream_name, endpoint, profiles_response):
    if endpoint != "sb/keywords":
        setup_responses(profiles_response=profiles_response, post_response=endpoint)
    else:
        setup_responses(profiles_response=profiles_response, generic_response=endpoint)

    source = SourceAmazonAds()
    streams = source.streams(config)
    test_stream = get_stream_by_name(streams, stream_name)

    records = get_all_stream_records(test_stream)
    assert records == []
    assert any([endpoint in call.request.url for call in responses.calls])


@responses.activate
def test_sponsored_product_ad_group_bid_recommendations_404_error(caplog, config, profiles_response):
    setup_responses(profiles_response=profiles_response)
    responses.add(
        responses.POST,
        "https://advertising-api.amazon.com/sp/targets/bid/recommendations",
        json={
            "code": "404",
            "details": "404 Either the specified ad group identifier was not found or the specified ad group was found but no associated bid was found.",
        },
        status=404,
    )
    source = SourceAmazonAds()
    streams = source.streams(config)
    test_stream = get_stream_by_name(streams, "sponsored_product_ad_group_bid_recommendations")
    records = get_all_stream_records(test_stream, stream_slice={"campaignId": "1231", "adGroupId": "xxx"})
    assert records == []
    assert "Skip current AdGroup because the specified ad group has no associated bid" in caplog.text
