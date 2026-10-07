# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

from airbyte_cdk.sources.declarative.models import HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


CONNECTOR_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("region, host", [("nl", "data.castoredc.com"), ("uk", "uk.castoredc.com"), ("us", "us.castoredc.com")])
def test_regional_api_and_oauth_hosts(region, host):
    manifest = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())
    metadata = yaml.safe_load((CONNECTOR_DIR / "metadata.yaml").read_text())
    requester = ModelToComponentFactory().create_component(
        model_type=HttpRequester,
        component_definition=manifest["definitions"]["base_requester"],
        config={"url_region": region, "client_id": "test-client", "client_secret": "test-secret"},
        name="test_stream",
    )

    api_url = requester.get_url_base()
    token_url = requester.authenticator.get_token_refresh_endpoint()
    assert api_url == f"https://{host}/api/"
    assert token_url == f"https://{host}/oauth/token"
    assert requester.authenticator.get_grant_type() == "client_credentials"
    for url in (api_url, token_url):
        assert urlparse(url).hostname in metadata["data"]["allowedHosts"]["hosts"]


def test_region_configuration_remains_compatible():
    manifest = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())
    region = manifest["spec"]["connection_specification"]["properties"]["url_region"]

    assert region["enum"] == ["uk", "nl", "us"]
    assert region["default"] == "uk"
