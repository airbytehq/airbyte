#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from octavia_cli.create import renderer


class TestFieldToRender:
    def test_init(self, mocker):
        mocker.patch.object(renderer.FieldToRender, "_get_one_of_values")
        mocker.patch.object(renderer, "get_object_fields")
        mocker.patch.object(renderer.FieldToRender, "_get_array_items")
        mocker.patch.object(renderer.FieldToRender, "_build_comment")
        mocker.patch.object(renderer.FieldToRender, "_get_default")

        field_metadata = mocker.Mock()
        field_to_render = renderer.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.name == "field_name"
        assert field_to_render.required
        assert field_to_render.field_metadata == field_metadata
        assert field_to_render.one_of_values == field_to_render._get_one_of_values.return_value
        assert field_to_render.object_properties == renderer.get_object_fields.return_value
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
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render.foo == "bar"
        assert field_to_render.not_existing is None

    def test__is_array_of_objects(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = "array"
        field_to_render.items = {"type": "object"}
        assert field_to_render._is_array_of_objects
        field_to_render.type = "array"
        field_to_render.items = {"type": "int"}
        assert not field_to_render._is_array_of_objects

    def test__get_one_of_values(self, mocker):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.oneOf = False
        assert field_to_render._get_one_of_values() == []

        mocker.patch.object(renderer, "get_object_fields")
        one_of_value = mocker.Mock()
        field_to_render.oneOf = [one_of_value]
        one_of_values = field_to_render._get_one_of_values()
        renderer.get_object_fields.assert_called_once_with(one_of_value)
        assert one_of_values == [renderer.get_object_fields.return_value]

    def test__get_array_items(self, mocker):
        mocker.patch.object(renderer, "parse_fields")
        mocker.patch.object(renderer.FieldToRender, "_is_array_of_objects", False)

        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render._get_array_items() == []
        field_to_render.items = {"required": [], "properties": []}
        mocker.patch.object(renderer.FieldToRender, "_is_array_of_objects", True)
        assert field_to_render._get_array_items() == renderer.parse_fields.return_value
        renderer.parse_fields.assert_called_with([], [])

    def test__get_required_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.required = True
        assert field_to_render._get_required_comment() == "REQUIRED"
        field_to_render.required = False
        assert field_to_render._get_required_comment() == "OPTIONAL"

    def test__get_type_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = "mytype"
        assert field_to_render._get_type_comment() == "mytype"
        field_to_render.type = None
        assert field_to_render._get_type_comment() is None

    def test__get_secret_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.airbyte_secret = True
        assert field_to_render._get_secret_comment() == "🤫"
        field_to_render.airbyte_secret = False
        assert field_to_render._get_secret_comment() is None

    def test__get_description_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
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
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.examples = examples_value
        assert field_to_render._get_example_comment() == expected_output

    @pytest.mark.parametrize(
        "field_metadata,expected_default",
        [
            ({"const": "foo", "default": "bar"}, "foo"),
            ({"default": "bar"}, "bar"),
            ({}, None),
        ],
    )
    def test__get_default(self, field_metadata, expected_default):
        field_to_render = renderer.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.default == expected_default

    def test__build_comment(self, mocker):
        comment_functions = [mocker.Mock(return_value="foo"), mocker.Mock(return_value=None), mocker.Mock(return_value="bar")]
        comment = renderer.FieldToRender._build_comment(comment_functions)
        assert comment == "foo | bar"


def test_parse_fields():
    required_fields = ["foo"]
    properties = {"foo": {}, "bar": {}}
    fields_to_render = renderer.parse_fields(required_fields, properties)
    assert fields_to_render[0].name == "foo"
    assert fields_to_render[0].required
    assert fields_to_render[1].name == "bar"
    assert not fields_to_render[1].required


def test_get_object_fields(mocker):
    mocker.patch.object(renderer, "parse_fields")
    field_metadata = {"properties": {"foo": {}, "bar": {}}, "required": ["foo"]}
    object_properties = renderer.get_object_fields(field_metadata)
    assert object_properties == renderer.parse_fields.return_value
    renderer.parse_fields.assert_called_with(["foo"], field_metadata["properties"])
    field_metadata = {}
    assert renderer.get_object_fields(field_metadata) == []


class TestConnectionSpecificationRenderer:
    def test_init(self, mocker):
        assert renderer.ConnectionSpecificationRenderer.TEMPLATE == renderer.JINJA_ENV.get_template("source_or_destination.yaml.j2")
        definition = mocker.Mock()
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", definition)
        assert spec_renderer.resource_name == "my_resource_name"
        assert spec_renderer.definition == definition

    def test__parse_connection_specification(self, mocker):
        mocker.patch.object(renderer, "parse_fields")
        schema = {"required": ["foo"], "properties": {"foo": "bar"}}
        definition = mocker.Mock()
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", definition)
        parsed_schema = spec_renderer._parse_connection_specification(schema)
        assert renderer.parse_fields.call_count == 1
        assert parsed_schema[0], renderer.parse_fields.return_value
        renderer.parse_fields.assert_called_with(["foo"], {"foo": "bar"})

    def test__parse_connection_specification_one_of(self, mocker):
        mocker.patch.object(renderer, "parse_fields")
        schema = {"oneOf": [{"required": ["foo"], "properties": {"foo": "bar"}}, {"required": ["free"], "properties": {"free": "beer"}}]}
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock())
        parsed_schema = spec_renderer._parse_connection_specification(schema)
        assert renderer.parse_fields.call_count == 2
        assert parsed_schema[0], renderer.parse_fields.return_value
        assert parsed_schema[1], renderer.parse_fields.return_value
        assert len(parsed_schema) == len(schema["oneOf"])
        renderer.parse_fields.assert_called_with(["free"], {"free": "beer"})

    def test__get_output_path(self, mocker):
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock(type="source"))
        assert spec_renderer._get_output_path(".") == "./sources/my_resource_name.yaml"

    def test_write_yaml(self, mocker):
        mocker.patch.object(renderer.ConnectionSpecificationRenderer, "_get_output_path")
        mocker.patch.object(renderer.ConnectionSpecificationRenderer, "_parse_connection_specification")
        mocker.patch.object(
            renderer.ConnectionSpecificationRenderer, "TEMPLATE", mocker.Mock(render=mocker.Mock(return_value="rendered_string"))
        )

        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock(type="source"))
        output_path = spec_renderer.write_yaml(".")
        assert output_path == spec_renderer._get_output_path.return_value
        spec_renderer.TEMPLATE.render.assert_called_with(
            {
                "resource_name": "my_resource_name",
                "definition": spec_renderer.definition,
                "configuration_fields": spec_renderer._parse_connection_specification.return_value,
            }
        )
