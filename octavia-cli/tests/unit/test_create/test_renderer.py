#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from octavia_cli.create import renderer


class TestFieldToRender:
    def test_init(self, mocker):
        mocker.patch.object(renderer.FieldToRender, "get_one_of_values")
        mocker.patch.object(renderer, "get_object_properties")
        mocker.patch.object(renderer.FieldToRender, "get_array_items")
        mocker.patch.object(renderer.FieldToRender, "build_comment")
        mocker.patch.object(renderer.FieldToRender, "get_default")

        field_metadata = mocker.Mock()
        field_to_render = renderer.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.name == "field_name"
        assert field_to_render.required
        assert field_to_render.field_metadata == field_metadata
        assert field_to_render.one_of_values == field_to_render.get_one_of_values.return_value
        assert field_to_render.object_properties == renderer.get_object_properties.return_value
        assert field_to_render.array_items == field_to_render.get_array_items.return_value
        assert field_to_render.comment == field_to_render.build_comment.return_value
        assert field_to_render.default == field_to_render.get_default.return_value
        field_to_render.build_comment.assert_called_with(
            [
                field_to_render.get_secret_comment,
                field_to_render.get_required_comment,
                field_to_render.get_type_comment,
                field_to_render.get_description_comment,
                field_to_render.get_example_comment,
            ]
        )

    def test_get_attr(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render.foo == "bar"
        assert field_to_render.not_existing is None

    def test_is_array_of_objects(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = "array"
        field_to_render.items = {"type": "object"}
        assert field_to_render.is_array_of_objects
        field_to_render.type = "array"
        field_to_render.items = {"type": "int"}
        assert not field_to_render.is_array_of_objects

    def test_get_one_of_values(self, mocker):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.oneOf = False
        assert field_to_render.get_one_of_values() == []

        mocker.patch.object(renderer, "get_object_properties")
        one_of_value = mocker.Mock()
        field_to_render.oneOf = [one_of_value]
        one_of_values = field_to_render.get_one_of_values()
        renderer.get_object_properties.assert_called_once_with(one_of_value)
        assert one_of_values == [renderer.get_object_properties.return_value]

    def test_get_array_items(self, mocker):
        mocker.patch.object(renderer, "parse_properties")
        mocker.patch.object(renderer.FieldToRender, "is_array_of_objects", False)

        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        assert field_to_render.get_array_items() == []
        field_to_render.items = {"required": [], "properties": []}
        mocker.patch.object(renderer.FieldToRender, "is_array_of_objects", True)
        assert field_to_render.get_array_items() == renderer.parse_properties.return_value
        renderer.parse_properties.assert_called_with([], [])

    def test_get_required_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.required = True
        assert field_to_render.get_required_comment() == "REQUIRED"
        field_to_render.required = False
        assert field_to_render.get_required_comment() == "OPTIONAL"

    def test_get_type_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.type = "mytype"
        assert field_to_render.get_type_comment() == "mytype"
        field_to_render.type = None
        assert field_to_render.get_type_comment() is None

    def test_get_secret_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.airbyte_secret = True
        assert field_to_render.get_secret_comment() == "🤫"
        field_to_render.airbyte_secret = False
        assert field_to_render.get_secret_comment() is None

    def test_get_description_comment(self):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.description = "foo"
        assert field_to_render.get_description_comment() == "foo"
        field_to_render.description = None
        assert field_to_render.get_description_comment() is None

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
    def test_get_example_comment(self, examples_value, expected_output):
        field_to_render = renderer.FieldToRender("field_name", True, {"foo": "bar"})
        field_to_render.examples = examples_value
        assert field_to_render.get_example_comment() == expected_output

    @pytest.mark.parametrize(
        "field_metadata,expected_default",
        [
            ({"const": "foo", "default": "bar"}, "foo"),
            ({"default": "bar"}, "bar"),
            ({}, None),
        ],
    )
    def test_get_default(self, field_metadata, expected_default):
        field_to_render = renderer.FieldToRender("field_name", True, field_metadata)
        assert field_to_render.default == expected_default

    def test_build_comment(self, mocker):
        comment_functions = [mocker.Mock(return_value="foo"), mocker.Mock(return_value=None), mocker.Mock(return_value="bar")]
        comment = renderer.FieldToRender.build_comment(comment_functions)
        assert comment == "foo | bar"


def test_parse_properties():
    required_fields = ["foo"]
    properties = {"foo": {}, "bar": {}}
    fields_to_render = renderer.parse_properties(required_fields, properties)
    assert fields_to_render[0].name == "foo"
    assert fields_to_render[0].required
    assert fields_to_render[1].name == "bar"
    assert not fields_to_render[1].required


def test_get_object_properties(mocker):
    mocker.patch.object(renderer, "parse_properties")
    field_metadata = {"properties": {"foo": {}, "bar": {}}, "required": ["foo"]}
    object_properties = renderer.get_object_properties(field_metadata)
    assert object_properties == renderer.parse_properties.return_value
    renderer.parse_properties.assert_called_with(["foo"], field_metadata["properties"])
    field_metadata = {}
    assert renderer.get_object_properties(field_metadata) == []


class TestConnectionSpecificationRenderer:
    def test_init(self, mocker):
        assert renderer.ConnectionSpecificationRenderer.TEMPLATE == renderer.JINJA_ENV.get_template("source_or_destination.yaml.j2")
        definition = mocker.Mock()
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", definition)
        assert spec_renderer.resource_name == "my_resource_name"
        assert spec_renderer.definition == definition

    def test_parse_schema(self, mocker):
        mocker.patch.object(renderer, "parse_properties")
        schema = {"required": ["foo"], "properties": {"foo": "bar"}}
        definition = mocker.Mock()
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", definition)
        parsed_schema = spec_renderer.parse_schema(schema)
        assert renderer.parse_properties.call_count == 1
        assert parsed_schema[0], renderer.parse_properties.return_value
        renderer.parse_properties.assert_called_with(["foo"], {"foo": "bar"})

    def test_parse_schema_one_of(self, mocker):
        mocker.patch.object(renderer, "parse_properties")
        schema = {"oneOf": [{"required": ["foo"], "properties": {"foo": "bar"}}, {"required": ["free"], "properties": {"free": "beer"}}]}
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock())
        parsed_schema = spec_renderer.parse_schema(schema)
        assert renderer.parse_properties.call_count == 2
        assert parsed_schema[0], renderer.parse_properties.return_value
        assert parsed_schema[1], renderer.parse_properties.return_value
        assert len(parsed_schema) == len(schema["oneOf"])
        renderer.parse_properties.assert_called_with(["free"], {"free": "beer"})

    def test_get_output_path(self, mocker):
        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock(type="source"))
        assert spec_renderer.get_output_path(".") == "./sources/my_resource_name.yaml"

    def test_write_yaml(self, mocker):
        mocker.patch.object(renderer.ConnectionSpecificationRenderer, "get_output_path")
        mocker.patch.object(renderer.ConnectionSpecificationRenderer, "parse_schema")
        mocker.patch.object(
            renderer.ConnectionSpecificationRenderer, "TEMPLATE", mocker.Mock(render=mocker.Mock(return_value="rendered_string"))
        )

        spec_renderer = renderer.ConnectionSpecificationRenderer("my_resource_name", mocker.Mock(type="source"))
        output_path = spec_renderer.write_yaml(".")
        assert output_path == spec_renderer.get_output_path.return_value
        spec_renderer.TEMPLATE.render.assert_called_with(
            {
                "resource_name": "my_resource_name",
                "definition": spec_renderer.definition,
                "configuration_fields": spec_renderer.parse_schema.return_value,
            }
        )
