# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for stream properties the HubSpot API returns but the schemas used to omit.

Schematizing destinations (S3/GCS with Avro or Parquet output) build records strictly from
the declared stream schema: an undeclared property is dropped and does not appear in
`_airbyte_meta.changes[]`, so the loss is silent. These tests pin the declarations, and pin
them as *nullable* like every sibling, so that neither the declaration nor its
backward-compatible nullability can be dropped without a test failing.
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


@pytest.fixture(scope="module")
def owners_archived_team(manifest: dict) -> dict:
    return manifest["schemas"]["owners_archived"]["properties"]["teams"]["items"]["properties"]


def test_marketing_emails_declares_testing_is_ab_variation(marketing_emails_testing: dict) -> None:
    assert "isAbVariation" in marketing_emails_testing, (
        "`marketing_emails.testing.isAbVariation` is returned by /marketing/v3/emails; without the "
        "declaration a schematizing destination (S3/GCS Avro/Parquet) drops it silently"
    )
    assert marketing_emails_testing["isAbVariation"]["type"] == ["null", "boolean"]


@pytest.mark.parametrize("fixture_name", ["owners_team", "owners_archived_team"])
def test_owners_declares_team_primary(fixture_name: str, request) -> None:
    team = request.getfixturevalue(fixture_name)
    assert "primary" in team, (
        "`teams[].primary` is returned by the Owners API for both active and archived owners; "
        "without the declaration a schematizing destination (S3/GCS Avro/Parquet) drops it silently"
    )
    assert team["primary"]["type"] == ["null", "boolean"]


@pytest.mark.parametrize(
    "fixture_name, added_property",
    [
        ("marketing_emails_testing", "isAbVariation"),
        ("owners_team", "primary"),
        ("owners_archived_team", "primary"),
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


@pytest.fixture(scope="module")
def engagements_task_pipelines_stage(manifest: dict) -> dict:
    return manifest["schemas"]["engagements_task_pipelines"]["properties"]["stages"]["items"]["properties"]


def test_task_pipeline_stage_id_is_a_string(engagements_task_pipelines_stage: dict) -> None:
    """`stages[].id` is the join key against `engagements_tasks.properties.hs_pipeline_stage`.

    HubSpot's default task stages use UUIDs, but stages created later in the UI get numeric ids
    (for example `5996839954`). Narrowing this to an integer would make numeric ids type-mismatch
    against `hs_pipeline_stage`, which HubSpot always returns as a string, and silently break the join.
    """
    assert engagements_task_pipelines_stage["id"]["type"] == ["null", "string"]


def test_task_pipeline_stage_metadata_values_are_strings(engagements_task_pipelines_stage: dict) -> None:
    """Task stages carry the open/closed flag as `state`, not the `ticketState` that ticket stages use.

    Both flags come back as strings rather than native booleans or enums. `state` is the only thing
    that says whether a task in the stage counts as done, so leaving it undeclared would drop it
    silently on a schematizing destination and defeat the point of the stream.
    """
    metadata = engagements_task_pipelines_stage["metadata"]
    assert metadata["additionalProperties"] is True, (
        "HubSpot's task stage `metadata` keys are not fully documented; keeping the object open "
        "prevents a schematizing destination from silently dropping an undeclared flag"
    )
    for key in ("isClosed", "state"):
        assert metadata["properties"][key]["type"] == ["null", "string"]
