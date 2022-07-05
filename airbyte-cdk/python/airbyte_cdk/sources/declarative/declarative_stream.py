#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.transformations.transformer import RecordTransformation
from airbyte_cdk.sources.streams.core import Stream


class DeclarativeStream(Stream):
    """
    DeclarativeStream is a Stream that delegates most of its logic to its schema_load and retriever
    """

    def __init__(
        self,
        name,
        primary_key,
        schema_loader: SchemaLoader,
        retriever: Retriever,
        cursor_field: Optional[List[str]] = None,
        transformations: List[RecordTransformation] = None,
    ):
        """

        :param name: stream name
        :param primary_key: the primary key of the stream
        :param schema_loader:
        :param retriever:
        :param cursor_field:
        :param transformations: A list of transformations to be applied to each output record in the stream. Transformations are applied
        in the order in which they are defined.
        """
        self._name = name
        self._primary_key = primary_key
        self._cursor_field = cursor_field or []
        self._schema_loader = schema_loader
        self._retriever = retriever
        self._transformations = transformations or []

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._retriever.state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._retriever.state = value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return self.state

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self._cursor_field

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in self._retriever.read_records(sync_mode, cursor_field, stream_slice, stream_state):
            yield self._apply_transformations(record)

    def _apply_transformations(self, record: Mapping[str, Any]):
        output_record = record
        for transformation in self._transformations:
            output_record = transformation.transform(record)

        return output_record

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
        # this is not passing the cursor field because it is known at init time
        return self._retriever.stream_slices(sync_mode=sync_mode, stream_state=stream_state)
