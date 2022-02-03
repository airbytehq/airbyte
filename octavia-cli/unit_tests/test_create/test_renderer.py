#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
import yaml

SOURCE_SPECS = "../airbyte-config/init/src/main/resources/seed/source_specs.yaml"

import os
from tempfile import TemporaryDirectory

from octavia_cli.create.renderer import SpecRenderer


@pytest.fixture
def octavia_project_directory():
    os.mkdir("octavia_specs")
    os.mkdir("octavia_specs/sources")
    os.mkdir("octavia_specs/destinations")
    return "octavia_specs"


def test_source_specs(octavia_project_directory):
    with open(SOURCE_SPECS, "r") as f:
        source_specs = yaml.load(f, yaml.FullLoader)
    rendered_sources = []
    for i, source_spec in enumerate(source_specs):
        renderer = SpecRenderer(
            f"source-{i}",
            "source",
            f"id-{i}",
            source_spec["dockerImage"],
            source_spec["dockerImage"].split(":")[-1],
            source_spec["spec"]["documentationUrl"],
            source_spec["spec"]["connectionSpecification"],
        )
        output_path = renderer.write_yaml(octavia_project_directory)
        rendered_sources.append(output_path)
    assert len(rendered_sources) == len(source_specs)
    for source_file in rendered_sources:
        with open(source_file, "r") as f:
            source = yaml.load(f, yaml.FullLoader)
            assert all(
                [
                    expected_field in source
                    for expected_field in ["definition_type", "definition_id", "definition_image", "definition_version", "configuration"]
                ]
            )
