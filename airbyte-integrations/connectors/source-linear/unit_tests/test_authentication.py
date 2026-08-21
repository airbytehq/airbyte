#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for source-linear authentication configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"


def _manifest() -> Mapping[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def test_oauth_is_the_default_authentication_method() -> None:
    manifest = _manifest()
    spec = manifest["spec"]
    branches = spec["connection_specification"]["properties"]["credentials"]["oneOf"]

    assert [branch["title"] for branch in branches] == ["OAuth2.0", "API Key"]
    assert branches[0]["properties"]["auth_type"]["const"] == spec["advanced_auth"]["predicate_value"]


def test_authentication_branches_have_matching_authenticators() -> None:
    manifest = _manifest()
    spec = manifest["spec"]
    branches = spec["connection_specification"]["properties"]["credentials"]["oneOf"]
    authenticators = manifest["definitions"]["base_requester"]["authenticator"]["authenticators"]

    assert {"OAuth2.0", "API Key"} <= authenticators.keys()
    assert all(branch["properties"]["auth_type"]["const"] in authenticators for branch in branches)
