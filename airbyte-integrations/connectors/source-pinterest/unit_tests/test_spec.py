#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import RefreshTokenUpdater


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _refresh_token_updater(manifest):
    # Parsed through the CDK model so unset config paths resolve to the CDK's own defaults.
    return RefreshTokenUpdater.parse_obj(manifest["definitions"]["authenticator"]["refresh_token_updater"])


def _spec_property(manifest, path):
    node = manifest["spec"]["connection_specification"]
    for key in path:
        node = node.get("properties", {}).get(key)
        if node is None:
            return None
    return node


def test_access_token_written_back_by_the_authenticator_is_declared_as_a_secret(manifest):
    access_token_path = _refresh_token_updater(manifest).access_token_config_path

    declared = _spec_property(manifest, access_token_path)

    assert declared is not None, f"{access_token_path} is written back to the config but not declared in the spec, so it is not masked"
    assert declared.get("airbyte_secret") is True


def test_token_expiry_date_written_back_by_the_authenticator_is_declared(manifest):
    expiry_path = _refresh_token_updater(manifest).token_expiry_date_config_path

    assert _spec_property(manifest, expiry_path) is not None
