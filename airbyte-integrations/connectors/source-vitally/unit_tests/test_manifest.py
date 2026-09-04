# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"


def _load_spec_properties():
    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)
    return manifest["spec"]["connection_specification"]["properties"]


def test_secret_token_has_airbyte_secret_flag():
    props = _load_spec_properties()
    secret_token = props["secret_token"]
    assert (
        secret_token.get("airbyte_secret") is True
    ), "secret_token must have airbyte_secret: true so the value is masked in the UI and logs"


def test_basic_auth_header_has_airbyte_secret_flag():
    props = _load_spec_properties()
    basic_auth_header = props["basic_auth_header"]
    assert basic_auth_header.get("airbyte_secret") is True, "basic_auth_header must have airbyte_secret: true"
