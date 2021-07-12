import argparse
from typing import Any, Mapping, List, Union, Dict

import pytest

from airbyte_cdk import AirbyteSpec
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteRecordMessage, AirbyteStateMessage, AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, Type, \
    ConnectorSpecification


@pytest.fixture
def destination(mocker) -> Destination:
    # Wipe the internal list of abstract methods to allow instantiating the abstract class without implementing its abstract methods
    mocker.patch('airbyte_cdk.destinations.Destination.__abstractmethods__', set())
    return Destination()


class TestArgParsing:
    @pytest.mark.parametrize(
        ('arg_list', 'expected_output'),
        [
            (['spec'], {'command': 'spec'}),
            (['check', '--config', 'bogus_path/'], {'command': 'check', 'config': 'bogus_path/'}),
            (['write', '--config', 'config_path1', '--catalog', 'catalog_path1'],
             {'command': 'write', 'config': 'config_path1', 'catalog': 'catalog_path1'}),
        ]
    )
    def test_successful_parse(self, arg_list: List[str], expected_output: Mapping[str, Any], destination: Destination):
        parsed_args = vars(destination.parse_args(arg_list))
        assert parsed_args == expected_output, f"Expected parsing {arg_list} to return parsed args {expected_output} but instead found {parsed_args}"

    @pytest.mark.parametrize(
        ('arg_list'),
        [
            # Invalid commands
            ([]),
            (['not-a-real-command']),
            (['']),
            # Incorrect parameters
            (['spec', '--config', 'path']),
            (['check']),
            (['check', '--catalog', 'path']),
            (['check', 'path'])
        ]
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
        return AirbyteMessage(type=Type.CONNECTION_STATUS, )
    elif isinstance(msg, ConnectorSpecification):
        return AirbyteMessage(type=Type.SPEC, spec=msg)
    else:
        raise Exception(f"Invalid Airbyte Message: {msg}")


class TestRun:
    def test_run_spec(self, mocker, destination: Destination):
        args = {'command': 'spec'}
        parsed_args = argparse.Namespace(**args)
        destination.run_cmd(parsed_args)

        mocker.patch.object(destination, 'spec', return_value=ConnectorSpecification(connectionSpecification={'json_schema': {'prop': 'value'}}))

        # verify spec was called

        # verify the output of spec was returned
