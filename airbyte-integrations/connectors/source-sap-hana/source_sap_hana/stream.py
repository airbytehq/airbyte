import datetime
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import (
    AirbyteStream,
    SyncMode,
    AirbyteMessage
)

from airbyte_cdk.sources.streams import IncrementalMixin, Stream

from hdbcli import dbapi
from hdbcli.dbapi import Connection as SAPHanaConnection, Cursor as SAPHanaCursor

StreamData = Union[Mapping[str, Any], AirbyteMessage]

JsonSchema = Mapping[str, Any]

class SAPHanaStream(Stream, IncrementalMixin):
    _cursor_field = None

    def __init__(self, stream_name: str, json_schema: dict, records_per_slice: int, config: dict, **kwargs):
        super().__init__(**kwargs)
        # self.namespace = namespace
        self.stream_name = stream_name
        self.json_schema = json_schema
        self.records_per_slice = records_per_slice
        self.config = config

    def get_json_schema(self) -> dict:
        return self.json_schema
    
    def get_connection(self) -> SAPHanaConnection:
        return dbapi.connect(address=self.config["host"], port=self.config["port"], user=self.config["username"], password=self.config["password"])
    
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        if not self._primary_key: 
            return None
        if len(self._primary_key) == 1:
            return self._primary_key[0]
        if len(self._primary_key) > 1:
            return self._primary_key
    
    @primary_key.setter
    def primary_key(self, value):
        self._primary_key = value

    # @property
    # def namespace(self) -> str:
    #     return self._namespace
    
    # @namespace.setter
    # def namespace(self, value):
    #     self._namespace = value

    @property
    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        return True

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self._cursor_field
    
    @cursor_field.setter
    def cursor_field(self, value):
        self._cursor_field = value

    @property
    def source_defined_cursor(self) -> bool:
        """
        Return False if the cursor can be configured by the user.
        """
        return False

    @property
    def name(self) -> str:
        """
        :return: Stream name. Overwriten method from Stream(ABC)
        """
        return str.lower(self.stream_name.split(".")[1])

    # @property
    # def state_checkpoint_interval(self) -> Optional[int]:
    #     return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

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

        if sync_mode == SyncMode.full_refresh:
            return ['1=1']
        
        normalized_cursor = cursor_field[0]
        _, table_name = self.stream_name.split(".")
        return [f'CAST("{table_name}"."{normalized_cursor}" AS VARCHAR) > CAST({stream_state.get(normalized_cursor)} AS VARCHAR)'] 
    
    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(
            name=self.name, 
            json_schema=dict(self.get_json_schema()), 
            supported_sync_modes=[SyncMode.full_refresh],
            config=self.config,
            records_per_slice = self.records_per_slice
        )

        if self.namespace:
            stream.namespace = self.namespace

        if self.supports_incremental:
            stream.source_defined_cursor = self.source_defined_cursor
            stream.supported_sync_modes.append(SyncMode.incremental)  # type: ignore
            stream.default_cursor_field = self._wrapped_cursor_field()

        keys = Stream._wrapped_primary_key(self.primary_key)
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = keys

        return stream

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        
        if cursor_field and isinstance(cursor_field, list):
            normalized_cursor = cursor_field[0]

        has_state = stream_state or False
        schema_name, table_name = self.stream_name.split(".")
        if sync_mode == SyncMode.full_refresh or not has_state:
            query = f'SELECT * FROM "{schema_name}"."{table_name}" '
        elif sync_mode == SyncMode.incremental:
            query = f'SELECT * FROM "{schema_name}"."{table_name}" WHERE {stream_slice}'

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]

        for row in cursor:
            yield dict(zip(columns, row))

        cursor.close()
        conn.close() 
        
        if sync_mode == SyncMode.incremental:
            cursor_index = columns.index(normalized_cursor)
            self.state = {normalized_cursor : row[cursor_index]}