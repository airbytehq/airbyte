from copy import deepcopy
from typing import Mapping, Any, List

import pytest

from airbyte_cdk.base_python import Source, AirbyteEntrypoint


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
        out.append(f'--{k}')
        out.append(v)
    return out


@pytest.fixture
def entrypoint() -> AirbyteEntrypoint:
    return AirbyteEntrypoint(MockSource())


@pytest.mark.parametrize(["cmd", "args"], [
    ("spec", dict()),
    ("check", {"config": "config_path"}),
    ("discover", {"config": "config_path"}),
    ("read", {"config": "config_path", "catalog": "catalog_path", "state": 'None'}),
    ("read", {"config": "config_path", "catalog": "catalog_path", "state": "state_path"})
])
def test_parse_valid_args(cmd: str, args: Mapping[str, Any], entrypoint: AirbyteEntrypoint):
    arglist = _as_arglist(cmd, args)
    parsed_args = entrypoint.parse_args(arglist)
    assert {"command": cmd, **args} == vars(parsed_args)


@pytest.mark.parametrize(["cmd", "args"], [
    ("check", {"config": "config_path"}),
    ("discover", {"config": "config_path"}),
    ("read", {"config": "config_path", "catalog": "catalog_path"})
])
def test_parse_missing_required_args(cmd: str, args: Mapping[str, Any], entrypoint: AirbyteEntrypoint):
    required_args = {
        'check': ['config'],
        'discover': ['config'],
        'read': ['config', 'catalog']
    }
    for required_arg in required_args[cmd]:
        argcopy = deepcopy(args)
        del argcopy[required_arg]
        with pytest.raises(BaseException):
            entrypoint.parse_args(_as_arglist(cmd, argcopy))
