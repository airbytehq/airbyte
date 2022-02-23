#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import filecmp
import os

import pytest
import yaml
from octavia_cli.generate.renderer import ConnectionSpecificationRenderer

pytestmark = pytest.mark.integration
SOURCE_SPECS = "../airbyte-config/init/src/main/resources/seed/source_specs.yaml"
DESTINATION_SPECS = "../airbyte-config/init/src/main/resources/seed/destination_specs.yaml"


@pytest.mark.parametrize("spec_type, spec_file_path", [("source", SOURCE_SPECS), ("destination", DESTINATION_SPECS)])
def test_rendering_all_specs(spec_type, spec_file_path, octavia_project_directory, mocker):
    with open(spec_file_path, "r") as f:
        specs = yaml.load(f, yaml.FullLoader)
    rendered_specs = []
    for i, spec in enumerate(specs):
        renderer = ConnectionSpecificationRenderer(
            resource_name=f"resource-{i}",
            definition=mocker.Mock(
                type=spec_type,
                id=i,
                docker_repository=spec["dockerImage"].split(":")[0],
                docker_image_tag=spec["dockerImage"].split(":")[-1],
                documentation_url=spec["spec"]["documentationUrl"],
                specification=mocker.Mock(connection_specification=spec["spec"]["connectionSpecification"]),
            ),
        )
        output_path = renderer.write_yaml(octavia_project_directory)
        rendered_specs.append(output_path)
    assert len(rendered_specs) == len(specs)
    for rendered_spec in rendered_specs:
        with open(rendered_spec, "r") as f:
            parsed_yaml = yaml.load(f, yaml.FullLoader)
            assert all(
                [
                    expected_field in parsed_yaml
                    for expected_field in [
                        "resource_name",
                        "definition_type",
                        "definition_id",
                        "definition_image",
                        "definition_version",
                        "configuration",
                    ]
                ]
            )


EXPECTED_RENDERED_YAML_PATH = "tests/integration/test_generate/expected_rendered_yaml"


@pytest.mark.parametrize(
    "resource_name, spec_type, input_spec_path, expected_yaml_path",
    [
        ("my_postgres_source", "source", "source_postgres/input_spec.yaml", "source_postgres/expected.yaml"),
        ("my_postgres_destination", "destination", "destination_postgres/input_spec.yaml", "destination_postgres/expected.yaml"),
        ("my_s3_destination", "destination", "destination_s3/input_spec.yaml", "destination_s3/expected.yaml"),
    ],
)
def test_expected_output(resource_name, spec_type, input_spec_path, expected_yaml_path, octavia_project_directory, mocker):
    with open(os.path.join(EXPECTED_RENDERED_YAML_PATH, input_spec_path), "r") as f:
        input_spec = yaml.load(f, yaml.FullLoader)
    renderer = ConnectionSpecificationRenderer(
        resource_name=resource_name,
        definition=mocker.Mock(
            type=spec_type,
            id="foobar",
            docker_repository=input_spec["dockerImage"].split(":")[0],
            docker_image_tag=input_spec["dockerImage"].split(":")[-1],
            documentation_url=input_spec["spec"]["documentationUrl"],
            specification=mocker.Mock(connection_specification=input_spec["spec"]["connectionSpecification"]),
        ),
    )
    output_path = renderer.write_yaml(octavia_project_directory)
    expect_output_path = os.path.join(EXPECTED_RENDERED_YAML_PATH, expected_yaml_path)
    assert filecmp.cmp(output_path, expect_output_path)
