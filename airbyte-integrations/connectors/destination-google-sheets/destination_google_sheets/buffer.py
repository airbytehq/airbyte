#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream


class WriteBufferMixin:
    # Default instance of AirbyteLogger
    logger = AirbyteLogger()
    # intervals after which the records_buffer should be cleaned up for selected stream
    flush_interval = 500  # records count
    flush_interval_size_in_kb = 10 ^ 8  # memory allocation ~ 97656 Kb or 95 Mb

    def __init__(self):
        # Buffer for input records
        self.records_buffer = {}
        # Placeholder for streams metadata
        self.stream_info = {}

    @property
    def default_missing(self) -> str:
        """
        Default value for missing keys in record stream, compared to configured_stream catalog.
        Overwrite if needed.
        """
        return ""

    def init_buffer_stream(self, configured_stream: AirbyteStream):
        """
        Saves important stream's information for later use.

        Particulary, creates the data structure for `records_stream`.
        Populates `stream_info` placeholder with stream metadata information.
        """
        stream = configured_stream.stream
        self.records_buffer[stream.name] = []
        self.stream_info[stream.name] = {
            "headers": sorted(list(stream.json_schema.get("properties").keys())),
            "is_set": False,
        }

    def add_to_buffer(self, stream_name: str, record: Mapping):
        """
        Populates input records to `records_buffer`.

        1) normalizes input record
        2) coerces normalized record to str
        3) gets values as list of record values from record mapping.
        """

        norm_record = self._normalize_record(stream_name, record)
        norm_values = list(map(str, norm_record.values()))
        self.records_buffer[stream_name].append(norm_values)

    def clear_buffer(self, stream_name: str):
        """
        Cleans up the `records_buffer` values, belonging to input stream.
        """
        self.records_buffer[stream_name].clear()

    def _normalize_record(self, stream_name: str, record: Mapping) -> Mapping[str, Any]:
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
        headers = self.stream_info[stream_name]["headers"]
        # undersetting scenario
        [record.update({key: self.default_missing}) for key in headers if key not in record.keys()]
        # oversetting scenario
        [record.pop(key) for key in record.copy().keys() if key not in headers]

        return dict(sorted(record.items(), key=lambda x: x[0]))
