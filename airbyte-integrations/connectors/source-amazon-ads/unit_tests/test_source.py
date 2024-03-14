#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import responses
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConnectorSpecification, Status, Type
from jsonschema import Draft4Validator
from source_amazon_ads import SourceAmazonAds
from source_amazon_ads.declarative_source_adapter import DeclarativeSourceAdapter
from source_amazon_ads.schemas import Profile

from .utils import command_check, url_strip_query


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "alala", "expires_in": 10},
    )
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/v2/profiles",
        json=[{"profileId": 111, "timezone": "gtm", "accountInfo": {"marketplaceStringId": "mkt_id_1", "id": "111", "type": "vendor"}}],
    )


def ensure_additional_property_is_boolean(root):
    for name, prop in root.get("properties", {}).items():
        if prop["type"] == "array" and "items" in prop:
            ensure_additional_property_is_boolean(prop["items"])
        if prop["type"] == "object" and "properties" in prop:
            ensure_additional_property_is_boolean(prop)
    if "additionalProperties" in root:
        assert type(root["additionalProperties"]) == bool, (
            f"`additionalProperties` expected to be of 'bool' type. " f"Got: {type(root['additionalProperties']).__name__}"
        )


@responses.activate
def test_discover(config):
    setup_responses()
    source = DeclarativeSourceAdapter(source=SourceAmazonAds())
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        Draft4Validator.check_schema(schema)
        ensure_additional_property_is_boolean(schema)


def test_spec():
    source = DeclarativeSourceAdapter(source=SourceAmazonAds())
    spec = source.spec(None)
    assert isinstance(spec, ConnectorSpecification)


@responses.activate
def test_check(config_gen):
    setup_responses()
    source = DeclarativeSourceAdapter(source=SourceAmazonAds())

    assert command_check(source, config_gen(start_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 2

    assert command_check(source, config_gen(start_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 4

    assert source.check(None, config_gen(start_date="2022-02-20")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 6

    assert command_check(source, config_gen(start_date="2022-20-02")) == AirbyteConnectionStatus(
        status=Status.FAILED, message="'month must be in 1..12'"
    )
    assert len(responses.calls) == 6

    assert command_check(source, config_gen(start_date="no date")) == AirbyteConnectionStatus(
        status=Status.FAILED, message="'String does not match format YYYY-MM-DD'"
    )
    assert len(responses.calls) == 6

    assert command_check(source, config_gen(region=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 8
    assert url_strip_query(responses.calls[7].request.url) == "https://advertising-api.amazon.com/v2/profiles"

    assert command_check(source, config_gen(look_back_window=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)


@responses.activate
def test_source_streams(config):
    setup_responses()
    source = DeclarativeSourceAdapter(source=SourceAmazonAds())
    streams = source.streams(config)
    assert len(streams) == 29
    actual_stream_names = {stream.name for stream in streams}
    expected_stream_names = {
        "profiles",
        "portfolios",
        "sponsored_display_campaigns",
        "sponsored_product_campaigns",
        "sponsored_product_ad_groups",
        "sponsored_product_ad_group_suggested_keywords",
        "sponsored_product_ad_group_bid_recommendations",
        "sponsored_product_keywords",
        "sponsored_product_negative_keywords",
        "sponsored_product_campaign_negative_keywords",
        "sponsored_product_ads",
        "sponsored_product_targetings",
        "sponsored_products_report_stream",
        "sponsored_brands_campaigns",
        "sponsored_brands_ad_groups",
        "sponsored_brands_keywords",
        "sponsored_brands_report_stream",
        "attribution_report_performance_adgroup",
        "attribution_report_performance_campaign",
        "attribution_report_performance_creative",
        "attribution_report_products",
        "sponsored_display_budget_rules",
    }
    assert not expected_stream_names - actual_stream_names


def test_filter_profiles_exist():
    source = SourceAmazonAds()
    mock_objs = [
        {"profileId": 111, "timezone": "gtm", "accountInfo": {"marketplaceStringId": "mkt_id_1", "id": "111", "type": "vendor"}},
        {"profileId": 222, "timezone": "gtm", "accountInfo": {"marketplaceStringId": "mkt_id_2", "id": "222", "type": "vendor"}},
        {"profileId": 333, "timezone": "gtm", "accountInfo": {"marketplaceStringId": "mkt_id_3", "id": "333", "type": "vendor"}},
    ]

    mock_profiles = [Profile.parse_obj(profile) for profile in mock_objs]

    filtered_profiles = source._choose_profiles({}, mock_profiles)
    assert len(filtered_profiles) == 3

    filtered_profiles = source._choose_profiles({"profiles": [111]}, mock_profiles)
    assert len(filtered_profiles) == 1
    assert filtered_profiles[0].profileId == 111

    filtered_profiles = source._choose_profiles({"profiles": [111, 333]}, mock_profiles)
    assert len(filtered_profiles) == 2

    filtered_profiles = source._choose_profiles({"profiles": [444]}, mock_profiles)
    assert len(filtered_profiles) == 0

    filtered_profiles = source._choose_profiles({"marketplace_ids": ["mkt_id_4"]}, mock_profiles)
    assert len(filtered_profiles) == 0

    filtered_profiles = source._choose_profiles({"marketplace_ids": ["mkt_id_1"]}, mock_profiles)
    assert len(filtered_profiles) == 1
    assert filtered_profiles[0].accountInfo.marketplaceStringId == "mkt_id_1"

    filtered_profiles = source._choose_profiles({"marketplace_ids": ["mkt_id_1", "mkt_id_3"]}, mock_profiles)
    assert len(filtered_profiles) == 2

    filtered_profiles = source._choose_profiles({"profiles": [111], "marketplace_ids": ["mkt_id_2"]}, mock_profiles)
    assert len(filtered_profiles) == 2

    filtered_profiles = source._choose_profiles({"profiles": [111], "marketplace_ids": ["mkt_id_1"]}, mock_profiles)
    assert len(filtered_profiles) == 1
    assert filtered_profiles[0].profileId == 111
