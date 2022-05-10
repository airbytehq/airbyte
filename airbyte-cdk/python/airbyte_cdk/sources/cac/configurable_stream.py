#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

# from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator, NoAuth
# from airbyte_cdk.sources.streams.http.http import HttpStream
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory
from airbyte_cdk.sources.cac.retrievers.retriever import Retriever

if TYPE_CHECKING:
    from airbyte_cdk.sources.cac.types import Vars, Config

from airbyte_cdk.sources.streams.core import Stream


class ConfigurableStream(Stream):
    def __init__(self, name, schema, retriever, vars: "Vars", config: "Config"):
        # print(f"creating a configurable stream with {name}")
        # print(f"schema: {schema}")
        self._name = name
        self._vars = vars
        self._schema_loader = LowCodeComponentFactory().create_component(schema, vars, config)
        # print(f"stream.vars: {self._vars}")
        self._retriever: Retriever = LowCodeComponentFactory().create_component(retriever, vars, config)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        records = self._retriever.read_records(sync_mode, cursor_field, stream_slice, stream_state)

        return records

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        # FIXME: TODO
        return "id"

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        # TODO show an example of using pydantic to define the JSON schema, or reading an OpenAPI spec
        return self._schema_loader.get_json_schema()

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        # FIXME: this is not passing the cursor field because i think it should be known at init time. Is this always true?
        return self._retriever.stream_slices(sync_mode=sync_mode, stream_state=stream_state)
