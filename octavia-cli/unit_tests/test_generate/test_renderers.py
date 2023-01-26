#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.airbyte_stream import AirbyteStream
from airbyte_api_client.model.airbyte_stream_and_configuration import AirbyteStreamAndConfiguration
from airbyte_api_client.model.airbyte_stream_configuration import AirbyteStreamConfiguration
from airbyte_api_client.model.destination_sync_mode import DestinationSyncMode
from airbyte_api_client.model.sync_mode import SyncMode
from octavia_cli.generate import renderers, yaml_dumpers


class TestFieldToRender:
    def test_init(self, mocker):
        mocker.patch.object(renderers.FieldToRender, "_get_one_of_values")
        mocker.patch.object(renderers, "get_object_fields")
        mocker.patch.object(renderers.FieldToRender, "_get_array_items")
        mocker.patch.object(renderers.FieldToRender, "_build_comment")
        mocker.patch.object(renderers.FieldToRender, "_get_default")

        field_metadata = mocker.Mock()
        field_to_render = renderers.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.name == "field_name"
        assert field_to_render.required
        assert field_to_render.field_metadata == field_metadata
        assert field_to_render.one_of_values == field_to_render._get_one_of_values.return_value
        assert field_to_render.object_properties == renderers.get_object_fields.return_value
        assert field_to_render.array_items == field_to_render._get_array_items.return_value
        assert field_to_render.comment == field_to_render._build_comment.return_value
        assert field_to_render.default == field_to_render._get_default.return_value
        field_to_render._build_comment.assert_called_with(
            [
                field_to_render._get_secret_comment,
                field_to_render._get_required_comment,
                field_to_render._get_type_comment,
                field_to_render._get_description_comment,
                field_to_render._get_example_comment,
            ]
        )

    def test_get_attr(self):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render.foo == "bar"
        assert field_to_render.not_existing is None

    def test_is_array_of_objects(self):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = "array"
        field_to_render.items = {"type": "object"}
        assert field_to_render.is_array_of_objects
        field_to_render.type = "array"
        field_to_render.items = {"type": "int"}
        assert not field_to_render.is_array_of_objects

    def test__get_one_of_values(self, mocker):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.oneOf = False
        assert field_to_render._get_one_of_values() == []

        mocker.patch.object(renderers, "get_object_fields")
        one_of_value = mocker.Mock()
        field_to_render.oneOf = [one_of_value]
        one_of_values = field_to_render._get_one_of_values()
        renderers.get_object_fields.assert_called_once_with(one_of_value)
        assert one_of_values == [renderers.get_object_fields.return_value]

    def test__get_array_items(self, mocker):
        mocker.patch.object(renderers, "parse_fields")
        mocker.patch.object(renderers.FieldToRender, "is_array_of_objects", False)

        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render._get_array_items() == []
        field_to_render.items = {"required": [], "properties": []}
        mocker.patch.object(renderers.FieldToRender, "is_array_of_objects", True)
        assert field_to_render._get_array_items() == renderers.parse_fields.return_value
        renderers.parse_fields.assert_called_with([], [])

    def test__get_required_comment(self):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.required = True
        assert field_to_render._get_required_comment() == "REQUIRED"
        field_to_render.required = False
        assert field_to_render._get_required_comment() == "OPTIONAL"

    @pytest.mark.parametrize(
        "_type,expected_comment",
        [("string", "string"), (["string", "null"], "string, null"), (None, None)],
    )
    def test__get_type_comment(self, _type, expected_comment):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = _type
        assert field_to_render._get_type_comment() == expected_comment

    def test__get_secret_comment(self):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.airbyte_secret = True
        assert field_to_render._get_secret_comment() == "SECRET (please store in environment variables)"
        field_to_render.airbyte_secret = False
        assert field_to_render._get_secret_comment() is None

    def test__get_description_comment(self):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.description = "foo"
        assert field_to_render._get_description_comment() == "foo"
        field_to_render.description = None
        assert field_to_render._get_description_comment() is None

    @pytest.mark.parametrize(
        "examples_value,expected_output",
        [
            (["foo", "bar"], "Examples: foo, bar"),
            (["foo"], "Example: foo"),
            ("foo", "Example: foo"),
            ([5432], "Example: 5432"),
            (None, None),
        ],
    )
    def test__get_example_comment(self, examples_value, expected_output):
        field_to_render = renderers.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.examples = examples_value
        assert field_to_render._get_example_comment() == expected_output

    @pytest.mark.parametrize(
        "field_metadata,expected_default",
        [
            ({"const": "foo", "default": "bar"}, "foo"),
            ({"default": "bar"}, "bar"),
            ({"airbyte_secret": True}, "${FIELD_NAME}"),
            ({}, None),
        ],
    )
    def test__get_default(self, field_metadata, expected_default):
        field_to_render = renderers.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.default == expected_default

    def test__build_comment(self, mocker):
        comment_functions = [mocker.Mock(return_value="foo"), mocker.Mock(return_value=None), mocker.Mock(return_value="bar")]
        comment = renderers.FieldToRender._build_comment(comment_functions)
        assert comment == "foo | bar"


def test_parse_fields():
    required_fields = ["foo"]
    properties = {"foo": {}, "bar": {}}
    fields_to_render = renderers.parse_fields(required_fields, properties)
    assert fields_to_render[0].name == "foo"
    assert fields_to_render[0].required
    assert fields_to_render[1].name == "bar"
    assert not fields_to_render[1].required


def test_get_object_fields(mocker):
    mocker.patch.object(renderers, "parse_fields")
    field_metadata = {"properties": {"foo": {}, "bar": {}}, "required": ["foo"]}
    object_properties = renderers.get_object_fields(field_metadata)
    assert object_properties == renderers.parse_fields.return_value
    renderers.parse_fields.assert_called_with(["foo"], field_metadata["properties"])
    field_metadata = {}
    assert renderers.get_object_fields(field_metadata) == []


class TestBaseRenderer:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(renderers.BaseRenderer, "__abstractmethods__", set())

    def test_init(self, patch_base_class):
        base = renderers.BaseRenderer("resource_name")
        assert base.resource_name == "resource_name"

    def test_get_output_path(self, patch_base_class, mocker):
        mocker.patch.object(renderers, "os")
        mocker.patch.object(renderers, "slugify")
        renderers.os.path.exists.return_value = False
        spec_renderer = renderers.BaseRenderer("my_resource_name")
        renderers.os.path.join.side_effect = [
            "./my_definition_types/my_resource_name",
            "./my_definition_types/my_resource_name/configuration.yaml",
        ]
        output_path = spec_renderer.get_output_path(".", "my_definition_type", "my_resource_name")
        renderers.os.makedirs.assert_called_once()
        renderers.slugify.assert_called_with("my_resource_name", separator="_")
        renderers.os.path.join.assert_has_calls(
            [
                mocker.call(".", "my_definition_types", renderers.slugify.return_value),
                mocker.call("./my_definition_types/my_resource_name", "configuration.yaml"),
            ]
        )
        assert output_path == Path("./my_definition_types/my_resource_name/configuration.yaml")

    @pytest.mark.parametrize("file_exists, confirmed_overwrite", [(True, True), (False, None), (True, False)])
    def test__confirm_overwrite(self, mocker, file_exists, confirmed_overwrite):
        mock_output_path = mocker.Mock(is_file=mocker.Mock(return_value=file_exists))
        mocker.patch.object(renderers.click, "confirm", mocker.Mock(return_value=confirmed_overwrite))
        overwrite = renderers.BaseRenderer._confirm_overwrite(mock_output_path)
        if file_exists:
            assert overwrite == confirmed_overwrite
        else:
            assert overwrite is True

    @pytest.mark.parametrize("confirmed_overwrite", [True, False])
    def test_import_configuration(self, mocker, patch_base_class, confirmed_overwrite):
        configuration = {"foo": "bar"}
        mocker.patch.object(renderers.BaseRenderer, "_render")
        mocker.patch.object(renderers.BaseRenderer, "get_output_path")
        mocker.patch.object(renderers.yaml, "safe_load", mocker.Mock(return_value={}))
        mocker.patch.object(renderers.yaml, "safe_dump")
        mocker.patch.object(renderers.BaseRenderer, "_confirm_overwrite", mocker.Mock(return_value=confirmed_overwrite))
        spec_renderer = renderers.BaseRenderer("my_resource_name")
        spec_renderer.definition = mocker.Mock(type="my_definition")
        expected_output_path = renderers.BaseRenderer.get_output_path.return_value
        with patch("builtins.open", mock_open()) as mock_file:
            output_path = spec_renderer.import_configuration(project_path=".", configuration=configuration)
            spec_renderer._render.assert_called_once()
            renderers.yaml.safe_load.assert_called_with(spec_renderer._render.return_value)
            assert renderers.yaml.safe_load.return_value["configuration"] == configuration
            spec_renderer.get_output_path.assert_called_with(".", spec_renderer.definition.type, spec_renderer.resource_name)
            spec_renderer._confirm_overwrite.assert_called_with(expected_output_path)
            if confirmed_overwrite:
                mock_file.assert_called_with(expected_output_path, "wb")
                renderers.yaml.safe_dump.assert_called_with(
                    renderers.yaml.safe_load.return_value,
                    mock_file.return_value,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    encoding="utf-8",
                )
            assert output_path == renderers.BaseRenderer.get_output_path.return_value


class TestConnectorSpecificationRenderer:
    def test_init(self, mocker):
        assert renderers.ConnectorSpecificationRenderer.TEMPLATE == renderers.JINJA_ENV.get_template("source_or_destination.yaml.j2")
        definition = mocker.Mock()
        spec_renderer = renderers.ConnectorSpecificationRenderer("my_resource_name", definition)
        assert spec_renderer.resource_name == "my_resource_name"
        assert spec_renderer.definition == definition

    def test__parse_connection_specification(self, mocker):
        mocker.patch.object(renderers, "parse_fields")
        schema = {"required": ["foo"], "properties": {"foo": "bar"}}
        definition = mocker.Mock()
        spec_renderer = renderers.ConnectorSpecificationRenderer("my_resource_name", definition)
        parsed_schema = spec_renderer._parse_connection_specification(schema)
        assert renderers.parse_fields.call_count == 1
        assert parsed_schema[0], renderers.parse_fields.return_value
        renderers.parse_fields.assert_called_with(["foo"], {"foo": "bar"})

    def test__parse_connection_specification_one_of(self, mocker):
        mocker.patch.object(renderers, "parse_fields")
        schema = {"oneOf": [{"required": ["foo"], "properties": {"foo": "bar"}}, {"required": ["free"], "properties": {"free": "beer"}}]}
        spec_renderer = renderers.ConnectorSpecificationRenderer("my_resource_name", mocker.Mock())
        parsed_schema = spec_renderer._parse_connection_specification(schema)
        assert renderers.parse_fields.call_count == 2
        assert parsed_schema[0], renderers.parse_fields.return_value
        assert parsed_schema[1], renderers.parse_fields.return_value
        assert len(parsed_schema) == len(schema["oneOf"])
        renderers.parse_fields.assert_called_with(["free"], {"free": "beer"})

    @pytest.mark.parametrize("overwrite", [True, False])
    def test_write_yaml(self, mocker, overwrite):

        mocker.patch.object(renderers.ConnectorSpecificationRenderer, "get_output_path")
        mocker.patch.object(renderers.ConnectorSpecificationRenderer, "_parse_connection_specification")
        mocker.patch.object(
            renderers.ConnectorSpecificationRenderer, "TEMPLATE", mocker.Mock(render=mocker.Mock(return_value="rendered_string"))
        )
        mocker.patch.object(renderers.ConnectorSpecificationRenderer, "_confirm_overwrite", mocker.Mock(return_value=overwrite))

        spec_renderer = renderers.ConnectorSpecificationRenderer("my_resource_name", mocker.Mock(type="source"))
        if overwrite:
            with patch("builtins.open", mock_open()) as mock_file:
                output_path = spec_renderer.write_yaml(".")
            spec_renderer.TEMPLATE.render.assert_called_with(
                {
                    "resource_name": "my_resource_name",
                    "definition": spec_renderer.definition,
                    "configuration_fields": spec_renderer._parse_connection_specification.return_value,
                }
            )
            mock_file.assert_called_with(output_path, "w")
        else:
            output_path = spec_renderer.write_yaml(".")
        assert output_path == spec_renderer.get_output_path.return_value

    def test__render(self, mocker):
        mocker.patch.object(renderers.ConnectorSpecificationRenderer, "_parse_connection_specification")
        mocker.patch.object(renderers.ConnectorSpecificationRenderer, "TEMPLATE")
        spec_renderer = renderers.ConnectorSpecificationRenderer("my_resource_name", mocker.Mock())
        rendered = spec_renderer._render()
        spec_renderer._parse_connection_specification.assert_called_with(spec_renderer.definition.specification.connection_specification)
        spec_renderer.TEMPLATE.render.assert_called_with(
            {
                "resource_name": spec_renderer.resource_name,
                "definition": spec_renderer.definition,
                "configuration_fields": spec_renderer._parse_connection_specification.return_value,
            }
        )
        assert rendered == spec_renderer.TEMPLATE.render.return_value


class TestConnectionRenderer:
    @pytest.fixture
    def mock_source(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def mock_destination(self, mocker):
        return mocker.Mock()

    def test_init(self, mock_source, mock_destination):
        assert renderers.ConnectionRenderer.TEMPLATE == renderers.JINJA_ENV.get_template("connection.yaml.j2")
        connection_renderer = renderers.ConnectionRenderer("my_resource_name", mock_source, mock_destination)
        assert connection_renderer.resource_name == "my_resource_name"
        assert connection_renderer.source == mock_source
        assert connection_renderer.destination == mock_destination

    def test_catalog_to_yaml(self, mocker):
        stream = AirbyteStream(
            default_cursor_field=["foo"], json_schema={}, name="my_stream", supported_sync_modes=[SyncMode("full_refresh")]
        )
        config = AirbyteStreamConfiguration(
            alias_name="pokemon", selected=True, destination_sync_mode=DestinationSyncMode("append"), sync_mode=SyncMode("full_refresh")
        )
        catalog = AirbyteCatalog([AirbyteStreamAndConfiguration(stream=stream, config=config)])
        yaml_catalog = renderers.ConnectionRenderer.catalog_to_yaml(catalog)
        assert yaml_catalog == yaml.dump(catalog.to_dict(), Dumper=yaml_dumpers.CatalogDumper, default_flow_style=False)

    @pytest.mark.parametrize("overwrite", [True, False])
    def test_write_yaml(self, mocker, mock_source, mock_destination, overwrite):
        mocker.patch.object(renderers.ConnectionRenderer, "get_output_path")
        mocker.patch.object(renderers.ConnectionRenderer, "catalog_to_yaml")
        mocker.patch.object(renderers.ConnectionRenderer, "TEMPLATE")
        mocker.patch.object(renderers.ConnectionRenderer, "_confirm_overwrite", mocker.Mock(return_value=overwrite))

        connection_renderer = renderers.ConnectionRenderer("my_resource_name", mock_source, mock_destination)
        if overwrite:
            with patch("builtins.open", mock_open()) as mock_file:
                output_path = connection_renderer.write_yaml(".")
            connection_renderer.get_output_path.assert_called_with(".", renderers.ConnectionDefinition.type, "my_resource_name")
            connection_renderer.catalog_to_yaml.assert_called_with(mock_source.catalog)
            mock_file.assert_called_with(output_path, "w")
            mock_file.return_value.write.assert_called_with(connection_renderer.TEMPLATE.render.return_value)
            connection_renderer.TEMPLATE.render.assert_called_with(
                {
                    "connection_name": connection_renderer.resource_name,
                    "source_configuration_path": mock_source.configuration_path,
                    "destination_configuration_path": mock_destination.configuration_path,
                    "catalog": connection_renderer.catalog_to_yaml.return_value,
                    "supports_normalization": connection_renderer.destination.definition.normalization_config.supported,
                    "supports_dbt": connection_renderer.destination.definition.supports_dbt,
                }
            )
        else:
            output_path = connection_renderer.write_yaml(".")
        assert output_path == connection_renderer.get_output_path.return_value

    def test__render(self, mocker):
        mocker.patch.object(renderers.ConnectionRenderer, "catalog_to_yaml")
        mocker.patch.object(renderers.ConnectionRenderer, "TEMPLATE")
        connection_renderer = renderers.ConnectionRenderer("my_connection_name", mocker.Mock(), mocker.Mock())
        rendered = connection_renderer._render()
        connection_renderer.catalog_to_yaml.assert_called_with(connection_renderer.source.catalog)
        connection_renderer.TEMPLATE.render.assert_called_with(
            {
                "connection_name": connection_renderer.resource_name,
                "source_configuration_path": connection_renderer.source.configuration_path,
                "destination_configuration_path": connection_renderer.destination.configuration_path,
                "catalog": connection_renderer.catalog_to_yaml.return_value,
                "supports_normalization": connection_renderer.destination.definition.normalization_config.supported,
                "supports_dbt": connection_renderer.destination.definition.supports_dbt,
            }
        )
        assert rendered == connection_renderer.TEMPLATE.render.return_value

    @pytest.mark.parametrize("confirmed_overwrite, operations", [(True, []), (False, []), (True, [{}]), (False, [{}])])
    def test_import_configuration(self, mocker, confirmed_overwrite, operations):
        configuration = {"foo": "bar", "bar": "foo", "operations": operations}
        mocker.patch.object(renderers.ConnectionRenderer, "KEYS_TO_REMOVE_FROM_REMOTE_CONFIGURATION", ["bar"])
        mocker.patch.object(renderers.ConnectionRenderer, "_render")
        mocker.patch.object(renderers.ConnectionRenderer, "get_output_path")
        mocker.patch.object(renderers.yaml, "safe_load", mocker.Mock(return_value={}))
        mocker.patch.object(renderers.yaml, "safe_dump")
        mocker.patch.object(renderers.ConnectionRenderer, "_confirm_overwrite", mocker.Mock(return_value=confirmed_overwrite))
        spec_renderer = renderers.ConnectionRenderer("my_resource_name", mocker.Mock(), mocker.Mock())
        expected_output_path = renderers.ConnectionRenderer.get_output_path.return_value
        with patch("builtins.open", mock_open()) as mock_file:
            output_path = spec_renderer.import_configuration(project_path=".", configuration=configuration)
            spec_renderer._render.assert_called_once()
            renderers.yaml.safe_load.assert_called_with(spec_renderer._render.return_value)
            if operations:
                assert renderers.yaml.safe_load.return_value["configuration"] == {"foo": "bar", "operations": operations}
            else:
                assert renderers.yaml.safe_load.return_value["configuration"] == {"foo": "bar"}
            spec_renderer.get_output_path.assert_called_with(".", spec_renderer.definition.type, spec_renderer.resource_name)
            spec_renderer._confirm_overwrite.assert_called_with(expected_output_path)
            if confirmed_overwrite:
                mock_file.assert_called_with(expected_output_path, "wb")
                renderers.yaml.safe_dump.assert_called_with(
                    renderers.yaml.safe_load.return_value,
                    mock_file.return_value,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    encoding="utf-8",
                )
            assert output_path == renderers.ConnectionRenderer.get_output_path.return_value
