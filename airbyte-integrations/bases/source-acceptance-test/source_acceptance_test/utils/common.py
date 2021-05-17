#
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
#


from collections import UserDict
from pathlib import Path
from typing import Iterable, List

import pytest
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode
from source_acceptance_test.config import Config


def load_config(path: str) -> Config:
    """Function to load test config, avoid duplication of code in places where we can't use fixture"""
    path = Path(path) / "acceptance-test-config.yml"
    if not path.exists():
        pytest.fail(f"config file {path.absolute()} does not exist")

    with open(str(path), "r") as file:
        data = load(file, Loader=Loader)
        return Config.parse_obj(data)


def full_refresh_only_catalog(configured_catalog: ConfiguredAirbyteCatalog) -> ConfiguredAirbyteCatalog:
    """Transform provided catalog to catalog with all streams configured to use Full Refresh sync (when possible)"""
    streams = []
    for stream in configured_catalog.streams:
        if SyncMode.full_refresh in stream.stream.supported_sync_modes:
            stream.sync_mode = SyncMode.full_refresh
            streams.append(stream)

    configured_catalog.streams = streams
    return configured_catalog


def incremental_only_catalog(configured_catalog: ConfiguredAirbyteCatalog) -> ConfiguredAirbyteCatalog:
    """Transform provided catalog to catalog with all streams configured to use Incremental sync (when possible)"""
    streams = []
    for stream in configured_catalog.streams:
        if SyncMode.incremental in stream.stream.supported_sync_modes:
            stream.sync_mode = SyncMode.incremental
            streams.append(stream)

    configured_catalog.streams = streams
    return configured_catalog


def filter_output(records: Iterable[AirbyteMessage], type_) -> List[AirbyteMessage]:
    """Filter messages to match specific type"""
    return list(filter(lambda x: x.type == type_, records))


class SecretDict(UserDict):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(******)"

    def __repr__(self) -> str:
        return str(self)
