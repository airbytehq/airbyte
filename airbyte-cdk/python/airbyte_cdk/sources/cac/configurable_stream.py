#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

# from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator, NoAuth
# from airbyte_cdk.sources.streams.http.http import HttpStream
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.retrievers.retriever import Retriever

if TYPE_CHECKING:
    from airbyte_cdk.sources.cac.types import Config

from airbyte_cdk.sources.streams.core import IncrementalMixin, Stream


class ConfigurableStream(Stream, IncrementalMixin):
    @classmethod
    def create(cls, /, *args, **keywords):
        func = ConfigurableStream

        def newfunc(*fargs, **fkeywords):
            newkeywords = {**keywords, **fkeywords}
            print(newkeywords)
            return func(*args, *fargs, **newkeywords)

        newfunc.func = func
        newfunc.args = args
        newfunc.kwargs = keywords

        return newfunc

    def __init__(self, name, primary_key, cursor_field, schema, retriever, config: "Config"):
        self._name = name
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._schema_loader = schema
        self._retriever: Retriever = retriever
        self._config = config

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._retriever._state.get_state()

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        # FIXME: Do we still need this?
        self._retriever._state.update_state(None, value, None, None)

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
        return self._primary_key

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

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self._cursor_field

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """
        Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.

        Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.

        return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.
        """
        return self._retriever.state_checkpoint_interval
