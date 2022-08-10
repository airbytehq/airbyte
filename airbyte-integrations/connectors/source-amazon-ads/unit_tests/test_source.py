#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import responses
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConnectorSpecification, Status, Type
from jsonschema import Draft4Validator
from source_amazon_ads import SourceAmazonAds


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "alala", "expires_in": 10},
    )
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/v2/profiles",
        json=[],
    )


@responses.activate
def test_discover(config):
    setup_responses()
    source = SourceAmazonAds()
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        Draft4Validator.check_schema(schema)


def test_spec():
    source = SourceAmazonAds()
    spec = source.spec(None)
    assert isinstance(spec, ConnectorSpecification)


@responses.activate
def test_check(config):
    setup_responses()
    source = SourceAmazonAds()
    assert source.check(None, config) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 2


@responses.activate
def test_source_streams(config):
    setup_responses()
    source = SourceAmazonAds()
    streams = source.streams(config)
    assert len(streams) == 18
    actual_stream_names = {stream.name for stream in streams}
    expected_stream_names = set(
        [
            "profiles",
            "sponsored_display_campaigns",
            "sponsored_product_campaigns",
            "sponsored_product_ad_groups",
            "sponsored_product_keywords",
            "sponsored_product_negative_keywords",
            "sponsored_product_ads",
            "sponsored_product_targetings",
            "sponsored_products_report_stream",
            "sponsored_brands_campaigns",
            "sponsored_brands_ad_groups",
            "sponsored_brands_keywords",
            "sponsored_brands_report_stream",
        ]
    )
    assert not expected_stream_names - actual_stream_names
