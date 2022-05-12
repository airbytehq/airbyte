#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import filecmp
import os

import pytest
import yaml
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.airbyte_stream import AirbyteStream
from airbyte_api_client.model.airbyte_stream_and_configuration import AirbyteStreamAndConfiguration
from airbyte_api_client.model.airbyte_stream_configuration import AirbyteStreamConfiguration
from airbyte_api_client.model.destination_sync_mode import DestinationSyncMode
from airbyte_api_client.model.sync_mode import SyncMode
from octavia_cli.generate.renderers import ConnectionRenderer, ConnectorSpecificationRenderer

pytestmark = pytest.mark.integration

SOURCE_SPECS = "../airbyte-config/init/src/main/resources/seed/source_specs.yaml"
DESTINATION_SPECS = "../airbyte-config/init/src/main/resources/seed/destination_specs.yaml"


def get_all_specs_params():
    with open(SOURCE_SPECS, "r") as f:
        source_specs = yaml.safe_load(f)
    with open(DESTINATION_SPECS, "r") as f:
        destination_specs = yaml.safe_load(f)
    return [pytest.param("source", spec, id=spec["dockerImage"]) for spec in source_specs] + [
        pytest.param("destination", spec, id=spec["dockerImage"]) for spec in destination_specs
    ]


@pytest.mark.parametrize("spec_type, spec", get_all_specs_params())
def test_render_spec(spec_type, spec, octavia_tmp_project_directory, mocker):
    renderer = ConnectorSpecificationRenderer(
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
    output_path = renderer.write_yaml(octavia_tmp_project_directory)
    with open(output_path, "r") as f:
        parsed_yaml = yaml.safe_load(f)
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


EXPECTED_RENDERED_YAML_PATH = f"{os.path.dirname(__file__)}/expected_rendered_yaml"


@pytest.mark.parametrize(
    "resource_name, spec_type, input_spec_path, expected_yaml_path",
    [
        ("my_postgres_source", "source", "source_postgres/input_spec.yaml", "source_postgres/expected.yaml"),
        ("my_postgres_destination", "destination", "destination_postgres/input_spec.yaml", "destination_postgres/expected.yaml"),
        ("my_s3_destination", "destination", "destination_s3/input_spec.yaml", "destination_s3/expected.yaml"),
    ],
)
def test_expected_output_connector_specification_renderer(
    resource_name, spec_type, input_spec_path, expected_yaml_path, octavia_tmp_project_directory, mocker
):
    with open(os.path.join(EXPECTED_RENDERED_YAML_PATH, input_spec_path), "r") as f:
        input_spec = yaml.safe_load(f)
    renderer = ConnectorSpecificationRenderer(
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
    output_path = renderer.write_yaml(octavia_tmp_project_directory)
    expect_output_path = os.path.join(EXPECTED_RENDERED_YAML_PATH, expected_yaml_path)
    assert filecmp.cmp(output_path, expect_output_path)


@pytest.mark.parametrize(
    "enable_normalization, expected_yaml_path",
    [
        (False, "connection/expected.yaml"),
        (True, "connection/expected_with_normalization.yaml"),
    ],
)
def test_expected_output_connection_renderer(octavia_tmp_project_directory, mocker, enable_normalization, expected_yaml_path):
    stream = AirbyteStream(default_cursor_field=["foo"], json_schema={}, name="my_stream", supported_sync_modes=[SyncMode("full_refresh")])
    config = AirbyteStreamConfiguration(
        alias_name="pokemon", selected=True, destination_sync_mode=DestinationSyncMode("append"), sync_mode=SyncMode("full_refresh")
    )
    catalog = AirbyteCatalog([AirbyteStreamAndConfiguration(stream=stream, config=config)])
    mock_source = mocker.Mock(resource_id="my_source_id", catalog=catalog)
    mock_destination = mocker.Mock(resource_id="my_destination_id")

    renderer = ConnectionRenderer("my_new_connection", mock_source, mock_destination, enable_normalization)
    output_path = renderer.write_yaml(octavia_tmp_project_directory)
    expect_output_path = os.path.join(EXPECTED_RENDERED_YAML_PATH, expected_yaml_path)
    assert filecmp.cmp(output_path, expect_output_path)
