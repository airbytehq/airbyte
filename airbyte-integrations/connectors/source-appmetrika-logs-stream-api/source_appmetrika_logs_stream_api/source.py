#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import csv
from io import StringIO
import json
from abc import ABC
from datetime import datetime, timedelta
import logging
import os
import pprint
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from source_appmetrika_logs_stream_api.auth import CredentialsCraftAuthenticator
from source_appmetrika_logs_stream_api.models import LogsStreamDataType, LogsStreamSchema, LogsStreamsStatus, LogsStreamWindow
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from urllib3.exceptions import ProtocolError
from source_appmetrika_logs_stream_api.thread import StreamWorkerThreadController
from source_appmetrika_logs_stream_api.utils import convert_size
from source_appmetrika_logs_stream_api.exceptions import UserDefinedSliceSkipException
import pandas as pd
from source_appmetrika_logs_stream_api.utils import filename_from_slice_window

# Basic full refresh stream
class AppmetrikaLogsStreamApiStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)
    url_base = "https://api.appmetrica.yandex.ru/logstream/v1/"
    primary_key = None

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        application_id: int,
        data_type: LogsStreamDataType,
        logs_stream_windows: list[LogsStreamWindow],
        logs_stream_schema: LogsStreamSchema,
        product_name_const: str,
        client_name_const: str,
        custom_constants: Mapping[str, Any],
        multithreading_threads_count: int = 10,
    ):
        super().__init__(authenticator=authenticator)
        self.application_id = application_id
        self.data_type = data_type
        self.logs_stream_windows = logs_stream_windows
        self.logs_stream_schema = logs_stream_schema
        self.product_name_const = product_name_const
        self.client_name_const = client_name_const
        self.custom_constants = custom_constants
        self.windows_to_load: list[LogsStreamWindow] = []
        self.multithreading_threads_count = multithreading_threads_count

    @property
    def max_retries(self) -> Union[int, None]:
        return 7

    def should_skip_slice(self, response: requests.Response) -> bool:
        return response.status_code == 404

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        response: requests.Response = self._session.send(request, **request_kwargs)

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self.should_retry(response):
            custom_backoff_time = self.backoff_time(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(backoff=custom_backoff_time, request=request, response=response)
            else:
                raise DefaultBackoffException(request=request, response=response)
        elif self.should_skip_slice(response):
            raise UserDefinedSliceSkipException(response.status_code)
        elif self.raise_on_http_errors:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                self.logger.error(response.text)
                raise exc
        return response

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}

        next_page_token = None
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        max_retries = 5
        unstable_exceptions = (requests.exceptions.ChunkedEncodingError, ProtocolError)
        window = stream_slice["window"]
        filename = filename_from_slice_window(window)
        for retry_n in range(1, max_retries + 1):
            self.logger.info(f'Start downloading file {filename} for window {datetime.fromtimestamp(window["stream_window_timestamp"])}')
            response = self._send_request(request, request_kwargs)
            try:
                self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)
                break
            except unstable_exceptions as e:
                if retry_n < max_retries:
                    self.logger.info(f"Caught unstable connection exception {e}. Retry [{retry_n}/{max_retries}]")
                    continue
                else:
                    raise e

    @property
    def name(self):
        return self.data_type.value

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, *args, **kwargs) -> str:
        return f"application/{self.application_id}/data"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        window: LogsStreamWindow = stream_slice["window"]
        params = {"data_type": self.data_type.value, "stream_window_timestamp": window["stream_window_timestamp"]}
        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping]:
        window = stream_slice["window"]
        filename = filename_from_slice_window(window)

        try:
            os.mkdir("output")
        except FileExistsError:
            pass

        # with open(filename, "wb") as f:
        #     for chunk in response.iter_content(chunk_size=8192):
        #         f.write(chunk)
        with open(filename, "wb") as f:
            f.write(response.content)
        datetime.now() - timedelta()
        self.logger.info(f'End downloading file {filename} for window {datetime.fromtimestamp(window["stream_window_timestamp"])}')

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("appmetrika_logs_stream_api_stream")
        for field_name in self.logs_stream_schema.field_names:
            schema["properties"][field_name] = {"type": ["null", "string"]}
        return schema

    def add_constants_to_record(self, record: Dict[str, Any]) -> Mapping[str, Any]:
        constants = {
            "__productName": self.product_name_const,
            "__clientName": self.client_name_const,
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def request_kwargs(self, *args, **kwargs) -> Mapping[str, Any]:
        rkwargs: Dict = super().request_kwargs(*args, **kwargs)
        rkwargs.update({"stream": True})
        return rkwargs

    @staticmethod
    def pick_windows_by_datetime_range(
        logs_stream_windows: List[LogsStreamWindow], datetime_from: datetime, datetime_to: datetime
    ) -> List[LogsStreamWindow]:
        picked_windows = []
        for window in logs_stream_windows:
            window_datetime = datetime.fromtimestamp(window.stream_window_timestamp)
            if datetime_from <= window_datetime and datetime_to > window_datetime:
                picked_windows.append(window)
        return picked_windows

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for window in self.windows_to_load:
            yield {"window": window.dict()}


# Source
class SourceAppmetrikaLogsStreamApi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception("Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def get_streams_status(self, config: Mapping[str, Any]) -> LogsStreamsStatus:
        auth = self.get_auth(config)
        status_data_resp = requests.get(
            AppmetrikaLogsStreamApiStream.url_base + f'application/{config["application_id"]}/status', headers=auth.get_auth_header()
        )
        status_data = status_data_resp.json()["status"]
        return LogsStreamsStatus.parse_obj(status_data)

    def transform_config_date_range(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        datetime_range: Mapping[str, Any] = config.get("datetime_range", {})
        datetime_range_type: str = datetime_range.get("datetime_range_type")
        datetime_from: datetime = None
        datetime_to: datetime = None
        today_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_datetime_format = "%Y-%m-%dT%H:%M:%S"

        if datetime_range_type == "custom_datetime":
            datetime_from = datetime.strptime(datetime_range.get("datetime_from"), from_user_datetime_format)
            datetime_to = datetime.strptime(datetime_range.get("datetime_to"), from_user_datetime_format)
        elif datetime_range_type == "last_n_days":
            if datetime_range.get("should_load_today"):
                datetime_from = today_datetime - timedelta(days=datetime_range.get("last_days_count"))
                datetime_to = today_datetime
            else:
                datetime_from = today_datetime - timedelta(days=datetime_range.get("last_days_count") + 1)
                datetime_to = today_datetime - timedelta(days=1)

        config["datetime_from_transformed"], config["datetime_to_transformed"] = datetime_from, datetime_to
        return config

    def _read_stream(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        self._apply_log_level_to_stream_logger(logger, stream_instance)
        use_incremental = configured_stream.sync_mode == SyncMode.incremental and stream_instance.supports_incremental
        if use_incremental:
            raise Exception("Incremental is not supported in this connector.")
        stream_name = configured_stream.stream.name
        logger.info(f"Syncing stream: {stream_name}.")
        self._read_full_refresh(logger, stream_instance, configured_stream, internal_config)
        return []

    def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: AppmetrikaLogsStreamApiStream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        all_windows = stream_instance.logs_stream_windows
        logger.info(f"All windows for stream {stream_instance.name}: {all_windows}")
        logger.info(f"Sum of all windows sizes: {convert_size(sum([window.payload_bytes for window in all_windows]))}")
        try:
            logger.info(
                f"Sum of all windows records: {sum([window.__getattribute__(f'{stream_instance.name}_count') for window in all_windows])}"
            )
        except:
            pass
        logger.debug(f"Processing stream slices for {configured_stream.stream.name}", extra={"stream_slices": all_windows})
        thread_controller = StreamWorkerThreadController(
            source_instance=self,
            all_windows=all_windows,
            every_thread_kwargs=self.every_stream_kwargs,
            main_stream_instance=stream_instance,
            multithreading_threads_count=stream_instance.multithreading_threads_count,
        )
        thread_controller.start_threads()
        thread_controller.wait_until_threads_completed()
        logger.info(f"Read {thread_controller.current_records_count} records from {stream_instance.name} stream")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.transform_config_date_range(config)
        streams_status = self.get_streams_status(config)

        streams = []
        for logs_stream in streams_status.streams:
            windows_by_datetime_range = AppmetrikaLogsStreamApiStream.pick_windows_by_datetime_range(
                logs_stream_windows=logs_stream.stream_windows,
                datetime_from=config["datetime_from_transformed"],
                datetime_to=config["datetime_to_transformed"],
            )
            logs_stream_schema = {schema.export_schema_id: schema for schema in streams_status.export_fields}[
                logs_stream.stream_windows[0].export_schema_id
            ]
            self.every_stream_kwargs = dict(
                authenticator=auth,
                application_id=config["application_id"],
                logs_stream_windows=windows_by_datetime_range,
                logs_stream_schema=logs_stream_schema,
                product_name_const=config.get("product_name_const"),
                client_name_const=config.get("client_name_const"),
                custom_constants=json.loads(config.get("custom_constants_json", "{}")),
                multithreading_threads_count=config.get("multithreading_threads_count", 10),
            )
            this_stream_kwargs = dict(data_type=logs_stream.data_type)
            airbyte_stream = AppmetrikaLogsStreamApiStream(**self.every_stream_kwargs, **this_stream_kwargs)
            streams.append(airbyte_stream)
        return streams
