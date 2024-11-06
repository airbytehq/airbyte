#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import responses
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConnectorSpecification, Status, Type
from jsonschema import Draft4Validator
from source_amazon_ads import SourceAmazonAds

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
