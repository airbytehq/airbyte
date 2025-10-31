#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import yaml
import pytest
from pathlib import Path
from orchestrator.assets.registry_entry import metadata_to_registry_entry
from orchestrator.models.metadata import LatestMetadataEntry, MetadataDefinition


@pytest.mark.parametrize(
    ("input_metadata_filepath", "expected_docker_image_tag"),
    [
        # For release candidates we return the rc docker image tag, whether or not there are overrides.
        # The override that was present on the registry entry for the latest connector will still be in effect as the default version.
        ("fixtures/metadata_airbyte_source-faker_release_candidate_metadata.yaml", "6.2.26-rc.1"),
        ("fixtures/metadata_airbyte_source-faker_release_candidate_with_overrides_metadata.yaml", "6.2.26-rc.1"),
        # No override so we return the docker image tag that was set
        ("fixtures/metadata_airbyte_source-faker_non-release-candidate_metadata.yaml", "6.2.25"),
        # Not a release candidate so we use the override docker image tag
        ("fixtures/metadata_airbyte_source-faker_non-release-candidate_with_overrides_metadata.yaml", "6.2.24"),
    ]
)
def test_metadata_to_registry_entry_rc_keeps_rc_version(input_metadata_filepath, expected_docker_image_tag):
    # Load the release candidate metadata
    rc_metadata_path = Path(__file__).parent / input_metadata_filepath

    with open(rc_metadata_path, "r") as f:
        rc_metadata_dict = yaml.safe_load(f)

    # The yaml file represents the metadata file, which has a top level "data" key
    metadata_data = rc_metadata_dict["data"]

    # Remove the invalid "registries" field
    if "registries" in metadata_data:
        del metadata_data["registries"]

    # Create a MetadataDefinition object, which has a top level "data" key
    # and a "metadataSpecVersion" key
    metadata_definition = MetadataDefinition(
        metadataSpecVersion="1.0",
        data=metadata_data
    )

    # Create a LatestMetadataEntry object
    latest_metadata_entry = LatestMetadataEntry(
        metadata_definition=metadata_definition,
        icon_blob=None, # Not needed for this test
        icon_url="", # Not needed for this test
        bucket_name="test_bucket",
        file_path="test/path/release_candidate/metadata.yaml",
        etag="test_etag",
        last_modified="2024-01-01",
    )

    # Call the function under test
    registry_entry_dict = metadata_to_registry_entry(latest_metadata_entry, "cloud")

    # Assert that the dockerIm ageTag is the release candidate version
    assert registry_entry_dict["dockerImageTag"] == expected_docker_image_tag
