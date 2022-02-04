#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
import yaml
from octavia_cli.create.renderer import SpecRenderer
from octavia_cli.init.commands import DIRECTORIES_TO_CREATE

SOURCE_SPECS = "../airbyte-config/init/src/main/resources/seed/source_specs.yaml"
DESTINATION_SPECS = "../airbyte-config/init/src/main/resources/seed/destination_specs.yaml"


@pytest.fixture
def octavia_project_directory(tmpdir):
    for directory in DIRECTORIES_TO_CREATE:
        tmpdir.mkdir(directory)
    return tmpdir


@pytest.mark.integration
@pytest.mark.parametrize("spec_type, spec_file_path", [("source", SOURCE_SPECS), ("destination", DESTINATION_SPECS)])
def test_rendering_specs(spec_type, spec_file_path, octavia_project_directory):
    """[summary]

    Args:
        spec_type ([type]): [description]
        spec_file_path ([type]): [description]
        octavia_project_directory ([type]): [description]
    """
    with open(spec_file_path, "r") as f:
        specs = yaml.load(f, yaml.FullLoader)
    rendered_specs = []
    for i, spec in enumerate(specs):
        renderer = SpecRenderer(
            f"{spec_type}-{i}",
            spec_type,
            f"id-{i}",
            spec["dockerImage"],
            spec["dockerImage"].split(":")[-1],
            spec["spec"]["documentationUrl"],
            spec["spec"]["connectionSpecification"],
        )
        output_path = renderer.write_yaml(octavia_project_directory)
        rendered_specs.append(output_path)
    assert len(rendered_specs) == len(specs)
    for source_file in rendered_specs:
        with open(source_file, "r") as f:
            source = yaml.load(f, yaml.FullLoader)
            assert all(
                [
                    expected_field in source
                    for expected_field in ["definition_type", "definition_id", "definition_image", "definition_version", "configuration"]
                ]
            )
