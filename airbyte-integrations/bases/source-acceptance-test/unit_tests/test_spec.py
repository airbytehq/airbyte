#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Callable, Dict

import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_acceptance_test import conftest
from source_acceptance_test.tests.test_core import TestSpec as _TestSpec

from .conftest import does_not_raise


@pytest.mark.parametrize(
    "connector_spec, should_fail",
    [
        (
            {
                "connectionSpecification": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "$ref": None,
                    },
                }
            },
            True,
        ),
        (
            {
                "advanced_auth": {
                    "auth_flow_type": "oauth2.0",
                    "predicate_key": ["credentials", "auth_type"],
                    "predicate_value": "Client",
                    "oauth_config_specification": {
                        "complete_oauth_output_specification": {
                            "type": "object",
                            "properties": {"refresh_token": {"type": "string"}, "$ref": None},
                        }
                    },
                }
            },
            True,
        ),
        (
            {
                "advanced_auth": {
                    "auth_flow_type": "oauth2.0",
                    "predicate_key": ["credentials", "auth_type"],
                    "predicate_value": "Client",
                    "oauth_config_specification": {
                        "complete_oauth_server_input_specification": {
                            "type": "object",
                            "properties": {"refresh_token": {"type": "string"}, "$ref": None},
                        }
                    },
                }
            },
            True,
        ),
        (
            {
                "advanced_auth": {
                    "auth_flow_type": "oauth2.0",
                    "predicate_key": ["credentials", "auth_type"],
                    "predicate_value": "Client",
                    "oauth_config_specification": {
                        "complete_oauth_server_output_specification": {
                            "type": "object",
                            "properties": {"refresh_token": {"type": "string"}, "$ref": None},
                        }
                    },
                }
            },
            True,
        ),
        (
            {
                "connectionSpecification": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                    },
                }
            },
            False,
        ),
        (
            {
                "connectionSpecification": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                    },
                },
                "advanced_auth": {
                    "auth_flow_type": "oauth2.0",
                    "predicate_key": ["credentials", "auth_type"],
                    "predicate_value": "Client",
                    "oauth_config_specification": {
                        "complete_oauth_server_output_specification": {
                            "type": "object",
                            "properties": {"refresh_token": {"type": "string"}},
                        }
                    },
                },
            },
            False,
        ),
        ({"$ref": None}, True),
        ({"properties": {"user": {"$ref": None}}}, True),
        ({"properties": {"user": {"$ref": "user.json"}}}, True),
        ({"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}}, False),
        ({"properties": {"fake_items": {"type": "array", "items": {"$ref": "fake_item.json"}}}}, True),
    ],
)
def test_ref_in_spec_schemas(connector_spec, should_fail):
    t = _TestSpec()
    if should_fail is True:
        with pytest.raises(AssertionError):
            t.test_defined_refs_exist_in_json_spec_file(connector_spec_dict=connector_spec)
    else:
        t.test_defined_refs_exist_in_json_spec_file(connector_spec_dict=connector_spec)


def parametrize_test_case(*test_cases: Dict[str, Any]) -> Callable:
    """Util to wrap pytest.mark.parametrize and provider more friendlier interface.

    @parametrize_test_case({"value": 10, "expected_to_fail": True}, {"value": 100, "expected_to_fail": False})

    an equivalent to:

    @pytest.mark.parametrize("value,expected_to_fail", [(10, True), (100, False)])

    :param test_cases: list of dicts
    :return: pytest.mark.parametrize decorator
    """
    all_keys = set()
    for test_case in test_cases:
        all_keys = all_keys.union(set(test_case.keys()))
    all_keys.discard("test_id")

    test_ids = []
    values = []
    for test_case in test_cases:
        test_ids.append(test_case.pop("test_id", None))
        values.append(tuple(test_case.get(k) for k in all_keys))

    return pytest.mark.parametrize(",".join(all_keys), values, ids=test_ids)


@parametrize_test_case(
    {
        "test_id": "all_good",
        "connector_spec": {
            "type": "object",
            "properties": {
                "select_type": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "option_title": {"type": "string", "title": "Title", "const": "first option"},
                                "something": {"type": "string"},
                            },
                        },
                        {
                            "type": "object",
                            "properties": {
                                "option_title": {"type": "string", "title": "Title", "const": "second option"},
                                "some_field": {"type": "boolean"},
                            },
                        },
                    ],
                },
                "client_secret": {"type": "string"},
                "access_token": {"type": "string"},
            },
        },
        "should_fail": False,
    },
    {
        "test_id": "top_level_node_is_not_of_object_type",
        "connector_spec": {
            "type": "object",
            "properties": {
                "select_type": {
                    "oneOf": [],
                },
            },
        },
        "should_fail": True,
    },
    {
        "test_id": "all_oneof_options_should_have_same_constant_attribute",
        "connector_spec": {
            "type": "object",
            "properties": {
                "select_type": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "wrong_title": {"type": "string", "title": "Title", "const": "first option"},
                                "something": {"type": "string"},
                            },
                        },
                        {
                            "type": "object",
                            "properties": {
                                "option_title": {"type": "string", "title": "Title", "const": "second option"},
                                "some_field": {"type": "boolean"},
                            },
                        },
                    ],
                },
                "client_secret": {"type": "string"},
                "access_token": {"type": "string"},
            },
        },
        "should_fail": True,
    },
    {
        "test_id": "one_of_item_is_not_of_type_object",
        "connector_spec": {
            "type": "object",
            "properties": {
                "select_type": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "string",
                        },
                        {
                            "type": "object",
                            "properties": {
                                "option_title": {"type": "string", "title": "Title", "const": "second option"},
                                "some_field": {"type": "boolean"},
                            },
                        },
                    ],
                },
                "client_secret": {"type": "string"},
                "access_token": {"type": "string"},
            },
        },
        "should_fail": True,
    },
    {
        "test_id": "no_common_property_for_all_oneof_subobjects",
        "connector_spec": {
            "type": "object",
            "properties": {
                "credentials": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "option1": {"type": "string"},
                                "option2": {"type": "string"},
                            },
                        },
                        {
                            "type": "object",
                            "properties": {
                                "option3": {"type": "string"},
                                "option4": {"type": "string"},
                            },
                        },
                    ],
                }
            },
        },
        "should_fail": True,
    },
    {
        "test_id": "two_common_properties_with_const_keyword",
        "connector_spec": {
            "type": "object",
            "properties": {
                "credentials": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "common1": {"type": "string", "const": "common1"},
                                "common2": {"type": "string", "const": "common2"},
                            },
                        },
                        {
                            "type": "object",
                            "properties": {
                                "common1": {"type": "string", "const": "common1"},
                                "common2": {"type": "string", "const": "common2"},
                            },
                        },
                    ],
                }
            },
        },
        "should_fail": True,
    },
    {
        "test_id": "default_keyword_in_common_property",
        "connector_spec": {
            "type": "object",
            "properties": {
                "credentials": {
                    "type": "object",
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "common": {"type": "string", "const": "option1", "default": "option1"},
                                "option1": {"type": "string"},
                            },
                        },
                        {
                            "type": "object",
                            "properties": {
                                "common": {"type": "string", "const": "option2", "default": "option2"},
                                "option2": {"type": "string"},
                            },
                        },
                    ],
                }
            },
        },
        "should_fail": True,
    },
)
def test_oneof_usage(connector_spec, should_fail):
    t = _TestSpec()
    if should_fail is True:
        with pytest.raises(AssertionError):
            t.test_oneof_usage(actual_connector_spec=ConnectorSpecification(connectionSpecification=connector_spec))
    else:
        t.test_oneof_usage(actual_connector_spec=ConnectorSpecification(connectionSpecification=connector_spec))


@parametrize_test_case(
    {
        "test_id": "successful",
        "connector_spec": {
            "type": "object",
            "properties": {
                "property_with_options": {
                    "title": "Property with options",
                    "description": "A property in the form of an enumerated list",
                    "type": "string",
                    "default": "Option 1",
                    "enum": ["Option 1", "Option 2", "Option 3"],
                }
            },
        },
        "should_fail": False,
    },
    {
        "test_id": "duplicate_values",
        "connector_spec": {
            "type": "object",
            "properties": {
                "property_with_options": {
                    "title": "Property with options",
                    "description": "A property in the form of an enumerated list",
                    "type": "string",
                    "default": "Option 1",
                    "enum": ["Option 1", "Option 2", "Option 3", "Option 2"],
                }
            },
        },
        "should_fail": True,
    },
)
def test_enum_usage(connector_spec, should_fail):
    t = _TestSpec()
    if should_fail is True:
        with pytest.raises(AssertionError):
            t.test_enum_usage(actual_connector_spec=ConnectorSpecification(connectionSpecification=connector_spec))
    else:
        t.test_enum_usage(actual_connector_spec=ConnectorSpecification(connectionSpecification=connector_spec))


@pytest.mark.parametrize(
    "connector_spec, expected_error",
    [
        # SUCCESS: no authSpecification specified
        (ConnectorSpecification(connectionSpecification={}), ""),
        # FAIL: Field specified in root object does not exist
        (
            ConnectorSpecification(
                connectionSpecification={"type": "object"},
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: Empty root object
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": [],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # FAIL: Some oauth fields missed
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "client_secret": {"type": "string"},
                                "access_token": {"type": "string"},
                            },
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: case w/o oneOf property
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "client_secret": {"type": "string"},
                                "access_token": {"type": "string"},
                                "refresh_token": {"type": "string"},
                            },
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials"],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # SUCCESS: case w/ oneOf property
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # FAIL: Wrong root object index
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 1],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: root object index equal to 1
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 1],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
    ],
)
def test_validate_oauth_flow(connector_spec, expected_error):
    t = _TestSpec()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t.test_oauth_flow_parameters(connector_spec)
    else:
        t.test_oauth_flow_parameters(connector_spec)


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
    "connector_spec, should_fail",
    (
        (
            {"type": "object", "properties": {"api_token": {"type": "string", "airbyte_secret": True}}},
            False,
        ),
        ({"type": "object", "properties": {"api_token": {"type": "null"}}}, False),
        ({"type": "object", "properties": {"refresh_token": {"type": "boolean", "airbyte_secret": True}}}, True),
        ({"type": "object", "properties": {"refresh_token": {"type": ["null", "string"]}}}, True),
        ({"type": "object", "properties": {"credentials": {"type": "array", "items": {"type": "string"}}}}, True),
        ({"type": "object", "properties": {"auth": {"oneOf": [{"api_token": {"type": "string"}}]}}}, True),
        (
            {
                "type": "object",
                "properties": {"credentials": {"oneOf": [{"type": "object", "properties": {"api_key": {"type": "string"}}}]}},
            },
            True,
        ),
        ({"type": "object", "properties": {"start_date": {"type": ["null", "string"]}}}, False),
        ({"type": "object", "properties": {"credentials": {"oneOf": [{"type": "string", "const": "OAuth2.0"}]}}}, False),
    ),
)
def test_airbyte_secret(mocker, connector_spec, should_fail):
    mocker.patch.object(conftest.pytest, "fail")
    t = _TestSpec()
    logger = mocker.Mock()
    t.test_secret_is_properly_marked(
        {"connectionSpecification": connector_spec}, logger, ("api_key", "api_token", "refresh_token", "jwt", "credentials")
    )
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "connector_spec, should_fail",
    (
        ({"type": "object", "properties": {"refresh_token": {"type": ["boolean", "string"]}}}, True),
        ({"type": "object", "properties": {"refresh_token": {"type": []}}}, True),
        ({"type": "object", "properties": {"refresh_token": {"type": ["string"]}}}, False),
        ({"type": "object", "properties": {"refresh_token": {"type": "string"}}}, False),
        ({"type": "object", "properties": {"refresh_token": {"type": ["boolean", "null"]}}}, False),
    ),
)
def test_property_type_is_not_array(mocker, connector_spec, should_fail):
    mocker.patch.object(conftest.pytest, "fail")
    t = _TestSpec()
    t.test_property_type_is_not_array(ConnectorSpecification(connectionSpecification=connector_spec))
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "connector_spec, should_fail",
    (
        ({"type": "object", "properties": {"refresh_token": {"type": "boolean", "airbyte_secret": True}}}, False),
        ({"type": "object", "properties": {}}, False),
        ({"type": "object", "properties": {"jwt": {"type": "object"}}}, True),
        (
            {
                "type": "object",
                "properties": {
                    "jwt": {
                        "type": "object",
                        "oneOf": [
                            {"type": "object", "properties": {"a": {"type": "string"}}},
                            {"type": "object", "properties": {"b": {"type": "string"}}},
                        ],
                    }
                },
            },
            False,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "jwt": {
                        "type": "object",
                        "oneOf": [
                            {"type": "object", "properties": {"a": {"type": "string"}}},
                            {"type": "object", "properties": {"b": {"type": "string"}}},
                            {"type": "object", "properties": {}},
                        ],
                    }
                },
            },
            True,
        ),
        ({"type": "object", "properties": {"jwt": {"type": "object", "properties": {}}}}, True),
    ),
)
def test_object_not_empty(mocker, connector_spec, should_fail):
    mocker.patch.object(conftest.pytest, "fail")
    t = _TestSpec()
    t.test_object_not_empty(ConnectorSpecification(connectionSpecification=connector_spec))
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "connector_spec, should_fail",
    (
        ({"type": "object", "properties": {"list": {"type": "array"}}}, False),
        ({"type": "object", "properties": {"list": {"type": "array", "items": [{"type": "string"}, {"type": "boolean"}]}}}, True),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "string"}}}}, False),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "number"}}}}, False),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "integer"}}}}, False),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "boolean"}}}}, True),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "number", "enum": [1, 2, 3]}}}}, False),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"enum": ["a", "b", "c"]}}}}, False),
        (
            {
                "type": "object",
                "properties": {"list": {"type": "array", "items": {"type": "object", "properties": {"a": {"type": "string"}}}}},
            },
            False,
        ),
        ({"type": "object", "properties": {"list": {"type": "array", "items": {"type": "boolean"}}}}, True),
    ),
)
def test_array_type(mocker, connector_spec, should_fail):
    mocker.patch.object(conftest.pytest, "fail")
    t = _TestSpec()
    t.test_array_type(ConnectorSpecification(connectionSpecification=connector_spec))
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "connector_spec, should_fail",
    (
        ({"type": "object", "properties": {"a": {"type": "string"}}}, False),
        ({"type": "object", "properties": {"a": {"type": "string", "allOf": [{"type": "string"}, {"maxLength": 5}]}}}, True),
        ({"type": "object", "properties": {"allOf": {"type": "string"}}}, False),
        (
            {
                "type": "object",
                "properties": {"allOf": {"type": "object", "patternProperties": {"^S_": {"type": "string"}, "^I_": {"type": "integer"}}}},
            },
            True,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "list": {
                        "type": "array",
                        "prefixItems": [{"enum": ["Street", "Avenue", "Boulevard"]}, {"enum": ["NW", "NE", "SW", "SE"]}],
                    }
                },
            },
            True,
        ),
    ),
)
def test_forbidden_complex_types(mocker, connector_spec, should_fail):
    mocker.patch.object(conftest.pytest, "fail")
    t = _TestSpec()
    t.test_forbidden_complex_types(ConnectorSpecification(connectionSpecification=connector_spec))
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "connector_spec, is_warning_logged",
    (
        ({"type": "object", "properties": {"date": {"type": "string"}}}, False),
        ({"type": "object", "properties": {"date": {"type": "string", "format": "date"}}}, True),
        ({"type": "object", "properties": {"date": {"type": "string", "format": "date-time"}}}, True),
        (
            {"type": "object", "properties": {"date": {"type": "string", "format": "date", "pattern": "^[0-9]{2}-[0-9]{2}-[0-9]{4}$"}}},
            False,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "format": "date-time",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?$",
                    }
                },
            },
            False,
        ),
        ({"type": "object", "properties": {"date": {"type": "string", "pattern": "^[0-9]{2}-[0-9]{2}-[0-9]{4}$"}}}, False),
        (
            {
                "type": "object",
                "properties": {"date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?$"}},
            },
            False,
        ),
    ),
)
def test_date_pattern(mocker, connector_spec, is_warning_logged):
    mocker.patch.object(conftest.pytest, "fail")
    logger = mocker.Mock()
    t = _TestSpec()
    t.test_date_pattern(ConnectorSpecification(connectionSpecification=connector_spec), logger)
    conftest.pytest.fail.assert_not_called()
    if is_warning_logged:
        _, args, _ = logger.warning.mock_calls[0]
        msg, *_ = args
        assert "Consider setting the pattern" in msg


@pytest.mark.parametrize(
    "connector_spec, is_warning_logged",
    (
        ({"type": "object", "properties": {"date": {"type": "string"}}}, False),
        ({"type": "object", "properties": {"format": {"type": "string"}}}, False),
        ({"type": "object", "properties": {"date": {"type": "string", "pattern": "[a-z]*"}}}, False),
        (
            {"type": "object", "properties": {"date": {"type": "string", "format": "date", "pattern": "^[0-9]{2}-[0-9]{2}-[0-9]{4}$"}}},
            False,
        ),
        (
            {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "format": "date-time",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?$",
                    }
                },
            },
            False,
        ),
        ({"type": "object", "properties": {"date": {"type": "string", "pattern": "^[0-9]{2}-[0-9]{2}-[0-9]{4}$"}}}, True),
        (
            {
                "type": "object",
                "properties": {"date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?$"}},
            },
            True,
        ),
    ),
)
def test_date_format(mocker, connector_spec, is_warning_logged):
    mocker.patch.object(conftest.pytest, "fail")
    logger = mocker.Mock()
    t = _TestSpec()
    t.test_date_format(ConnectorSpecification(connectionSpecification=connector_spec), logger)
    conftest.pytest.fail.assert_not_called()
    if is_warning_logged:
        _, args, _ = logger.warning.mock_calls[0]
        msg, *_ = args
        assert "Consider specifying the format" in msg


@pytest.mark.parametrize(
    "path, expected_name, expected_result",
    (
        ("properties/api_key/type", "api_key", True),
        ("properties/start_date/type", "start_date", False),
        ("properties/credentials/oneOf/1/properties/api_token/type", "api_token", True),
        ("properties/type", None, False),  # root element
        ("properties/accounts/items/2/properties/jwt/type", "jwt", True),
    ),
)
def test_is_spec_property_name_secret(path, expected_name, expected_result):
    t = _TestSpec()
    assert t._is_spec_property_name_secret(path, ("api_key", "api_token", "refresh_token", "jwt", "credentials")) == (
        expected_name,
        expected_result,
    )


@pytest.mark.parametrize(
    "property_def, can_store_secret",
    (
        ({"type": "boolean"}, False),
        ({"type": "null"}, False),
        ({"type": "string"}, True),
        ({"type": "integer"}, True),
        ({"type": "number"}, True),
        ({"type": ["null", "string"]}, True),
        ({"type": ["null", "boolean"]}, False),
        ({"type": "object"}, False),
        ({"type": "object", "properties": {"api_key": {}}}, False),
        ({"type": "array"}, False),
        ({"type": "array", "items": {"type": "string"}}, False),
        ({"type": "string", "const": "OAuth2.0"}, False),
    ),
)
def test_property_can_store_secret(property_def, can_store_secret):
    t = _TestSpec()
    assert t._property_can_store_secret(property_def) is can_store_secret
