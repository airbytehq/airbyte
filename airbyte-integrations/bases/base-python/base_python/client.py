"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import json
import pkgutil
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Generator, Tuple

from airbyte_protocol import AirbyteRecordMessage, AirbyteStream


def package_name_from_class(cls: object) -> str:
    """Find the package name given a class name"""
    module = inspect.getmodule(cls)
    return module.__name__.split(".")[0]


class ResourceSchemaLoader:
    """JSONSchema loader from package resources"""

    def __init__(self, package_name: str):
        self.package_name = package_name

    def get_schema(self, name: str) -> dict:
        raw_schema = json.loads(pkgutil.get_data(self.package_name, f"schemas/{name}.json"))
        return raw_schema


class BaseClient(ABC):
    """Base client for API"""

    schema_loader_class = ResourceSchemaLoader

    def __init__(self):
        package_name = package_name_from_class(self.__class__)
        self._schema_loader = self.schema_loader_class(package_name)
        self._stream_methods = self._enumerate_methods()

    def _enumerate_methods(self) -> Dict[str, callable]:
        """Detect available streams and return mapping"""
        prefix = "stream__"
        mapping = {}
        methods = inspect.getmembers(self.__class__, predicate=inspect.isfunction)
        for name, method in methods:
            if name.startswith(prefix):
                mapping[name[len(prefix) :]] = method

        return mapping

    def read_stream(self, stream: AirbyteStream) -> Generator[AirbyteRecordMessage, None, None]:
        """Yield records from stream"""
        method = self._stream_methods.get(stream.name)
        if not method:
            raise ValueError(f"Client does not know how to read stream `{stream.name}`")

        for message in method():
            now = int(datetime.now().timestamp()) * 1000
            yield AirbyteRecordMessage(stream=stream.name, data=message, emitted_at=now)

    @property
    def streams(self) -> Generator[AirbyteStream, None, None]:
        """List of available streams"""
        for name, method in self._stream_methods.items():
            yield AirbyteStream(name=name, json_schema=self._schema_loader.get_schema(name))

    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """Check if service is up and running"""
