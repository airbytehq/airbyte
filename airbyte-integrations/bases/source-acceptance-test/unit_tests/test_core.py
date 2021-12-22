#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    Type,
)
from source_acceptance_test.config import BasicReadTestConfig
from source_acceptance_test.tests.test_core import TestBasicRead as _TestBasicRead
from source_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery
from source_acceptance_test.tests.test_core import TestSpec as _TestSpec


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


@pytest.mark.parametrize(
    "schema, cursors, should_fail",
    [
        ({}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["created"], False),
        ({"properties": {"created_at": {"type": "string"}}}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["updated", "created"], True),
        ({"properties": {"updated": {"type": "object", "properties": {"created": {"type": "string"}}}}}, ["updated", "created"], False),
        ({"properties": {"created": {"type": "object", "properties": {"updated": {"type": "string"}}}}}, ["updated", "created"], True),
    ],
)
def test_discovery(schema, cursors, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "default_cursor_field": cursors})
    }
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_cursors_exist_in_schema(None, discovered_catalog)
    else:
        t.test_defined_cursors_exist_in_schema(None, discovered_catalog)


@pytest.mark.parametrize(
    "schema, should_fail",
    [
        ({}, False),
        ({"$ref": None}, True),
        ({"properties": {"user": {"$ref": None}}}, True),
        ({"properties": {"user": {"$ref": "user.json"}}}, True),
        ({"properties": {"user": {"type": "object", "properties": {"username": {"type": "string"}}}}}, False),
        ({"properties": {"fake_items": {"type": "array", "items": {"$ref": "fake_item.json"}}}}, True),
        (
            {
                "properties": {
                    "fake_items": {
                        "oneOf": [{"type": "object", "$ref": "fake_items_1.json"}, {"type": "object", "$ref": "fake_items_2.json"}]
                    }
                }
            },
            True,
        ),
    ],
)
def test_ref_in_discovery_schemas(schema, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {"test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema})}
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_refs_exist_in_schema(None, discovered_catalog)
    else:
        t.test_defined_refs_exist_in_schema(None, discovered_catalog)


@pytest.mark.parametrize(
    "schema, record, should_fail",
    [
        ({"type": "object"}, {"aa": 23}, False),
        ({"type": "object"}, {}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"aa": 23}, True),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"root": {"created": "23"}}, True),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            False,
        ),
    ],
)
def test_read(schema, record, should_fail):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    input_config = BasicReadTestConfig()
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = _TestBasicRead()
    if should_fail:
        with pytest.raises(AssertionError, match="stream should have some fields mentioned by json schema"):
            t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())
    else:
        t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())


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
    "records, configured_catalog, expected_error",
    [
        (
            [AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111)],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {"name": "test1", "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}}}}
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111)],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}, "f2": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f2'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {"type": "object", "properties": {"f1": {"type": "string"}, "f2": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": [1, 2, 3]}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "array", "items": {"type": "integer"}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": []}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "array", "items": {"type": "integer"}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [1, 2]}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "object", "properties": {"f4": {"type": "string"}, "f5": {"type": "array"}}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {"type": "object", "properties": {"f4": {"type": "string"}, "f5": {"type": "array"}}},
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/f5/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    )
                ]
            ),
            r"`test1` stream has `\['/f3/f5/\[\]/f6', '/f3/f5/\[\]/f7/\[\]'\]`",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(
                    stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [{"f6": "v6", "f7": ["a", "b"]}]}}, emitted_at=111
                ),
                AirbyteRecordMessage(stream="test2", data={"f8": "v8"}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={"f9": "v9"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test2",
                                "json_schema": {"type": "object", "properties": {"f8": {"type": "string"}, "f9": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f2": "v2", "f3": {"f4": "v4", "f5": [{"f6": "v6", "f7": []}]}}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test2", data={"f9": "v9"}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "type": "object",
                                            "properties": {
                                                "f4": {"type": "string"},
                                                "f5": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "f6": {"type": "string"},
                                                            "f7": {"type": "array"},
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test2",
                                "json_schema": {"type": "object", "properties": {"f8": {"type": "string"}, "f9": {"type": "string"}}},
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            r"(`test1` stream has `\['/f3/f5/\[\]/f7/\[\]']`)|(`test2` `\['/f8'\]`)",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f4": "v4"}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {"type": "object", "properties": {"f5": {"type": "array"}}},
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f5": {"f7": "v7"}}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "f5": {
                                                            "oneOf": [
                                                                {"type": "object", "properties": {"f6": {"type": "string"}}},
                                                                {"type": "object", "properties": {"f7": {"type": "string"}}},
                                                            ]
                                                        }
                                                    },
                                                },
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            "",
        ),
        (
            [
                AirbyteRecordMessage(stream="test1", data={"f1": "v1", "f2": "v2"}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={}, emitted_at=111),
                AirbyteRecordMessage(stream="test1", data={"f3": {"f5": {}}}, emitted_at=111),
            ],
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream.parse_obj(
                            {
                                "name": "test1",
                                "json_schema": {
                                    "type": "object",
                                    "properties": {
                                        "f1": {"type": "string"},
                                        "f2": {"type": "string"},
                                        "f3": {
                                            "oneOf": [
                                                {"type": "object", "properties": {"f4": {"type": "string"}}},
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "f5": {
                                                            "anyOf": [
                                                                {"type": "object", "properties": {"f6": {"type": "string"}}},
                                                                {"type": "object", "properties": {"f7": {"type": "string"}}},
                                                            ]
                                                        }
                                                    },
                                                },
                                            ]
                                        },
                                    },
                                },
                            }
                        ),
                        sync_mode="full_refresh",
                        destination_sync_mode="overwrite",
                    ),
                ]
            ),
            r"`test1` stream has `\['/f3\(0\)/f4', '/f3\(1\)/f5\(0\)/f6', '/f3\(1\)/f5\(1\)/f7'\]`",
        ),
    ],
)
def test_validate_field_appears_at_least_once(records, configured_catalog, expected_error):
    t = _TestBasicRead()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
    else:
        t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)
