# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import csv
import gzip
import io
import logging
import tempfile
import zipfile
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import Any, Callable, Dict, Generator, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.http_client import HttpClient


logger = logging.getLogger(__name__)


PARENT_SLICE_KEY: str = "parent_slice"


@dataclass
class DuplicatedRecordsFilter(RecordFilter):
    """
    Filter duplicated records based on the "Id" field.
    This can happen when we use predicates that could match the same record
    multiple times.

    e.g.
    With one record like:
    {"type":"RECORD","record":{"stream":"accounts","data":{"Id":151049662,
    "Name":"Airbyte Plumbing"},"emitted_at":1748277607993}}
    account_names in config:
    [
        {
          "name": "Airbyte",
          "operator": "Contains"
        },
        {
          "name": "Plumbing",
          "operator": "Contains"
        }
    ],
    will return the same record twice, once for each predicate.
    """

    CONFIG_PREDICATES = "account_names"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._seen_keys = set()

    @cached_property
    def _using_predicates(self) -> bool:
        """
        Indicates whether the connection uses predicates.
        :return: True if the connector uses predicates, False otherwise
        """
        predicates = self.config.get(self.CONFIG_PREDICATES)
        return bool(predicates and isinstance(predicates, list) and predicates)

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            if not self._using_predicates:
                yield record
            else:
                key = record["Id"]
                if key not in self._seen_keys:
                    self._seen_keys.add(key)
                    yield record


@dataclass
class BingAdsCampaignsRecordTransformer(RecordTransformation):
    """
    Transform Campaigns records from Bing Ads API to ensure consistent data structure and types.

    This transformer handles two main transformations:

    Settings field transformations:
    1. For settings with Details, wrap the Details array in TargetSettingDetail structure:
       {"Details": {"TargetSettingDetail": original_details}}
    2. For settings without Details or with null Details, preserve the original structure
    3. Convert empty lists ([]) to null for backward compatibility
    4. Convert string values to integers for keys ending with "Id" (when valid integers)
    5. Convert PageFeedIds lists to object format: {"long": [int_values]}
    6. Wrap all transformed settings in {"Setting": transformed_settings}

    BiddingScheme field transformations:
    1. Recursively convert all integer values to floats to ensure consistent numeric type handling

    Example Settings transformation:
    Input:  {"Settings": [{"Type": "Target", "Details": [...], "PageFeedIds": ["123", "456"]}]}
    Output: {"Settings": {"Setting": [{"Type": "Target",
                                      "Details": {"TargetSettingDetail": [...]},
                                      "PageFeedIds": {"long": [123, 456]}}]}}

    Example BiddingScheme transformation:
    Input:  {"BiddingScheme": {"MaxCpc": {"Amount": 5}}}
    Output: {"BiddingScheme": {"MaxCpc": {"Amount": 5.0}}}
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform the record by converting the Settings and BiddingScheme properties.

        Args:
            record: The campaign record to transform (modified in-place)
            config: Optional configuration (unused)
            stream_state: Optional stream state (unused)
            stream_slice: Optional stream slice (unused)
        """
        settings = record.get("Settings")
        bidding_scheme = record.get("BiddingScheme")

        if settings:
            self._transform_settings_property(record, settings)

        if bidding_scheme:
            self._transform_bidding_scheme_property(bidding_scheme)

    def _transform_settings_property(self, record: MutableMapping[str, Any], settings: Any) -> None:
        """
        Transform the Settings property of a campaign record.
        Converts the Settings list into the expected nested structure and applies
        value transformations to individual setting properties.
        Args:
            record: The campaign record containing the Settings (modified in-place)
            settings: The Settings value from the record
        """
        if not isinstance(settings, list) or len(settings) == 0:
            # Keep original value (None, empty list, etc.)
            return

        transformed_settings = []

        for setting in settings:
            if not isinstance(setting, dict):
                # Keep non-dict settings as-is
                transformed_settings.append(setting)
                continue

            if "Details" in setting and setting["Details"] is not None:
                # Wrap Details in TargetSettingDetail only if Details is not None
                transformed_setting = {
                    "Type": setting.get("Type"),
                    "Details": {"TargetSettingDetail": setting["Details"]},
                }
                # Add any other properties that might exist
                for key, value in setting.items():
                    if key not in ["Type", "Details"]:
                        transformed_setting[key] = self._transform_setting_value(key, value)
                transformed_settings.append(transformed_setting)
            else:
                # Keep setting as-is (no Details to wrap or Details is None)
                # But still convert empty lists to null and string IDs to integers
                transformed_setting = {}
                for key, value in setting.items():
                    transformed_setting[key] = self._transform_setting_value(key, value)
                transformed_settings.append(transformed_setting)

        # Wrap the transformed settings in the expected structure
        record["Settings"] = {"Setting": transformed_settings}

    def _transform_setting_value(self, key: str, value: Any) -> Any:
        """
        Transform individual setting values based on key name and value type.
        Applies specific transformations:
        - Empty lists become null
        - PageFeedIds lists become {"long": [int_values]} objects
        - String values for keys ending with "Id" become integers (when valid)
        Args:
            key: The setting property name
            value: The setting property value
        Returns:
            The transformed value
        """
        # Convert empty lists to null for backward compatibility
        if isinstance(value, list) and len(value) == 0:
            return None
        elif key == "PageFeedIds":
            # Convert PageFeedIds list to object with long array
            return self._convert_page_feed_id_lists(value)
        else:
            # Convert string IDs to integers
            return self._convert_id_strings_to_integers(key, value)

    def _transform_bidding_scheme_property(self, bidding_scheme: Any) -> None:
        """
        Transform the BiddingScheme property of a campaign record.
        Recursively converts all integer values to floats for consistent numeric handling.
        """
        if bidding_scheme and isinstance(bidding_scheme, dict):
            self._convert_integers_to_floats(bidding_scheme)

    def _convert_integers_to_floats(self, obj: MutableMapping[str, Any]) -> None:
        """
        Recursively convert integer values to floats in a dictionary.
        This ensures consistent numeric type handling across all BiddingScheme values.
        Only converts values that are whole numbers (int or float with no decimal part).
        """
        if not isinstance(obj, dict):
            return

        for key, value in obj.items():
            if isinstance(value, dict):
                self._convert_integers_to_floats(value)
                continue

            # Convert any whole numbers to float type
            if isinstance(value, (int, float)) and value == int(value):
                obj[key] = float(value)

    def _convert_id_strings_to_integers(self, key: str, value: Any) -> Any:
        """
        Convert string values to integers for keys ending with "Id".
        Only converts if the string represents a valid integer. If conversion fails,
        the original string value is preserved.
        """
        if key.endswith("Id") and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                # If conversion fails, return original value
                return value
        return value

    def _convert_page_feed_id_lists(self, value: Any) -> Any:
        """
        Convert PageFeedIds from list of strings to object with long array of integers.
        This transformation is required for compatibility with the expected API format.
        If any string cannot be converted to an integer, the original value is returned.
        Example:
            Input:  ["8246337222870", "1234567890"]
            Output: {"long": [8246337222870, 1234567890]}
        """
        if isinstance(value, list) and len(value) > 0:
            try:
                # Convert string IDs to integers
                long_values = [int(id_str) for id_str in value if isinstance(id_str, str)]
                return {"long": long_values}
            except ValueError:
                # If conversion fails, return original value
                return value
        return value


@dataclass
class BulkDatetimeToRFC3339(RecordTransformation):
    """
    Bing Ads Bulk API provides datetime fields in custom format with milliseconds: "04/27/2023 18:00:14.970"
    Return datetime in RFC3339 format: "2023-04-27T18:00:14.970+00:00"
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        original_value = record["Modified Time"]
        if original_value is not None and original_value != "":
            try:
                record["Modified Time"] = (
                    datetime.strptime(original_value, "%m/%d/%Y %H:%M:%S.%f")
                    .replace(tzinfo=timezone.utc)
                    .isoformat(timespec="milliseconds")
                )
            except ValueError:
                pass  # Keep original value if parsing fails
        # Don't set to None - leave original value unchanged


@dataclass
class LightSubstreamPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        For migration to manifest connector we needed to migrate legacy state to per partition
        but regular SubstreamPartitionRouter will include the parent_slice in the partition that
        LegacyToPerPartitionStateMigration can't add in transformed state.
        Then, we remove the parent_slice.

        e.g.
        super().stream_slices() = [
            StreamSlice(partition={"parent_slice": {"user_id": 1, "parent_slice": {}}, "account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"parent_slice": {"user_id": 2, "parent_slice": {}}, "account_id": 2}, cursor_slice={}, extra_fields=None)            ]
        Router yields: [
            StreamSlice(partition={"account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"account_id": 2}, cursor_slice={}, extra_fields=None),
        ]
        """
        stream_slices = super().stream_slices()
        for stream_slice in stream_slices:
            stream_slice_partition: Dict[str, Any] = dict(stream_slice.partition)
            partition_keys = list(stream_slice_partition.keys())
            if PARENT_SLICE_KEY in partition_keys:
                partition_keys.remove(PARENT_SLICE_KEY)
                stream_slice_partition.pop(PARENT_SLICE_KEY, None)
            if len(partition_keys) != 1:
                raise ValueError(f"SubstreamDedupPartitionRouter expects a single partition key-value pair. Got {stream_slice_partition}")

            yield StreamSlice(
                partition=stream_slice_partition,
                cursor_slice=stream_slice.cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )


class BulkStreamsStateMigration(StateMigration):
    """
    Due to a bug in python implementation legacy state may look like this:
    "streamState": {
      "account_id": {
        "Modified Time": "valid modified time"
      },
      "Id": "Id",
      [record data ...]
      "Modified Time": null,
      [record data ...]
    }

    It happens when received record doesn't have a cursor field and state updating logic stores it in state.
    To avoid parsing null cursor fields that lead to value error, this state migration deletes the top level cursor field and records data
    if the cursor is null.
    """

    cursor_field = "Modified Time"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if self.cursor_field in stream_state.keys() and stream_state.get(self.cursor_field) is None:
            return True
        return False

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if self.should_migrate(stream_state):
            state_copy = deepcopy(stream_state)

            for key, value in state_copy.items():
                if not isinstance(value, dict):
                    del stream_state[key]

        return stream_state


@dataclass
class CustomReportSchemaLoader(SchemaLoader):
    """
    Creates custom report schema based on provided reporting columns.
    """

    reporting_columns: List[str]
    report_aggregation: str

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.report_aggregation == "DayOfWeek":
            self.reporting_columns = self.reporting_columns + ["DayOfWeek", "StartOfTimePeriod", "EndOfTimePeriod"]
        if self.report_aggregation == "HourOfDay":
            self.reporting_columns = self.reporting_columns + ["HourOfDay", "StartOfTimePeriod", "EndOfTimePeriod"]

        self.reporting_columns = list(frozenset(self.reporting_columns))

        columns_schema = {col: {"type": ["null", "string"]} for col in self.reporting_columns}
        schema: Mapping[str, Any] = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": columns_schema,
        }
        return schema


@dataclass
class CustomReportTransformation(RecordTransformation):
    report_aggregation: str

    def transform_report_hourly_datetime_format_to_rfc_3339(self, original_value: str) -> str:
        """
        Bing Ads API reports with hourly aggregation provides date fields in custom format: "2023-11-04|11"
        Return date in RFC3339 format: "2023-11-04T11:00:00+00:00"
        """
        return datetime.strptime(original_value, "%Y-%m-%d|%H").replace(tzinfo=timezone.utc).isoformat(timespec="seconds")

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        if self.report_aggregation == "Hourly":
            if record.get("TimePeriod"):
                record.update({"TimePeriod": self.transform_report_hourly_datetime_format_to_rfc_3339(record["TimePeriod"])})

        if self.report_aggregation == "DayOfWeek":
            cursor_field = record["TimePeriod"]
            record.update(
                {
                    "StartOfTimePeriod": stream_slice["start_time"],
                    "EndOfTimePeriod": stream_slice["end_time"],
                    "DayOfWeek": cursor_field,
                    "TimePeriod": stream_slice["end_time"],
                }
            )
            record["TimePeriod"] = record["EndOfTimePeriod"]

        if self.report_aggregation == "HourOfDay":
            cursor_field = record["TimePeriod"]
            record.update(
                {
                    "StartOfTimePeriod": stream_slice["start_time"],
                    "EndOfTimePeriod": stream_slice["end_time"],
                    "HourOfDay": cursor_field,
                    "TimePeriod": stream_slice["end_time"],
                }
            )


class _PrefixedStream(io.RawIOBase):
    """
    A minimal read-only stream that prepends initial bytes to another stream.
    Used to peek at the first bytes of a response (for gzip magic number detection)
    while still allowing the full stream to be read sequentially.
    """

    def __init__(self, prefix: bytes, stream: Any) -> None:
        self._prefix = prefix
        self._prefix_offset = 0
        self._stream = stream

    def readable(self) -> bool:
        return True

    def readinto(self, b: bytearray) -> int:
        data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def read(self, size: int = -1) -> bytes:
        prefix_remaining = len(self._prefix) - self._prefix_offset
        if prefix_remaining > 0:
            if size < 0:
                chunk = self._prefix[self._prefix_offset :]
                self._prefix_offset = len(self._prefix)
                return chunk + (self._stream.read() or b"")
            take = min(size, prefix_remaining)
            chunk = self._prefix[self._prefix_offset : self._prefix_offset + take]
            self._prefix_offset += take
            if take < size:
                more = self._stream.read(size - take)
                return chunk + (more or b"")
            return chunk
        return self._stream.read(size) or b""


@dataclass
class BingAdsReportZipCsvDecoder(Decoder):
    """
    Streaming decoder for Bing Ads report ZIP downloads.

    The CDK's built-in ZipfileDecoder loads the entire HTTP response into memory
    via `response.content`, creating multiple in-memory copies of the data.
    With high concurrency, this causes OOM when processing large reports.

    This decoder streams the response to a temporary SpooledTemporaryFile
    (spilling to disk beyond 5 MB), then extracts and parses the CSV content
    row-by-row, keeping memory usage bounded regardless of report size.
    """

    encoding: str = "utf-8-sig"
    set_values_to_none: Optional[List[str]] = None

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: Any) -> Generator[MutableMapping[str, Any], None, None]:
        spool = tempfile.SpooledTemporaryFile(max_size=5 * 1024 * 1024)
        raw = response.raw
        try:
            while True:
                chunk = raw.read(64 * 1024)
                if not chunk:
                    break
                spool.write(chunk)
            spool.seek(0)

            try:
                with zipfile.ZipFile(spool) as zf:
                    for name in zf.namelist():
                        with zf.open(name) as member:
                            text_stream = io.TextIOWrapper(member, encoding=self.encoding)
                            reader = csv.DictReader(text_stream)
                            none_values = set(self.set_values_to_none) if self.set_values_to_none else set()
                            for row in reader:
                                row.pop(None, None)  # Remove extra columns not in header
                                if none_values:
                                    for key, value in row.items():
                                        if value in none_values:
                                            row[key] = None
                                yield row
            except zipfile.BadZipFile as exc:
                logger.error("Received an invalid zip file in response: %s", exc)
                raise
        finally:
            spool.close()
            raw.close()


@dataclass
class BingAdsGzipCsvDecoder(Decoder):
    """
    Custom decoder that detects GZip compression via magic bytes and parses CSV data
    using streaming decompression. This prevents OOM on large bulk downloads by avoiding
    loading the entire file into memory.

    Bing Ads sends GZip compressed files from Azure Blob Storage without proper
    compression headers, so standard header-based detection does not work. Instead,
    this decoder checks the first two bytes for the gzip magic number (0x1f 0x8b)
    and routes to either streaming gzip decompression or plain-text CSV parsing.
    """

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: Any) -> Generator[MutableMapping[str, Any], None, None]:
        raw = response.raw
        raw.auto_close = False
        try:
            yield from self._decode_stream(raw)
        except Exception as e:
            logger.error(f"Failed to parse response as either GZip or plain CSV: {e}")
            yield {}
        finally:
            raw.close()

    def _decode_stream(self, raw: Any) -> Generator[MutableMapping[str, Any], None, None]:
        header = raw.read(2)
        if not header:
            return

        is_gzip = header[:2] == b"\x1f\x8b"
        byte_stream = _PrefixedStream(header, raw)

        if is_gzip:
            decompressed = gzip.GzipFile(fileobj=byte_stream, mode="rb")
            text_stream = io.TextIOWrapper(decompressed, encoding="utf-8-sig")
        else:
            text_stream = io.TextIOWrapper(io.BufferedReader(byte_stream), encoding="utf-8-sig")

        csv_reader = csv.DictReader(text_stream)
        for row in csv_reader:
            yield row


BING_ADS_REPORTING_POLL_URL = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"


@dataclass
class BingAdsReportDownloadRequester(HttpRequester):
    """Custom download requester that re-polls Bing Ads for a fresh SAS URL before downloading.

    When many streams are synced concurrently, the SAS download URL obtained at
    poll-completion time may expire (10-minute TTL) before the download begins.
    This requester makes a lightweight re-poll request to obtain a fresh URL
    immediately before each download, preventing ``AuthenticationFailed`` errors
    from Azure Blob Storage.
    """

    report_poll_authenticator: Optional[DeclarativeAuthenticator] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        # When instantiated via create_custom_component, stream_response is not
        # explicitly passed (unlike create_http_requester which computes it from
        # the decoder).  Derive it here so streaming decoders that read
        # response.raw (e.g. BingAdsReportZipCsvDecoder) work correctly.
        if self.decoder and hasattr(self.decoder, "is_stream_response"):
            self.stream_response = self.decoder.is_stream_response()
        super().__post_init__(parameters)

    def send_request(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        if stream_slice:
            fresh_url = self._get_fresh_download_url(stream_slice)
            if fresh_url:
                stream_slice = StreamSlice(
                    partition=stream_slice.partition,
                    cursor_slice=stream_slice.cursor_slice,
                    extra_fields={
                        **stream_slice.extra_fields,
                        "download_target": fresh_url,
                    },
                )

        return super().send_request(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            path=path,
            request_headers=request_headers,
            request_params=request_params,
            request_body_data=request_body_data,
            request_body_json=request_body_json,
            log_formatter=log_formatter,
        )

    def _get_fresh_download_url(self, stream_slice: StreamSlice) -> Optional[str]:
        """Re-poll Bing Ads Reporting API to obtain a fresh SAS download URL."""
        creation_response = stream_slice.extra_fields.get("creation_response", {})
        report_request_id = creation_response.get("ReportRequestId")
        if not report_request_id:
            logger.warning("No ReportRequestId in creation_response; using existing download URL")
            return None

        account_id = stream_slice.partition.get("account_id", "")
        parent_customer_id = stream_slice.extra_fields.get("ParentCustomerId", "")
        developer_token = self.config.get("developer_token", "")

        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "DeveloperToken": str(developer_token),
            "CustomerId": str(parent_customer_id),
            "CustomerAccountId": str(account_id),
        }

        try:
            if self.report_poll_authenticator:
                auth_header = self.report_poll_authenticator.get_auth_header()
                headers.update(auth_header)

            http_client = HttpClient(
                name="bing_ads_report_repoll",
                logger=logger,
            )
            _, response = http_client.send_request(
                http_method="POST",
                url=BING_ADS_REPORTING_POLL_URL,
                headers=headers,
                json={"ReportRequestId": str(report_request_id)},
                request_kwargs={"timeout": 30},
            )
            data = response.json()
            fresh_url = data.get("ReportRequestStatus", {}).get("ReportDownloadUrl")
            if fresh_url:
                logger.info("Obtained fresh download URL via re-poll for report request %s", report_request_id)
                return fresh_url
            logger.warning("Re-poll did not return a ReportDownloadUrl for report request %s", report_request_id)
            return None
        except Exception:
            logger.warning(
                "Re-poll failed for report request %s; falling back to existing download URL",
                report_request_id,
                exc_info=True,
            )
            return None
