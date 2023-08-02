#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import MutableMapping, Union

import pytest
from airbyte_cdk.models import AirbyteStream, ConnectorSpecification
from connector_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery
from connector_acceptance_test.tests.test_core import TestSpec as _TestSpec
from connector_acceptance_test.utils.backward_compatibility import NonBackwardCompatibleError, validate_previous_configs

from .conftest import does_not_raise


@dataclass
class Transition:
    """An helper class to improve readability of the test cases"""

    previous: Union[ConnectorSpecification, MutableMapping[str, AirbyteStream]]
    current: Union[ConnectorSpecification, MutableMapping[str, AirbyteStream]]
    should_fail: bool
    name: str
    is_valid_json_schema: bool = True

    def as_pytest_param(self):
        return pytest.param(self.previous, self.current, self.should_fail, id=self.name)


FAILING_SPEC_TRANSITIONS = [
    Transition(
        ConnectorSpecification(connectionSpecification={}),
        ConnectorSpecification(
            connectionSpecification={
                "required": ["a", "b"],
            }
        ),
        should_fail=True,
        name="Top level: declaring the required field should fail.",
    ),
    Transition(
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
        should_fail=True,
        name="Nested level: adding the required field should fail.",
    ),
    Transition(
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
        name="Top level: adding a new required property should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Nested level: adding a new required property should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Nullable: Making a field not nullable should fail (not in a list).",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["null", "integer"]}}},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["integer"]}}},
                },
            }
        ),
        name="Nested level: Narrowing a field type should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        name="Nullable field: Making a field not nullable should fail",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "integer"},
                },
            }
        ),
        name="Changing a field type should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["integer"]},
                },
            }
        ),
        name="Changing a field type from a string to a list with a different type value should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "integer"},
                },
            }
        ),
        name="Changing a field type should fail from a list to string with different value should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["integer"]},
                },
            }
        ),
        name="Changing a field type in list should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["integer", "null"]},
                },
            }
        ),
        name="Making a field nullable and changing type should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "integer"]},
                },
            }
        ),
        name="Making a field nullable and changing type should fail (change list order).",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "integer"]},
                },
            }
        ),
        name="Nullable field: Changing a field type should fail",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "credentials": {
                        "oneOf": [
                            {"title": "a", "type": "string"},
                            {"title": "b", "type": "integer"},
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
                            {"title": "a", "type": "integer"},
                            {"title": "b", "type": "integer"},
                        ]
                    },
                },
            }
        ),
        name="Changing a field type in oneOf should fail.",
        should_fail=True,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "credentials": {
                        "oneOf": [
                            {"title": "a", "type": ["string", "null"]},
                            {"title": "b", "type": "integer"},
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
                            {"title": "a", "type": ["string"]},
                            {"title": "b", "type": "integer"},
                        ]
                    },
                },
            }
        ),
        name="Narrowing a field type in oneOf should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Top level: Narrowing a field enum should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Nested level: Narrowing a field enum should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Top level: Declaring a field enum should fail.",
        should_fail=True,
    ),
    Transition(
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
        name="Nested level: Declaring a field enum should fail.",
        should_fail=True,
    ),
    Transition(
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
                    "my_string": {"type": {}},
                },
            }
        ),
        name="Changing a 'type' field from a string to something else than a list should fail.",
        should_fail=True,
        is_valid_json_schema=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_string": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_string": {"type": {}},
                },
            }
        ),
        name="Changing a 'type' field from a list to something else than a string should fail.",
        should_fail=True,
        is_valid_json_schema=False,
    ),
]

VALID_SPEC_TRANSITIONS = [
    Transition(
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
                },
            }
        ),
        name="Not changing a spec should not fail",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "required": ["my_required_string"],
                "additionalProperties": False,
                "properties": {
                    "my_required_string": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "required": ["my_required_string"],
                "additionalProperties": True,
                "properties": {
                    "my_required_string": {"type": "string"},
                },
            }
        ),
        name="Top level: Changing the value of additionalProperties should not fail",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["integer"]}}},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {"my_property": {"type": ["integer"]}},
                    },
                },
            }
        ),
        name="Nested level: Changing the value of additionalProperties should not fail",
        should_fail=False,
    ),
    Transition(
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
                    "my_optional": {"type": "string"},
                },
            }
        ),
        name="Adding an optional field should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Adding an optional object with required properties should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        name="No change should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        name="Changing a field type from a list to a string with same value should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        name="Changing a field type from a string to a list should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string", "integer"]},
                },
            }
        ),
        name="Adding a field type in list should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "string"]},
                },
            }
        ),
        name="Making a field nullable should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": "string"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string", "null"]},
                },
            }
        ),
        name="Making a field nullable should not fail (change list order).",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "string"]},
                },
            }
        ),
        name="Making a field nullable should not fail (from a list).",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string", "null"]},
                },
            }
        ),
        name="Making a field nullable should not fail (from a list, changing order).",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["null", "string"]},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_int": {"type": ["string", "null"]},
                },
            }
        ),
        name="Nullable field: Changing order should not fail",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["integer"]}}},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_nested_object": {"type": "object", "properties": {"my_property": {"type": ["null", "integer"]}}},
                },
            }
        ),
        name="Nested level: Expanding a field type should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "credentials": {
                        "oneOf": [
                            {"title": "a", "type": "string"},
                            {"title": "b", "type": "integer"},
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
                            {"title": "b", "type": "string"},
                            {"title": "a", "type": "integer"},
                        ]
                    },
                },
            }
        ),
        name="Changing a order in oneOf should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Top level: Expanding a field enum should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Nested level: Expanding a field enum should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Top level: Adding a new optional field with enum should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Top level: Removing the field enum should not fail.",
        should_fail=False,
    ),
    Transition(
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
        name="Nested level: Removing the enum field should not fail.",
        should_fail=False,
    ),
    Transition(
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_string": {"type": "integer"},
                },
            }
        ),
        ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "properties": {
                    "my_string": {"type": ["integer", "string"]},
                },
            }
        ),
        name="Changing a 'type' field from a string to a list containing that same string should not fail.",
        should_fail=False,
    ),
]

# Checking that all transitions in FAILING_SPEC_TRANSITIONS have should_fail == True to prevent typos
assert all([transition.should_fail for transition in FAILING_SPEC_TRANSITIONS])
# Checking that all transitions in VALID_SPEC_TRANSITIONS have should_fail = False to prevent typos
assert all([not transition.should_fail for transition in VALID_SPEC_TRANSITIONS])

ALL_SPEC_TRANSITIONS_PARAMS = [transition.as_pytest_param() for transition in FAILING_SPEC_TRANSITIONS + VALID_SPEC_TRANSITIONS]


@pytest.mark.parametrize("previous_connector_spec, actual_connector_spec, should_fail", ALL_SPEC_TRANSITIONS_PARAMS)
def test_spec_backward_compatibility(previous_connector_spec, actual_connector_spec, should_fail):
    t = _TestSpec()
    expectation = pytest.raises(NonBackwardCompatibleError) if should_fail else does_not_raise()
    with expectation:
        t.test_backward_compatibility(False, actual_connector_spec, previous_connector_spec, 10)


VALID_JSON_SCHEMA_TRANSITIONS_PARAMS = [
    transition.as_pytest_param() for transition in FAILING_SPEC_TRANSITIONS + VALID_SPEC_TRANSITIONS if transition.is_valid_json_schema
]


@pytest.mark.slow
@pytest.mark.parametrize("previous_connector_spec, actual_connector_spec, should_fail", VALID_JSON_SCHEMA_TRANSITIONS_PARAMS)
def test_validate_previous_configs(previous_connector_spec, actual_connector_spec, should_fail):
    expectation = pytest.raises(NonBackwardCompatibleError) if should_fail else does_not_raise()
    with expectation:
        validate_previous_configs(previous_connector_spec, actual_connector_spec, 200)


FAILING_CATALOG_TRANSITIONS = [
    Transition(
        name="Removing a stream from a catalog should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
            "other_test_stream": AirbyteStream.parse_obj(
                {
                    "name": "other_test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
    Transition(
        name="Changing a field type should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "integer"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
    Transition(
        name="Renaming a stream should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "new_test_stream": AirbyteStream.parse_obj(
                {
                    "name": "new_test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
    Transition(
        name="Changing a cursor in a stream should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["a"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["b"],
                }
            ),
        },
    ),
    Transition(
        name="Changing a cursor in a stream should fail (nested cursors).",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["a"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["a", "b"],
                }
            ),
        },
    ),
    Transition(
        name="Changing a cursor in a stream should fail (nested cursors removal).",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["a", "b"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                    "default_cursor_field": ["a"],
                }
            ),
        },
    ),
    Transition(
        name="Adding a stream but changing cursor should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["incremental"],
                    "default_cursor_field": ["a"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["incremental"],
                    "default_cursor_field": ["b"],
                }
            ),
            "other_test_stream": AirbyteStream.parse_obj(
                {
                    "name": "other_test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["incremental"],
                }
            ),
        },
    ),
    Transition(
        name="Changing a 'type' field from a string to something else than a list containing just that string and null should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "integer"}}}}},
                    "default_cursor_field": ["a"],
                    "supported_sync_modes": ["incremental"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {
                        "properties": {"user": {"type": "object", "properties": {"username": {"type": ["integer", "string"]}}}}
                    },
                    "default_cursor_field": ["b"],
                    "supported_sync_modes": ["incremental"],
                }
            ),
        },
    ),
    Transition(
        name="Removing a top level field should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {
                        "properties": {"username": {"type": "string"}, "email": {"type": "string"}},
                    },
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {
                        "properties": {"username": {"type": "string"}},
                    },
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
    Transition(
        name="Removing a nested field should fail.",
        should_fail=True,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {
                        "properties": {
                            "user": {"type": "object", "properties": {"username": {"type": "string"}, "email": {"type": "string"}}}
                        }
                    },
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
]

VALID_CATALOG_TRANSITIONS = [
    Transition(
        name="Adding a stream to a catalog should not fail.",
        should_fail=False,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
            "other_test_stream": AirbyteStream.parse_obj(
                {
                    "name": "other_test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
        },
    ),
    Transition(
        name="Making a field nullable should not fail.",
        should_fail=False,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": ["string", "null"]}}}}},
                }
            )
        },
    ),
    Transition(
        name="Changing 'type' field to list should not fail.",
        should_fail=False,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                }
            )
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": ["string"]}}}}},
                    "supported_sync_modes": ["full_refresh"],
                }
            )
        },
    ),
    Transition(
        name="Not changing a cursor in a stream should not fail.",
        should_fail=False,
        previous={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "default_cursor_field": ["a"],
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
        },
        current={
            "test_stream": AirbyteStream.parse_obj(
                {
                    "name": "test_stream",
                    "json_schema": {"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}},
                    "default_cursor_field": ["a"],
                    "supported_sync_modes": ["full_refresh"],
                }
            ),
        },
    ),
]

# Checking that all transitions in FAILING_CATALOG_TRANSITIONS have should_fail == True to prevent typos
assert all([transition.should_fail for transition in FAILING_CATALOG_TRANSITIONS])
# Checking that all transitions in VALID_CATALOG_TRANSITIONS have should_fail = False to prevent typos
assert all([not transition.should_fail for transition in VALID_CATALOG_TRANSITIONS])

ALL_CATALOG_TRANSITIONS_PARAMS = [transition.as_pytest_param() for transition in FAILING_CATALOG_TRANSITIONS + VALID_CATALOG_TRANSITIONS]


@pytest.mark.parametrize("previous_discovered_catalog, discovered_catalog, should_fail", ALL_CATALOG_TRANSITIONS_PARAMS)
def test_catalog_backward_compatibility(previous_discovered_catalog, discovered_catalog, should_fail):
    t = _TestDiscovery()
    expectation = pytest.raises(NonBackwardCompatibleError) if should_fail else does_not_raise()
    with expectation:
        t.test_backward_compatibility(False, discovered_catalog, previous_discovered_catalog)
