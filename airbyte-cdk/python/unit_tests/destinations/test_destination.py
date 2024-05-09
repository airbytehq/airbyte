#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import io
import json
from os import PathLike
from typing import Any, Dict, Iterable, List, Mapping, Union
from unittest.mock import ANY

import pytest
from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations import destination as destination_module
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


@pytest.fixture(name="destination")
def destination_fixture(mocker) -> Destination:
    # Wipe the internal list of abstract methods to allow instantiating the abstract class without implementing its abstract methods
    mocker.patch("airbyte_cdk.destinations.Destination.__abstractmethods__", set())
    # Mypy yells at us because we're init'ing an abstract class
    return Destination()  # type: ignore


class TestArgParsing:
    @pytest.mark.parametrize(
        ("arg_list", "expected_output"),
        [
            (["spec"], {"command": "spec"}),
            (["check", "--config", "bogus_path/"], {"command": "check", "config": "bogus_path/"}),
            (
                ["write", "--config", "config_path1", "--catalog", "catalog_path1"],
                {"command": "write", "config": "config_path1", "catalog": "catalog_path1"},
            ),
        ],
    )
    def test_successful_parse(self, arg_list: List[str], expected_output: Mapping[str, Any], destination: Destination):
        parsed_args = vars(destination.parse_args(arg_list))
        assert (
            parsed_args == expected_output
        ), f"Expected parsing {arg_list} to return parsed args {expected_output} but instead found {parsed_args}"

    @pytest.mark.parametrize(
        ("arg_list"),
        [
            # Invalid commands
            ([]),
            (["not-a-real-command"]),
            ([""]),
            # Incorrect parameters
            (["spec", "--config", "path"]),
            (["check"]),
            (["check", "--catalog", "path"]),
            (["check", "path"]),
        ],
    )
    def test_failed_parse(self, arg_list: List[str], destination: Destination):
        # We use BaseException because it encompasses SystemExit (raised by failed parsing) and other exceptions (raised by additional semantic
        # checks)
        with pytest.raises(BaseException):
            destination.parse_args(arg_list)


def _state(state: Dict[str, Any]) -> AirbyteStateMessage:
    return AirbyteStateMessage(data=state)


def _record(stream: str, data: Dict[str, Any]) -> AirbyteRecordMessage:
    return AirbyteRecordMessage(stream=stream, data=data, emitted_at=0)


def _spec(schema: Dict[str, Any]) -> ConnectorSpecification:
    return ConnectorSpecification(connectionSpecification=schema)


def write_file(path: PathLike, content: Union[str, Mapping]):
    content = json.dumps(content) if isinstance(content, Mapping) else content
    with open(path, "w") as f:
        f.write(content)


def _wrapped(
    msg: Union[AirbyteRecordMessage, AirbyteStateMessage, AirbyteCatalog, ConnectorSpecification, AirbyteConnectionStatus]
) -> AirbyteMessage:
    if isinstance(msg, AirbyteRecordMessage):
        return AirbyteMessage(type=Type.RECORD, record=msg)
    elif isinstance(msg, AirbyteStateMessage):
        return AirbyteMessage(type=Type.STATE, state=msg)
    elif isinstance(msg, AirbyteCatalog):
        return AirbyteMessage(type=Type.CATALOG, catalog=msg)
    elif isinstance(msg, AirbyteConnectionStatus):
        return AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
    elif isinstance(msg, ConnectorSpecification):
        return AirbyteMessage(type=Type.SPEC, spec=msg)
    else:
        raise Exception(f"Invalid Airbyte Message: {msg}")


class OrderedIterableMatcher(Iterable):
    """
    A class whose purpose is to verify equality of one iterable object against another
    in an ordered fashion
    """

    def attempt_consume(self, iterator):
        try:
            return next(iterator)
        except StopIteration:
            return None

    def __iter__(self):
        return iter(self.iterable)

    def __init__(self, iterable: Iterable):
        self.iterable = iterable

    def __eq__(self, other):
        if not isinstance(other, Iterable):
            return False

        return list(self) == list(other)


class TestRun:
    def test_run_initializes_exception_handler(self, mocker, destination: Destination):
        mocker.patch.object(destination_module, "init_uncaught_exception_handler")
        mocker.patch.object(destination, "parse_args")
        mocker.patch.object(destination, "run_cmd")
        destination.run(["dummy"])
        destination_module.init_uncaught_exception_handler.assert_called_once_with(destination_module.logger)

    def test_run_spec(self, mocker, destination: Destination):
        args = {"command": "spec"}
        parsed_args = argparse.Namespace(**args)

        expected_spec = ConnectorSpecification(connectionSpecification={"json_schema": {"prop": "value"}})
        mocker.patch.object(destination, "spec", return_value=expected_spec, autospec=True)

        spec_message = next(iter(destination.run_cmd(parsed_args)))

        # Mypy doesn't understand magicmock so it thinks spec doesn't have assert_called_once attr
        destination.spec.assert_called_once()  # type: ignore

        # verify the output of spec was returned
        assert spec_message == _wrapped(expected_spec)

    def test_run_check(self, mocker, destination: Destination, tmp_path):
        file_path = tmp_path / "config.json"
        dummy_config = {"user": "sherif"}
        write_file(file_path, dummy_config)
        args = {"command": "check", "config": file_path}

        parsed_args = argparse.Namespace(**args)
        destination.run_cmd(parsed_args)
        spec_msg = ConnectorSpecification(connectionSpecification={})
        mocker.patch.object(destination, "spec", return_value=spec_msg)
        validate_mock = mocker.patch("airbyte_cdk.destinations.destination.check_config_against_spec_or_exit")
        expected_check_result = AirbyteConnectionStatus(status=Status.SUCCEEDED)
        mocker.patch.object(destination, "check", return_value=expected_check_result, autospec=True)

        returned_check_result = next(iter(destination.run_cmd(parsed_args)))
        # verify method call with the correct params
        # Affirm to Mypy that this is indeed a method on this mock
        destination.check.assert_called_once()  # type: ignore
        # Affirm to Mypy that this is indeed a method on this mock
        destination.check.assert_called_with(logger=ANY, config=dummy_config)  # type: ignore
        # Check if config validation has been called
        validate_mock.assert_called_with(dummy_config, spec_msg)

        # verify output was correct
        assert returned_check_result == _wrapped(expected_check_result)

    def test_run_write(self, mocker, destination: Destination, tmp_path, monkeypatch):
        config_path, dummy_config = tmp_path / "config.json", {"user": "sherif"}
        write_file(config_path, dummy_config)

        dummy_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name="mystream", json_schema={"type": "object"}, supported_sync_modes=[SyncMode.full_refresh]),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            ]
        )
        catalog_path = tmp_path / "catalog.json"
        write_file(catalog_path, dummy_catalog.json(exclude_unset=True))

        args = {"command": "write", "config": config_path, "catalog": catalog_path}
        parsed_args = argparse.Namespace(**args)

        expected_write_result = [_wrapped(_state({"k1": "v1"})), _wrapped(_state({"k2": "v2"}))]
        mocker.patch.object(
            destination, "write", return_value=iter(expected_write_result), autospec=True  # convert to iterator to mimic real usage
        )
        spec_msg = ConnectorSpecification(connectionSpecification={})
        mocker.patch.object(destination, "spec", return_value=spec_msg)
        validate_mock = mocker.patch("airbyte_cdk.destinations.destination.check_config_against_spec_or_exit")
        # mock input is a record followed by some state messages
        mocked_input: List[AirbyteMessage] = [_wrapped(_record("s1", {"k1": "v1"})), *expected_write_result]
        mocked_stdin_string = "\n".join([record.json(exclude_unset=True) for record in mocked_input])
        mocked_stdin_string += "\n add this non-serializable string to verify the destination does not break on malformed input"
        mocked_stdin = io.TextIOWrapper(io.BytesIO(bytes(mocked_stdin_string, "utf-8")))

        monkeypatch.setattr("sys.stdin", mocked_stdin)

        returned_write_result = list(destination.run_cmd(parsed_args))
        # verify method call with the correct params
        # Affirm to Mypy that call_count is indeed a method on this mock
        destination.write.assert_called_once()  # type: ignore
        # Affirm to Mypy that call_count is indeed a method on this mock
        destination.write.assert_called_with(  # type: ignore
            config=dummy_config,
            configured_catalog=dummy_catalog,
            # Stdin is internally consumed as a generator so we use a custom matcher
            # that iterates over two iterables to check equality
            input_messages=OrderedIterableMatcher(mocked_input),
        )
        # Check if config validation has been called
        validate_mock.assert_called_with(dummy_config, spec_msg)

        # verify output was correct
        assert returned_write_result == expected_write_result

    @pytest.mark.parametrize("args", [{}, {"command": "fake"}])
    def test_run_cmd_with_incorrect_args_fails(self, args, destination: Destination):
        with pytest.raises(Exception):
            list(destination.run_cmd(parsed_args=argparse.Namespace(**args)))
