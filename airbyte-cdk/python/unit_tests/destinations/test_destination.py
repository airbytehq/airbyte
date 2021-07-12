from typing import Any, Mapping, List

import pytest

from airbyte_cdk.destinations import Destination


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
            (['write', '--config', 'config_path1', '--catalog', 'catalog_path1'], {'command': 'write', 'config': 'config_path1', 'catalog': 'catalog_path1'}),
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
            # (['not-a-real-command']),
            # (['']),
            # # Incorrect parameters
            # (['spec', '--config', 'path']),
            # (['check']),
            # (['check', '--catalog', 'path']),
            # (['check', 'path'])
        ]
    )
    def test_failed_parse(self, arg_list: List[str], destination: Destination):
        with pytest.raises(SystemExit):
            destination.parse_args(arg_list)
