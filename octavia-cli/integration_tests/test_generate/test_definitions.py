#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
from octavia_cli.generate.commands import generate_source_or_destination

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ("definition_type, definition_id, resource_name"),
    [
        ("source", "6371b14b-bc68-4236-bfbd-468e8df8e968", "test_generate_source"),
        ("destination", "22f6c74f-5699-40ff-833c-4a879ea40133", "test_generate_destination"),
    ],
)
def test_generate_source_or_destination(
    octavia_tmp_project_directory, api_client, workspace_id, definition_type, definition_id, resource_name
):
    current_path = os.getcwd()
    os.chdir(octavia_tmp_project_directory)
    generate_source_or_destination(definition_type, api_client, workspace_id, definition_id, resource_name)
    expected_output_path = f"{definition_type}s/{resource_name}/configuration.yaml"
    with open(expected_output_path, "r") as f:
        parsed_yaml = yaml.safe_load(f)
        assert parsed_yaml["resource_name"] == resource_name
        assert parsed_yaml["definition_type"] == definition_type
        assert parsed_yaml["definition_id"] == definition_id
    os.chdir(current_path)
