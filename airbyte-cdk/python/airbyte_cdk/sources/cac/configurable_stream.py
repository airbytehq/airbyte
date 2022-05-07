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
    def __init__(self, schema, retriever: Retriever, vars: "Vars", config: "Config"):
        print(f"creating a configurable stream with {retriever}")
        self._vars = vars
        print(f"stream.vars: {self._vars}")
        self._retriever = LowCodeComponentFactory().create_component(retriever, vars, config)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return self._retriever.read_records(sync_mode, cursor_field, stream_slice, stream_state)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        pass

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}
