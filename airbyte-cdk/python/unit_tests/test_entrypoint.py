#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from argparse import Namespace
from copy import deepcopy
from typing import Any, List, Mapping, MutableMapping, Union
from unittest.mock import MagicMock

import pytest
from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk import entrypoint as entrypoint_module
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConnectorSpecification,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source


class MockSource(Source):
    def read(self, **kwargs):
        pass

    def discover(self, **kwargs):
        pass

    def check(self, **kwargs):
        pass


def _as_arglist(cmd: str, named_args: Mapping[str, Any]) -> List[str]:
    out = [cmd]
    for k, v in named_args.items():
        out.append(f"--{k}")
        if v:
            out.append(v)
    return out


@pytest.fixture
def spec_mock(mocker):
    expected = ConnectorSpecification(connectionSpecification={})
    mock = MagicMock(return_value=expected)
    mocker.patch.object(MockSource, "spec", mock)
    return mock


@pytest.fixture
def entrypoint() -> AirbyteEntrypoint:
    return AirbyteEntrypoint(MockSource())


def test_airbyte_entrypoint_init(mocker):
    mocker.patch.object(entrypoint_module, "init_uncaught_exception_handler")
    AirbyteEntrypoint(MockSource())
    entrypoint_module.init_uncaught_exception_handler.assert_called_once_with(entrypoint_module.logger)


@pytest.mark.parametrize(
    ["cmd", "args", "expected_args"],
    [
        ("spec", {"debug": ""}, {"command": "spec", "debug": True}),
        ("check", {"config": "config_path"}, {"command": "check", "config": "config_path", "debug": False}),
        ("discover", {"config": "config_path", "debug": ""}, {"command": "discover", "config": "config_path", "debug": True}),
        (
            "read",
            {"config": "config_path", "catalog": "catalog_path", "state": "None"},
            {"command": "read", "config": "config_path", "catalog": "catalog_path", "state": "None", "debug": False},
        ),
        (
            "read",
            {"config": "config_path", "catalog": "catalog_path", "state": "state_path", "debug": ""},
            {"command": "read", "config": "config_path", "catalog": "catalog_path", "state": "state_path", "debug": True},
        ),
    ],
)
def test_parse_valid_args(cmd: str, args: Mapping[str, Any], expected_args, entrypoint: AirbyteEntrypoint):
    arglist = _as_arglist(cmd, args)
    parsed_args = entrypoint.parse_args(arglist)
    assert vars(parsed_args) == expected_args


@pytest.mark.parametrize(
    ["cmd", "args"],
    [
        ("check", {"config": "config_path"}),
        ("discover", {"config": "config_path"}),
        ("read", {"config": "config_path", "catalog": "catalog_path"}),
    ],
)
def test_parse_missing_required_args(cmd: str, args: MutableMapping[str, Any], entrypoint: AirbyteEntrypoint):
    required_args = {"check": ["config"], "discover": ["config"], "read": ["config", "catalog"]}
    for required_arg in required_args[cmd]:
        argcopy = deepcopy(args)
        del argcopy[required_arg]
        with pytest.raises(BaseException):
            entrypoint.parse_args(_as_arglist(cmd, argcopy))


def _wrap_message(submessage: Union[AirbyteConnectionStatus, ConnectorSpecification, AirbyteRecordMessage, AirbyteCatalog]) -> str:
    if isinstance(submessage, AirbyteConnectionStatus):
        message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=submessage)
    elif isinstance(submessage, ConnectorSpecification):
        message = AirbyteMessage(type=Type.SPEC, spec=submessage)
    elif isinstance(submessage, AirbyteCatalog):
        message = AirbyteMessage(type=Type.CATALOG, catalog=submessage)
    elif isinstance(submessage, AirbyteRecordMessage):
        message = AirbyteMessage(type=Type.RECORD, record=submessage)
    else:
        raise Exception(f"Unknown message type: {submessage}")

    return message.json(exclude_unset=True)


def test_run_spec(entrypoint: AirbyteEntrypoint, mocker):
    parsed_args = Namespace(command="spec")
    expected = ConnectorSpecification(connectionSpecification={"hi": "hi"})
    mocker.patch.object(MockSource, "spec", return_value=expected)
    assert [_wrap_message(expected)] == list(entrypoint.run(parsed_args))


@pytest.fixture
def config_mock(mocker, request):
    config = request.param if hasattr(request, "param") else {"username": "fake"}
    mocker.patch.object(MockSource, "read_config", return_value=config)
    mocker.patch.object(MockSource, "configure", return_value=config)
    return config


@pytest.mark.parametrize(
    "config_mock, schema, config_valid",
    [
        ({"username": "fake"}, {"type": "object", "properties": {"name": {"type": "string"}}, "additionalProperties": False}, False),
        ({"username": "fake"}, {"type": "object", "properties": {"username": {"type": "string"}}, "additionalProperties": False}, True),
        ({"username": "fake"}, {"type": "object", "properties": {"user": {"type": "string"}}}, True),
        ({"username": "fake"}, {"type": "object", "properties": {"user": {"type": "string", "airbyte_secret": True}}}, True),
        (
            {"username": "fake", "_limit": 22},
            {"type": "object", "properties": {"username": {"type": "string"}}, "additionalProperties": False},
            True,
        ),
    ],
    indirect=["config_mock"],
)
def test_config_validate(entrypoint: AirbyteEntrypoint, mocker, config_mock, schema, config_valid):
    parsed_args = Namespace(command="check", config="config_path")
    check_value = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    mocker.patch.object(MockSource, "check", return_value=check_value)
    mocker.patch.object(MockSource, "spec", return_value=ConnectorSpecification(connectionSpecification=schema))

    messages = list(entrypoint.run(parsed_args))
    if config_valid:
        assert [_wrap_message(check_value)] == messages
    else:
        assert len(messages) == 1
        airbyte_message = AirbyteMessage.parse_raw(messages[0])
        assert airbyte_message.type == Type.CONNECTION_STATUS
        assert airbyte_message.connectionStatus.status == Status.FAILED
        assert airbyte_message.connectionStatus.message.startswith("Config validation error:")


def test_run_check(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="check", config="config_path")
    check_value = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    mocker.patch.object(MockSource, "check", return_value=check_value)
    assert [_wrap_message(check_value)] == list(entrypoint.run(parsed_args))
    assert spec_mock.called


def test_run_discover(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="discover", config="config_path")
    expected = AirbyteCatalog(streams=[AirbyteStream(name="stream", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh])])
    mocker.patch.object(MockSource, "discover", return_value=expected)
    assert [_wrap_message(expected)] == list(entrypoint.run(parsed_args))
    assert spec_mock.called


def test_run_read(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="read", config="config_path", state="statepath", catalog="catalogpath")
    expected = AirbyteRecordMessage(stream="stream", data={"data": "stuff"}, emitted_at=1)
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})
    mocker.patch.object(MockSource, "read", return_value=[AirbyteMessage(record=expected, type=Type.RECORD)])
    assert [_wrap_message(expected)] == list(entrypoint.run(parsed_args))
    assert spec_mock.called


def test_invalid_command(entrypoint: AirbyteEntrypoint, mocker, config_mock):
    with pytest.raises(Exception):
        list(entrypoint.run(Namespace(command="invalid", config="conf")))
