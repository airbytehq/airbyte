#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses
from airbyte_cdk import AirbyteTracedException
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


