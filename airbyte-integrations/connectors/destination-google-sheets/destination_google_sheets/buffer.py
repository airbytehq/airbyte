#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream


class WriteBuffer:

    # Default instance of AirbyteLogger
    logger = AirbyteLogger()
    # Buffer for input records
    records_buffer = []
    # Placeholder for streams metadata
    stream_info = []
    # interval after which the records_buffer should be cleaned up for selected stream
    flush_interval = 1000

    @property
    def default_missing(self) -> str:
        """
        Default value for missing keys in record stream, compared to configured_stream catalog.
        Overwrite if needed.
        """
        return ""

    def buffer_stream(self, configured_stream: AirbyteStream):
        """
        Saves important stream's information for later use.

        Particulary, creates the data structure for `records_stream`.
        Populates `stream_info` placeholder with stream metadata information.
        """
        stream = configured_stream.stream
        stream_schema = stream.json_schema
        stream_name = stream.name

        self.records_buffer.append({stream_name: []})
        self.stream_info.append({stream_name: sorted(list(stream_schema.get("properties").keys())), "is_set": False})

    def buffer_has_more_records(self) -> bool:
        """
        Check whether `records_buffer` has any values that are still need to be written.
        """
        for stream in self.records_buffer:
            stream_name = list(stream.keys())[0]
            if stream_name in stream:
                result = True if len(stream[stream_name]) > 0 else False
        return result

    def add_to_buffer(self, stream_name: str, record: Mapping):
        """
        Populates input records to `records_buffer`.

        1) normalizes input record
        2) coerces normalized record to str
        3) gets values as list of record values from record mapping.
        """
        for stream in self.records_buffer:
            if stream_name in stream:
                stream[stream_name].append(self.get_record_values(self.normalize_record(stream_name, record)))

    def flush_buffer(self, stream_name: str):
        """
        Cleans up the `records_buffer` values, belonging to input stream.
        """
        [stream[stream_name].clear() for stream in self.records_buffer if stream_name in stream]

    def normalize_record(self, stream_name: str, record: Mapping) -> Mapping[str, Any]:
        """
        Updates the record keys up to the input configured_stream catalog keys.

        Handles two scenarios:
        1) when record has less keys than catalog declares (undersetting)
        2) when record has more keys than catalog declares (oversetting)

        Returns: alphabetically sorted, catalog-normalized Mapping[str, Any].

        EXAMPLE:
        - UnderSetting:
            * Catalog:
                - has 3 entities:
                    [ 'id', 'key1', 'key2' ]
                              ^
            * Input record:
                - missing 1 entity, compare to catalog
                    { 'id': 123,    'key2': 'value' }
                                  ^
            * Result:
                - 'key1' has been added to the record, because it was declared in catalog, to keep the data structure.
                    {'id': 123, 'key1': '', {'key2': 'value'} }
                                  ^
        - OverSetting:
            * Catalog:
                - has 3 entities:
                    [ 'id', 'key1', 'key2',   ]
                                            ^
            * Input record:
                - doesn't have entity 'key1'
                - has 1 more enitity, compare to catalog 'key3'
                    { 'id': 123,     ,'key2': 'value', 'key3': 'value' }
                                  ^                      ^
            * Result:
                - 'key1' was added, because it expected be the part of the record, to keep the data structure
                - 'key3' was dropped, because it was not declared in catalog, to keep the data structure
                    { 'id': 123, 'key1': '', 'key2': 'value',   }
                                   ^                          ^

        """

        for stream in self.stream_info:
            if stream_name in stream:
                # undersetting scenario
                [record.update({key: self.default_missing}) for key in stream[stream_name] if key not in record.keys()]
                # oversetting scenario
                [record.pop(key) for key in record.copy().keys() if key not in stream[stream_name]]

        return dict(sorted(record.items(), key=lambda x: x[0]))

    def get_record_values(self, record: Mapping) -> List[str]:
        """
        Returns the input record values.
        """
        return self.values_to_str(list(record.values()))

    def values_to_str(self, values: List) -> List[Any]:
        """
        Force input record values to be a type of string.
        """
        return [str(values[i]) for i in range(len(values))]
