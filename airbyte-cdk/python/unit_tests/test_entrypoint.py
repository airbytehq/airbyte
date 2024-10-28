#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from argparse import Namespace
from collections import defaultdict
from copy import deepcopy
from typing import Any, List, Mapping, MutableMapping, Union
from unittest import mock
from unittest.mock import MagicMock, patch

import freezegun
import pytest
import requests
from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk import entrypoint as entrypoint_module
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateStats,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConnectorSpecification,
    FailureType,
    OrchestratorType,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_cdk.utils import AirbyteTracedException
from orjson import orjson


class MockSource(Source):
    def read(self, **kwargs):
        pass

    def discover(self, **kwargs):
        pass

    def check(self, **kwargs):
        pass

    @property
    def message_repository(self):
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


MESSAGE_FROM_REPOSITORY = AirbyteMessage(
    type=Type.CONTROL,
    control=AirbyteControlMessage(
        type=OrchestratorType.CONNECTOR_CONFIG,
        emitted_at=10,
        connectorConfig=AirbyteControlConnectorConfigMessage(config={"any config": "a config value"}),
    ),
)


@pytest.fixture
def entrypoint(mocker) -> AirbyteEntrypoint:
    message_repository = MagicMock()
    message_repository.consume_queue.side_effect = [[message for message in [MESSAGE_FROM_REPOSITORY]], [], []]
    mocker.patch.object(MockSource, "message_repository", new_callable=mocker.PropertyMock, return_value=message_repository)
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
    elif isinstance(submessage, AirbyteTraceMessage):
        message = AirbyteMessage(type=Type.TRACE, trace=submessage)
    else:
        raise Exception(f"Unknown message type: {submessage}")

    return orjson.dumps(AirbyteMessageSerializer.dump(message)).decode()


def test_run_spec(entrypoint: AirbyteEntrypoint, mocker):
    parsed_args = Namespace(command="spec")
    expected = ConnectorSpecification(connectionSpecification={"hi": "hi"})
    mocker.patch.object(MockSource, "spec", return_value=expected)

    messages = list(entrypoint.run(parsed_args))

    assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(), _wrap_message(expected)] == messages


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
        assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(), _wrap_message(check_value)] == messages
    else:
        assert len(messages) == 2
        assert messages[0] == orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode()
        connection_status_message = AirbyteMessage(**orjson.loads(messages[1]))
        assert connection_status_message.type == Type.CONNECTION_STATUS.value
        assert connection_status_message.connectionStatus.get("status") == Status.FAILED.value
        assert connection_status_message.connectionStatus.get("message").startswith("Config validation error:")


def test_run_check(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="check", config="config_path")
    check_value = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    mocker.patch.object(MockSource, "check", return_value=check_value)

    messages = list(entrypoint.run(parsed_args))

    assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(), _wrap_message(check_value)] == messages
    assert spec_mock.called


@freezegun.freeze_time("1970-01-01T00:00:00.001Z")
def test_run_check_with_exception(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    exception = ValueError("Any error")
    parsed_args = Namespace(command="check", config="config_path")
    mocker.patch.object(MockSource, "check", side_effect=exception)

    with pytest.raises(ValueError):
        list(entrypoint.run(parsed_args))


@freezegun.freeze_time("1970-01-01T00:00:00.001Z")
def test_run_check_with_traced_exception(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    exception = AirbyteTracedException.from_exception(ValueError("Any error"))
    parsed_args = Namespace(command="check", config="config_path")
    mocker.patch.object(MockSource, "check", side_effect=exception)

    with pytest.raises(AirbyteTracedException):
        list(entrypoint.run(parsed_args))


@freezegun.freeze_time("1970-01-01T00:00:00.001Z")
def test_run_check_with_config_error(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    exception = AirbyteTracedException.from_exception(ValueError("Any error"))
    exception.failure_type = FailureType.config_error
    parsed_args = Namespace(command="check", config="config_path")
    mocker.patch.object(MockSource, "check", side_effect=exception)

    messages = list(entrypoint.run(parsed_args))
    expected_trace = exception.as_airbyte_message()
    expected_trace.emitted_at = 1
    expected_trace.trace.emitted_at = 1
    expected_messages = [
        orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(),
        orjson.dumps(AirbyteMessageSerializer.dump(expected_trace)).decode(),
        _wrap_message(
            AirbyteConnectionStatus(
                status=Status.FAILED,
                message=AirbyteTracedException.from_exception(exception).message
            )
        ),
    ]
    assert messages == expected_messages


@freezegun.freeze_time("1970-01-01T00:00:00.001Z")
def test_run_check_with_transient_error(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    exception = AirbyteTracedException.from_exception(ValueError("Any error"))
    exception.failure_type = FailureType.transient_error
    parsed_args = Namespace(command="check", config="config_path")
    mocker.patch.object(MockSource, "check", side_effect=exception)

    with pytest.raises(AirbyteTracedException):
        list(entrypoint.run(parsed_args))


def test_run_discover(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="discover", config="config_path")
    expected = AirbyteCatalog(streams=[AirbyteStream(name="stream", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh])])
    mocker.patch.object(MockSource, "discover", return_value=expected)

    messages = list(entrypoint.run(parsed_args))

    assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(), _wrap_message(expected)] == messages
    assert spec_mock.called


def test_run_discover_with_exception(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="discover", config="config_path")
    mocker.patch.object(MockSource, "discover", side_effect=ValueError("Any error"))

    with pytest.raises(ValueError):
        messages = list(entrypoint.run(parsed_args))
        assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode()] == messages


def test_run_read(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="read", config="config_path", state="statepath", catalog="catalogpath")
    expected = AirbyteRecordMessage(stream="stream", data={"data": "stuff"}, emitted_at=1)
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})
    mocker.patch.object(MockSource, "read", return_value=[AirbyteMessage(record=expected, type=Type.RECORD)])

    messages = list(entrypoint.run(parsed_args))

    assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode(), _wrap_message(expected)] == messages
    assert spec_mock.called


def test_given_message_emitted_during_config_when_read_then_emit_message_before_next_steps(
    entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock
):
    parsed_args = Namespace(command="read", config="config_path", state="statepath", catalog="catalogpath")
    mocker.patch.object(MockSource, "read_catalog", side_effect=ValueError)

    messages = entrypoint.run(parsed_args)
    assert next(messages) == orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode()
    with pytest.raises(ValueError):
        next(messages)


def test_run_read_with_exception(entrypoint: AirbyteEntrypoint, mocker, spec_mock, config_mock):
    parsed_args = Namespace(command="read", config="config_path", state="statepath", catalog="catalogpath")
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})
    mocker.patch.object(MockSource, "read", side_effect=ValueError("Any error"))

    with pytest.raises(ValueError):
        messages = list(entrypoint.run(parsed_args))
        assert [orjson.dumps(AirbyteMessageSerializer.dump(MESSAGE_FROM_REPOSITORY)).decode()] == messages


def test_invalid_command(entrypoint: AirbyteEntrypoint, config_mock):
    with pytest.raises(Exception):
        list(entrypoint.run(Namespace(command="invalid", config="conf")))


@pytest.mark.parametrize(
    "deployment_mode, url, expected_error",
    [
        pytest.param("CLOUD", "https://airbyte.com", None, id="test_cloud_public_endpoint_is_successful"),
        pytest.param("CLOUD", "https://192.168.27.30", AirbyteTracedException, id="test_cloud_private_ip_address_is_rejected"),
        pytest.param("CLOUD", "https://localhost:8080/api/v1/cast", AirbyteTracedException, id="test_cloud_private_endpoint_is_rejected"),
        pytest.param("CLOUD", "http://past.lives.net/api/v1/inyun", ValueError, id="test_cloud_unsecured_endpoint_is_rejected"),
        pytest.param("CLOUD", "https://not:very/cash:443.money", ValueError, id="test_cloud_invalid_url_format"),
        pytest.param("CLOUD", "https://192.168.27.30    ", ValueError, id="test_cloud_incorrect_ip_format_is_rejected"),
        pytest.param("cloud", "https://192.168.27.30", AirbyteTracedException, id="test_case_insensitive_cloud_environment_variable"),
        pytest.param("OSS", "https://airbyte.com", None, id="test_oss_public_endpoint_is_successful"),
        pytest.param("OSS", "https://192.168.27.30", None, id="test_oss_private_endpoint_is_successful"),
        pytest.param("OSS", "https://localhost:8080/api/v1/cast", None, id="test_oss_private_endpoint_is_successful"),
        pytest.param("OSS", "http://past.lives.net/api/v1/inyun", None, id="test_oss_unsecured_endpoint_is_successful"),
    ],
)
@patch.object(requests.Session, "send", lambda self, request, **kwargs: requests.Response())
def test_filter_internal_requests(deployment_mode, url, expected_error):
    with mock.patch.dict(os.environ, {"DEPLOYMENT_MODE": deployment_mode}, clear=False):
        AirbyteEntrypoint(source=MockSource())

        session = requests.Session()

        prepared_request = requests.PreparedRequest()
        prepared_request.method = "GET"
        prepared_request.headers = {"header": "value"}
        prepared_request.url = url

        if expected_error:
            with pytest.raises(expected_error):
                session.send(request=prepared_request)
        else:
            actual_response = session.send(request=prepared_request)
            assert isinstance(actual_response, requests.Response)


@pytest.mark.parametrize(
    "incoming_message, stream_message_count, expected_message, expected_records_by_stream",
    [
        pytest.param(
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", data={"id": "12345"}, emitted_at=1)),
            {HashableStreamDescriptor(name="customers"): 100.0},
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", data={"id": "12345"}, emitted_at=1)),
            {HashableStreamDescriptor(name="customers"): 101.0},
            id="test_handle_record_message",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="customers"), stream_state=AirbyteStateBlob(updated_at="2024-02-02")
                    ),
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 100.0},
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="customers"), stream_state=AirbyteStateBlob(updated_at="2024-02-02")
                    ),
                    sourceStats=AirbyteStateStats(recordCount=100.0),
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 0.0},
            id="test_handle_state_message",
        ),
        pytest.param(
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", data={"id": "12345"}, emitted_at=1)),
            defaultdict(float),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", data={"id": "12345"}, emitted_at=1)),
            {HashableStreamDescriptor(name="customers"): 1.0},
            id="test_handle_first_record_message",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="customers"), status=AirbyteStreamStatus.COMPLETE
                    ),
                    emitted_at=1,
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 5.0},
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name="customers"), status=AirbyteStreamStatus.COMPLETE
                    ),
                    emitted_at=1,
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 5.0},
            id="test_handle_other_message_type",
        ),
        pytest.param(
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="others", data={"id": "12345"}, emitted_at=1)),
            {HashableStreamDescriptor(name="customers"): 100.0, HashableStreamDescriptor(name="others"): 27.0},
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="others", data={"id": "12345"}, emitted_at=1)),
            {HashableStreamDescriptor(name="customers"): 100.0, HashableStreamDescriptor(name="others"): 28.0},
            id="test_handle_record_message_for_other_stream",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="others"), stream_state=AirbyteStateBlob(updated_at="2024-02-02")
                    ),
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 100.0, HashableStreamDescriptor(name="others"): 27.0},
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="others"), stream_state=AirbyteStateBlob(updated_at="2024-02-02")
                    ),
                    sourceStats=AirbyteStateStats(recordCount=27.0),
                ),
            ),
            {HashableStreamDescriptor(name="customers"): 100.0, HashableStreamDescriptor(name="others"): 0.0},
            id="test_handle_state_message_for_other_stream",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", namespace="public", data={"id": "12345"}, emitted_at=1)
            ),
            {HashableStreamDescriptor(name="customers", namespace="public"): 100.0},
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="customers", namespace="public", data={"id": "12345"}, emitted_at=1)
            ),
            {HashableStreamDescriptor(name="customers", namespace="public"): 101.0},
            id="test_handle_record_message_with_descriptor",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="customers", namespace="public"),
                        stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
                    ),
                ),
            ),
            {HashableStreamDescriptor(name="customers", namespace="public"): 100.0},
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="customers", namespace="public"),
                        stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
                    ),
                    sourceStats=AirbyteStateStats(recordCount=100.0),
                ),
            ),
            {HashableStreamDescriptor(name="customers", namespace="public"): 0.0},
            id="test_handle_state_message_with_descriptor",
        ),
        pytest.param(
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="others", namespace="public"),
                        stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
                    ),
                ),
            ),
            {HashableStreamDescriptor(name="customers", namespace="public"): 100.0},
            AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="others", namespace="public"),
                        stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
                    ),
                    sourceStats=AirbyteStateStats(recordCount=0.0),
                ),
            ),
            {
                HashableStreamDescriptor(name="customers", namespace="public"): 100.0,
                HashableStreamDescriptor(name="others", namespace="public"): 0.0,
            },
            id="test_handle_state_message_no_records",
        ),
    ],
)
def test_handle_record_counts(incoming_message, stream_message_count, expected_message, expected_records_by_stream):
    entrypoint = AirbyteEntrypoint(source=MockSource())
    actual_message = entrypoint.handle_record_counts(message=incoming_message, stream_message_count=stream_message_count)
    assert actual_message == expected_message

    for stream_descriptor, message_count in stream_message_count.items():
        assert isinstance(message_count, float)
        # Python assertions against different number types won't fail if the value is equivalent
        assert message_count == expected_records_by_stream[stream_descriptor]

    if actual_message.type == Type.STATE:
        assert isinstance(actual_message.state.sourceStats.recordCount, float), "recordCount value should be expressed as a float"
