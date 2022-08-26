#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_acceptance_test.tests.test_core import TestSpec as _TestSpec

from .conftest import does_not_raise


@pytest.mark.parametrize(
    "connector_spec, expectation",
    [
        (ConnectorSpecification(connectionSpecification={}), does_not_raise()),
        (ConnectorSpecification(connectionSpecification={"type": "object", "additionalProperties": True}), does_not_raise()),
        (ConnectorSpecification(connectionSpecification={"type": "object", "additionalProperties": False}), pytest.raises(AssertionError)),
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "additionalProperties": True,
                    "properties": {"my_object": {"type": "object", "additionalProperties": "foo"}},
                }
            ),
            pytest.raises(AssertionError),
        ),
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "additionalProperties": True,
                    "properties": {
                        "my_oneOf_object": {"type": "object", "oneOf": [{"additionalProperties": True}, {"additionalProperties": False}]}
                    },
                }
            ),
            pytest.raises(AssertionError),
        ),
    ],
)
def test_additional_properties_is_true(connector_spec, expectation):
    t = _TestSpec()
    with expectation:
        t.test_additional_properties_is_true(connector_spec)


@pytest.mark.parametrize(
    "previous_connector_spec, actual_connector_spec, expectation",
    [
        pytest.param(
            ConnectorSpecification(connectionSpecification={}),
            ConnectorSpecification(
                connectionSpecification={
                    "required": ["a", "b"],
                }
            ),
            pytest.raises(AssertionError),
            id="Top level: declaring the required field should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {"my_optional_object": {"type": "object", "properties": {"optional_property": {"type": "string"}}}},
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_optional_object": {
                            "type": "object",
                            "required": ["optional_property"],
                            "properties": {"optional_property": {"type": "string"}},
                        }
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nested level: adding the required field should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "required": ["my_required_string"],
                    "properties": {
                        "my_required_string": {"type": "string"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "required": ["my_required_string"],
                    "properties": {
                        "my_required_string": {"type": "string"},
                        "my_optional_object": {
                            "type": "object",
                            "required": ["another_required_string"],
                            "properties": {"another_required_string": {"type": "string"}},
                        },
                    },
                }
            ),
            does_not_raise(),
            id="Adding an optional object with required properties should not fail.",
        ),
    ],
)
def test_new_required_field_declaration(previous_connector_spec, actual_connector_spec, expectation):
    t = _TestSpec()
    spec_diff = t.compute_spec_diff(actual_connector_spec, previous_connector_spec)
    with expectation:
        t.test_new_required_field_declaration(spec_diff)


@pytest.mark.parametrize(
    "previous_connector_spec, actual_connector_spec, expectation",
    [
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "required": ["a"],
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "required": ["a", "b"],
                }
            ),
            pytest.raises(AssertionError),
            id="Top level: adding a new required property should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_optional_object": {
                            "type": "object",
                            "required": ["first_required_property"],
                            "properties": {"first_required_property": {"type": "string"}},
                        }
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_optional_object": {
                            "type": "object",
                            "required": ["first_required_property", "second_required_property"],
                            "properties": {
                                "first_required_property": {"type": "string"},
                                "second_required_property": {"type": "string"},
                            },
                        }
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nested level: adding a new required property should fail.",
        ),
    ],
)
def test_new_required_property(previous_connector_spec, actual_connector_spec, expectation):
    t = _TestSpec()
    spec_diff = t.compute_spec_diff(actual_connector_spec, previous_connector_spec)
    with expectation:
        t.test_new_required_property(spec_diff)


@pytest.mark.parametrize(
    "previous_connector_spec, actual_connector_spec, expectation",
    [
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "int"},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            does_not_raise(),
            id="No change should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            does_not_raise(),
            id="Changing a field type from a string to a list should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a string to a list with a different type value should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "int"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int", "int"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a string to a list with duplicate same type should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "int"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int", "null", "str"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a string to a list with more than two values should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "int"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": []},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a string to an empty list should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": []},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a list to an empty list should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "int"},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type should fail from a list to string with different value should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            does_not_raise(),
            id="Changing a field type from a list to a string with same value should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type in list should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str", "int"]},
                    },
                }
            ),
            does_not_raise(),
            id="Adding a field type in list should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "str"]},
                    },
                }
            ),
            does_not_raise(),
            id="Making a field nullable should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str", "null"]},
                    },
                }
            ),
            does_not_raise(),
            id="Making a field nullable should not fail (change list order).",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "str"]},
                    },
                }
            ),
            does_not_raise(),
            id="Making a field nullable should not fail (from a list).",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str", "null"]},
                    },
                }
            ),
            does_not_raise(),
            id="Making a field nullable should not fail (from a list, changing order).",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["int", "null"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Making a field nullable and changing type should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "int"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Making a field nullable and changing type should fail (change list order).",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": "str"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": 1},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type from a string to something else than a list should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "int"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nullable field: Changing a field type should fail",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str", "null"]},
                    },
                }
            ),
            does_not_raise(),
            id="Nullable field: Changing order should not fail",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["null", "str"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_int": {"type": ["str"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nullable field: Making a field not nullable should fail",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": ["null", "string"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string"},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nullable: Making a field not nullable should fail (not in a list).",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["null", "int"]}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["int"]}}},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nested level: Narrowing a field type should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["int"]}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["null", "int"]}}},
                    },
                }
            ),
            does_not_raise(),
            id="Nested level: Expanding a field type should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "a", "type": "str"},
                                {"title": "b", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "a", "type": "int"},
                                {"title": "b", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Changing a field type in oneOf should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "a", "type": "str"},
                                {"title": "b", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "b", "type": "str"},
                                {"title": "a", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            does_not_raise(),
            id="Changing a order in oneOf should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "a", "type": ["str", "int"]},
                                {"title": "b", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "oneOf": [
                                {"title": "a", "type": ["str"]},
                                {"title": "b", "type": "int"},
                            ]
                        },
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Narrowing a field type in oneOf should fail.",
        ),
    ],
)
def test_field_type_changed(previous_connector_spec, actual_connector_spec, expectation):
    t = _TestSpec()
    spec_diff = t.compute_spec_diff(actual_connector_spec, previous_connector_spec)
    with expectation:
        t.test_field_type_changed(spec_diff)


@pytest.mark.parametrize(
    "previous_connector_spec, actual_connector_spec, expectation",
    [
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Top level: Narrowing a field enum should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            ),
            does_not_raise(),
            id="Top level: Expanding a field enum should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a", "b"]}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a"]}}},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nested level: Narrowing a field enum should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a"]}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a", "b"]}}},
                    },
                }
            ),
            does_not_raise(),
            id="Nested level: Expanding a field enum should not fail.",
        ),
    ],
)
def test_enum_field_has_narrowed(previous_connector_spec, actual_connector_spec, expectation):
    t = _TestSpec()
    spec_diff = t.compute_spec_diff(actual_connector_spec, previous_connector_spec)
    with expectation:
        t.test_enum_field_has_narrowed(spec_diff)


@pytest.mark.parametrize(
    "previous_connector_spec, actual_connector_spec, expectation",
    [
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string"},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Top level: Declaring a field enum should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string"},
                    },
                }
            ),
            does_not_raise(),
            id="Top level: Removing the field enum should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_string": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {"my_string": {"type": "string", "enum": ["a", "b"]}, "my_enum": {"type": "string", "enum": ["c", "d"]}},
                }
            ),
            does_not_raise(),
            id="Top level: Adding a new optional field with enum should not fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string"}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a", "b"]}}},
                    },
                }
            ),
            pytest.raises(AssertionError),
            id="Nested level: Declaring a field enum should fail.",
        ),
        pytest.param(
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string", "enum": ["a", "b"]}}},
                    },
                }
            ),
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "my_nested_object": {"type": "object", "properties": {"my_property": {"type": "string"}}},
                    },
                }
            ),
            does_not_raise(),
            id="Nested level: Removing the enum field should not fail.",
        ),
    ],
)
def test_new_enum_field_declaration(previous_connector_spec, actual_connector_spec, expectation):
    t = _TestSpec()
    spec_diff = t.compute_spec_diff(actual_connector_spec, previous_connector_spec)
    with expectation:
        t.test_new_enum_field_declaration(spec_diff)
