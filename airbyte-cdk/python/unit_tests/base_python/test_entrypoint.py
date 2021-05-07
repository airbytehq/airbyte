# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from copy import deepcopy
from typing import Any, List, Mapping

import pytest
from airbyte_cdk.base_python import AirbyteEntrypoint, Source


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
        out.append(v)
    return out


@pytest.fixture
def entrypoint() -> AirbyteEntrypoint:
    return AirbyteEntrypoint(MockSource())


@pytest.mark.parametrize(
    ["cmd", "args"],
    [
        ("spec", dict()),
        ("check", {"config": "config_path"}),
        ("discover", {"config": "config_path"}),
        ("read", {"config": "config_path", "catalog": "catalog_path", "state": "None"}),
        ("read", {"config": "config_path", "catalog": "catalog_path", "state": "state_path"}),
    ],
)
def test_parse_valid_args(cmd: str, args: Mapping[str, Any], entrypoint: AirbyteEntrypoint):
    arglist = _as_arglist(cmd, args)
    parsed_args = entrypoint.parse_args(arglist)
    assert {"command": cmd, **args} == vars(parsed_args)


@pytest.mark.parametrize(
    ["cmd", "args"],
    [
        ("check", {"config": "config_path"}),
        ("discover", {"config": "config_path"}),
        ("read", {"config": "config_path", "catalog": "catalog_path"}),
    ],
)
def test_parse_missing_required_args(cmd: str, args: Mapping[str, Any], entrypoint: AirbyteEntrypoint):
    required_args = {"check": ["config"], "discover": ["config"], "read": ["config", "catalog"]}
    for required_arg in required_args[cmd]:
        argcopy = deepcopy(args)
        del argcopy[required_arg]
        with pytest.raises(BaseException):
            entrypoint.parse_args(_as_arglist(cmd, argcopy))
