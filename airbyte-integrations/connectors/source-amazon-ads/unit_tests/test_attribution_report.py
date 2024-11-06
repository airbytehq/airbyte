#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
import responses
from jsonschema import validate
from source_amazon_ads import SourceAmazonAds

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
