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


@pytest.fixture(scope="module")
def refresh_token_updater(manifest):
    return RefreshTokenUpdater.parse_obj(manifest["definitions"]["authenticator"]["refresh_token_updater"])


def _spec_property(manifest, path):
    node = manifest["spec"]["connection_specification"]
    for key in path:
        node = node.get("properties", {}).get(key)
        if node is None:
            return None
    return node


def test_access_token_written_back_by_the_authenticator_is_a_hidden_secret(manifest, refresh_token_updater):
    access_token_path = refresh_token_updater.access_token_config_path

    declared = _spec_property(manifest, access_token_path)

    assert declared is not None, f"{access_token_path} is written back to the config but not declared in the spec, so it is not masked"
    assert declared.get("airbyte_secret") is True
    assert declared.get("airbyte_hidden") is True


def test_token_expiry_date_written_back_by_the_authenticator_is_hidden(manifest, refresh_token_updater):
    declared = _spec_property(manifest, refresh_token_updater.token_expiry_date_config_path)

    assert declared is not None
    assert declared.get("airbyte_hidden") is True
