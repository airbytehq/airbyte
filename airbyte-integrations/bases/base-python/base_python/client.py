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
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generator, List, Mapping, Tuple

import pkg_resources
from airbyte_protocol import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode
from jsonschema import RefResolver


def package_name_from_class(cls: object) -> str:
    """Find the package name given a class name"""
    module = inspect.getmodule(cls)
    return module.__name__.split(".")[0]


class JsonSchemaResolver:
    """Helper class to expand $ref items in json schema"""

    def __init__(self, shared_schemas_path: str):
        self._shared_refs = self._load_shared_schema_refs(shared_schemas_path)

    @staticmethod
    def _load_shared_schema_refs(path: str):
        shared_file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        shared_schema_refs = {}
        for shared_file in shared_file_names:
            with open(os.path.join(path, shared_file)) as data_file:
                shared_schema_refs[shared_file] = json.load(data_file)

        return shared_schema_refs

    def _resolve_schema_references(self, schema: dict, resolver: RefResolver) -> dict:
        if "$ref" in schema:
            reference_path = schema.pop("$ref", None)
            resolved = resolver.resolve(reference_path)[1]
            schema.update(resolved)
            return self._resolve_schema_references(schema, resolver)

        if "properties" in schema:
            for k, val in schema["properties"].items():
                schema["properties"][k] = self._resolve_schema_references(val, resolver)

        if "patternProperties" in schema:
            for k, val in schema["patternProperties"].items():
                schema["patternProperties"][k] = self._resolve_schema_references(val, resolver)

        if "items" in schema:
            schema["items"] = self._resolve_schema_references(schema["items"], resolver)

        if "anyOf" in schema:
            for i, element in enumerate(schema["anyOf"]):
                schema["anyOf"][i] = self._resolve_schema_references(element, resolver)

        return schema

    def resolve(self, schema: dict, refs: Dict[str, dict] = None) -> dict:
        """Resolves and replaces json-schema $refs with the appropriate dict.
        Recursively walks the given schema dict, converting every instance
        of $ref in a 'properties' structure with a resolved dict.
        This modifies the input schema and also returns it.
        Arguments:
            schema:
                the schema dict
            refs:
                a dict of <string, dict> which forms a store of referenced schemata
        Returns:
            schema
        """
        refs = refs or {}
        refs = {**self._shared_refs, **refs}
        return self._resolve_schema_references(schema, RefResolver("", schema, store=refs))


class ResourceSchemaLoader:
    """JSONSchema loader from package resources"""

    def __init__(self, package_name: str):
        self.package_name = package_name

    def get_schema(self, name: str) -> dict:
        raw_schema = json.loads(pkgutil.get_data(self.package_name, f"schemas/{name}.json"))
        shared_schemas_folder = pkg_resources.resource_filename(self.package_name, "schemas/shared/")
        if os.path.exists(shared_schemas_folder):
            return JsonSchemaResolver(shared_schemas_folder).resolve(raw_schema)
        return raw_schema


class StreamStateMixin:
    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        raise NotImplementedError

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        raise NotImplementedError

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return False


class BaseClient(StreamStateMixin, ABC):
    """Base client for API"""

    schema_loader_class = ResourceSchemaLoader

    def __init__(self, **kwargs):
        package_name = package_name_from_class(self.__class__)
        self._schema_loader = self.schema_loader_class(package_name)
        self._stream_methods = self._enumerate_methods()

    def _enumerate_methods(self) -> Mapping[str, callable]:
        """Detect available streams and return mapping"""
        prefix = "stream__"
        mapping = {}
        methods = inspect.getmembers(self.__class__, predicate=inspect.isfunction)
        for name, method in methods:
            if name.startswith(prefix):
                mapping[name[len(prefix) :]] = getattr(self, name)

        return mapping

    @staticmethod
    def _get_fields_from_stream(stream: AirbyteStream) -> List[str]:
        return list(stream.json_schema.get("properties", {}).keys())

    def _get_stream_method(self, name: str) -> Callable:
        method = self._stream_methods.get(name)
        if not method:
            raise ValueError(f"Client does not know how to read stream `{name}`")
        return method

    def read_stream(self, stream: AirbyteStream) -> Generator[Dict[str, Any], None, None]:
        """Yield records from stream"""
        method = self._get_stream_method(stream.name)
        fields = self._get_fields_from_stream(stream)

        for message in method(fields=fields):
            yield dict(message)

    @property
    def streams(self) -> Generator[AirbyteStream, None, None]:
        """List of available streams"""
        for name, method in self._stream_methods.items():
            supported_sync_modes = [SyncMode.full_refresh]
            source_defined_cursor = False
            if self.stream_has_state(name):
                supported_sync_modes = [SyncMode.incremental]
                source_defined_cursor = True

            yield AirbyteStream(
                name=name,
                json_schema=self._schema_loader.get_schema(name),
                supported_sync_modes=supported_sync_modes,
                source_defined_cursor=source_defined_cursor,
            )

    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """Check if service is up and running"""


def configured_catalog_from_client(client: BaseClient) -> ConfiguredAirbyteCatalog:
    """Helper to generate configured catalog for testing"""
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStream(stream=stream) for stream in client.streams])

    return catalog
