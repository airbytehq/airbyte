# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for two stream properties the HubSpot API returns but the schemas used to omit.

V2 destinations materialise exactly the declared stream schema: an undeclared property is
dropped and does not appear in `_airbyte_meta.changes[]`, so the loss is silent. These tests
pin the two declarations, and pin them as *nullable* like every sibling, so that neither the
declaration nor its backward-compatible nullability can be dropped without a test failing.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="module")
def manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


@pytest.fixture(scope="module")
def marketing_emails_testing(manifest: dict) -> dict:
    return manifest["schemas"]["marketing_emails"]["properties"]["testing"]["properties"]


@pytest.fixture(scope="module")
def owners_team(manifest: dict) -> dict:
    return manifest["schemas"]["owners"]["properties"]["teams"]["items"]["properties"]


def test_marketing_emails_declares_testing_is_ab_variation(marketing_emails_testing: dict) -> None:
    assert "isAbVariation" in marketing_emails_testing, (
        "`marketing_emails.testing.isAbVariation` is returned by /marketing/v3/emails; without the "
        "declaration a V2 destination drops it silently"
    )
    assert marketing_emails_testing["isAbVariation"]["type"] == ["null", "boolean"]


def test_owners_declares_team_primary(owners_team: dict) -> None:
    assert (
        "primary" in owners_team
    ), "`owners.teams[].primary` is returned by the Owners API; without the declaration a V2 destination drops it silently"
    assert owners_team["primary"]["type"] == ["null", "boolean"]


@pytest.mark.parametrize(
    "fixture_name, added_property",
    [
        ("marketing_emails_testing", "isAbVariation"),
        ("owners_team", "primary"),
    ],
)
def test_added_property_is_nullable_like_its_siblings(fixture_name: str, added_property: str, request) -> None:
    """A non-nullable addition would break existing connections; every sibling is nullable."""
    properties = request.getfixturevalue(fixture_name)
    assert added_property in properties, f"{added_property} is not declared"
    siblings = {name: spec for name, spec in properties.items() if name != added_property}
    assert siblings, f"expected {added_property} to have siblings to compare against"

    non_nullable = [name for name, spec in siblings.items() if "null" not in spec["type"]]
    assert non_nullable == [], f"unexpected non-nullable siblings: {non_nullable}"
    assert "null" in properties[added_property]["type"]
