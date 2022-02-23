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


def get_all_specs_params():
    with open(SOURCE_SPECS, "r") as f:
        source_specs = yaml.load(f, yaml.FullLoader)
    with open(DESTINATION_SPECS, "r") as f:
        destination_specs = yaml.load(f, yaml.FullLoader)
    return [pytest.param("source", spec, id=spec["dockerImage"]) for spec in source_specs] + [
        pytest.param("destination", spec, id=spec["dockerImage"]) for spec in destination_specs
    ]


@pytest.mark.parametrize("spec_type, spec", get_all_specs_params())
def test_render_spec(spec_type, spec, octavia_project_directory, mocker):
    renderer = ConnectionSpecificationRenderer(
        resource_name=f"resource-{spec['dockerImage']}",
        definition=mocker.Mock(
            type=spec_type,
            id="foo",
            docker_repository=spec["dockerImage"].split(":")[0],
            docker_image_tag=spec["dockerImage"].split(":")[-1],
            documentation_url=spec["spec"]["documentationUrl"],
            specification=mocker.Mock(connection_specification=spec["spec"]["connectionSpecification"]),
        ),
    )
    output_path = renderer.write_yaml(octavia_project_directory)
    with open(output_path, "r") as f:
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


def pytest_generate_tests(metafunc):
    if "stringinput" in metafunc.fixturenames:
        metafunc.parametrize("stringinput", metafunc.config.getoption("stringinput"))


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
