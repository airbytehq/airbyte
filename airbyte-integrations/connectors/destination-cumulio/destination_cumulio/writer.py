#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from logging import Logger
from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from destination_cumulio.client import CumulioClient


def _convert_airbyte_configured_stream_into_headers_dict(
    configured_stream: ConfiguredAirbyteStream,
):
    """Return a dict of column names and types based on the configured Airbyte stream.
    Note that the Airbyte types are currently not used due to Cumul.io's Data API Service not supporting specifying column types.
    """
    column_headers = {}
    for column_header in configured_stream.stream.json_schema["properties"]:
        if "airbyte-type" in configured_stream.stream.json_schema["properties"][column_header]:
            column_headers[column_header] = {
                "airbyte-type": configured_stream.stream.json_schema["properties"][column_header]["airbyte-type"]
            }
        else:
            column_headers[column_header] = {"airbyte-type": configured_stream.stream.json_schema["properties"][column_header]["type"]}
    return column_headers


class CumulioWriter:
    # Cumul.io's Data API service has a limit of pushing 10 000 data points (i.e. rows) in a single request.
    # (see note here: https://developer.cumul.io/?shell#data_create)
    FLUSH_INTERVAL = 10000

    def __init__(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        logger: Logger,
    ):
        """Create a single Cumul.io Client and a dict of writers.
        The Cumul.io Client will be used to send API requests to Cumul.io's API.
        The writers dict will contain one element for each configured_stream in the connection.
        Each of these dicts have a stream-specific configuration and write buffer.
        """
        self.logger = logger
        self.client = CumulioClient(config, logger)
        self.writers = self._create_writers(configured_catalog)

    def queue_write_operation(self, stream_name: str, data: Mapping):
        """Queue data in a specific writer buffer.
        It flushes the buffer in case it has reached the flush interval.
        """
        cumulio_data = self.transform_data(stream_name, data)
        self.writers[stream_name]["write_buffer"].append(cumulio_data)
        if len(self.writers[stream_name]["write_buffer"]) == self.FLUSH_INTERVAL:
            self.flush(stream_name)

    def flush_all(self):
        """Flush all writer buffers."""
        for stream_name in self.writers:
            self.flush(stream_name)

    def flush(self, stream_name: str):
        """Write a batch of data from the write buffer using the Cumul.io client."""
        self.client.batch_write(
            stream_name,
            self.writers[stream_name]["write_buffer"],
            [column_header["name"] for column_header in self.writers[stream_name]["column_headers"]],
            self.writers[stream_name]["is_in_overwrite_sync_mode"],
            self.writers[stream_name]["is_first_batch"],
            self.writers[stream_name]["update_metadata"],
        )
        self.writers[stream_name]["write_buffer"].clear()
        if self.writers[stream_name]["is_first_batch"]:
            self.writers[stream_name]["is_first_batch"] = False

    def transform_data(self, stream_name: str, airbyte_data: Mapping) -> list[Any]:
        """Transform Airbyte data (one row) into Cumul.io's expected data format (a list in the appropriate order).
        If data for a specific column is not included in the Airbyte data, the value will be None.
        If data for a specific column in the Airbyte data is not recognized, it will be ignored as extraneous.
        (see here: https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#output-4)
        """
        try:
            self.writers[stream_name]
        except KeyError:
            raise Exception(f"The stream {stream_name} is not defined in the configured_catalog and won't thus be streamed.")

        data: list[Any] = [None for i in range(len(self.writers[stream_name]["column_headers"]))]
        for column in airbyte_data:
            unknown_data = True
            index: int = 0
            for column_header in self.writers[stream_name]["column_headers"]:
                if column_header["name"] == column:
                    unknown_data = False
                    # Cumul.io doesn't support storing or querying nested (list, dict) or boolean data.
                    # we'll stringify this data via json.dumps
                    if (
                        isinstance(airbyte_data[column], list)
                        or isinstance(airbyte_data[column], dict)
                        or isinstance(airbyte_data[column], bool)
                    ):
                        data[index] = json.dumps(airbyte_data[column])
                    else:
                        data[index] = airbyte_data[column]
                index += 1
            if unknown_data:
                self.logger.debug(
                    f"The value with name {column} has not been defined in the ConfiguredAirbyteStream and will thus be "
                    f"ignored as extraneous."
                )
        return data

    def delete_stream_entries(self, stream_name: str):
        """Set a "replace" tag on a dataset to ensure all existing data will be replaced upon next synchronization."""
        return self.client.set_replace_tag_on_dataset(stream_name)

    def _create_writers(self, configured_catalog: ConfiguredAirbyteCatalog):
        """Return a set of writers, one for each stream in the configured_catalog.
        This method will also merge the Cumul.io columns for the stream's dataset, if existing."""
        writers = {}
        for configured_stream in configured_catalog.streams:
            result = self._merge_cumulio_and_airbyte_column_headers(configured_stream)
            writers[configured_stream.stream.name] = {
                "write_buffer": [],
                "column_headers": result["sorted_column_headers"],
                "is_in_overwrite_sync_mode": configured_stream.destination_sync_mode == DestinationSyncMode.overwrite,
                "is_first_batch": True,
                "update_metadata": result["update_metadata"],
            }
        return writers

    def _merge_cumulio_and_airbyte_column_headers(self, configured_stream: ConfiguredAirbyteStream):
        """Merge columns known by Airbyte and Cumul.io.
        - If the dataset does not yet exist in Cumul.io (i.e. the first sync), the columns order will be based on "for el in dict" order.
        - Upon next synchronizations, the dataset exists in Cumul.io. Its column order will be used to send data in the corresponding order.
        - If a new column is added to the source table (i.e. this column doesn't exist yet in Cumul.io),
          it will be added at the end of the dataset's columns upon next synchronization.
        - If an existing column is removed from the source:
          1. If the next synchronization for this stream runs in "overwrite" mode (or a "replace" tag is set), the Cumul.io dataset will
             no longer contain the original column.
          2. If the next synchronization for this stream runs in "append" mode, the Cumul.io dataset will
             contain empty values for the non-existing columns for all appended rows.
          Note that Airbyte recommends a reset upon changes to source schema(s). In that case, the first batch will be synced
          using the "overwrite" mode (due to setting a reset tag on the dataset, see delete_stream_entries implementation).
        """
        cumulio_column_headers = self.client.get_ordered_columns(configured_stream.stream.name)
        airbyte_column_headers = _convert_airbyte_configured_stream_into_headers_dict(configured_stream)

        update_metadata = False

        merged_column_headers = []
        new_column_count = 0
        for airbyte_column_header in airbyte_column_headers:
            merged_column_header = {
                "name": airbyte_column_header,
                "airbyte-type": airbyte_column_headers[airbyte_column_header]["airbyte-type"],
            }

            try:
                # Add an order based on the order of the column in the Cumul.io dataset
                merged_column_header["order"] = cumulio_column_headers.index(airbyte_column_header)
            except ValueError:
                # Add an appropriate order to ensure the column appears at the end of the data
                new_column_count += 1
                merged_column_header["order"] = len(cumulio_column_headers) + new_column_count

            merged_column_headers.append(merged_column_header)

        sorted_column_headers = sorted(merged_column_headers, key=lambda x: x["order"])
        if new_column_count > 0:
            update_metadata = True

            if len(cumulio_column_headers) > 0:
                self.logger.info(
                    f"One or more columns defined in stream {configured_stream.stream.name} are not yet present in Cumul.io, "
                    f"and will added upon next successful synchronization."
                )
            else:
                self.logger.info(
                    f"The dataset for stream {configured_stream.stream.name} doesn't seem to exist in Cumul.io. "
                    f"The next sync for this stream will create it."
                )
        elif not update_metadata:
            # Validate whether all columns in Cumul.io are still part of the configured airbyte catalog definition.
            for cumulio_column_header in cumulio_column_headers:
                try:
                    # Try to find the Cumul.io column header in the Airbyte columns
                    airbyte_column_headers[cumulio_column_header]
                except KeyError:
                    # Cumul.io's column hasn't been found, so we'll need to update the dataset's metadata upon next sync.
                    if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                        self.logger.info(
                            f"The source column {cumulio_column_header} in Cumul.io is no longer present in the configured "
                            f"stream {configured_stream.stream.name} (i.e. in the source). As the stream synchronization is "
                            f"in overwrite mode, the existing column in Cumul.io will be deleted upon next sync. Check "
                            f"carefully whether this column is used in any existing Cumul.io dashboards!"
                        )
                        update_metadata = True

        return {
            "sorted_column_headers": sorted_column_headers,
            "update_metadata": update_metadata,
        }
