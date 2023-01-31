#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import csv
from datetime import datetime
import io
import logging
from typing import Any, Iterable, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    Type,
)
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from destination_yandex_metrica_offline_conv.auth import CredentialsCraftAuthenticator

logger = logging.getLogger('airbyte')


class StreamRecordsCsvBuffer:
    def __init__(self, csv_buffer: io.StringIO, configured_stream: ConfiguredAirbyteStream, dict_writer: csv.DictWriter, id_type: str):
        self.csv_buffer = csv_buffer
        self.configured_stream = configured_stream
        self.dict_writer = dict_writer
        self.id_type = id_type
        self.current_records_count = 0


class YandexMetricaOfflineConvWriter:
    def __init__(
        self,
        auth: TokenAuthenticator,
        counter_id: int,
        configured_streams: List[ConfiguredAirbyteStream],
        flush_interval: int = 15_000
    ):
        self.auth = auth
        self.counter_id = counter_id
        self.flush_interval = flush_interval

        self.stream_buffers: Mapping[str, StreamRecordsCsvBuffer] = {}
        for configured_stream in configured_streams:
            csv_buffer = io.StringIO()
            dict_writer = csv.DictWriter(
                csv_buffer,
                fieldnames=configured_stream.stream.json_schema['properties'].keys(
                )
            )
            self.stream_buffers[configured_stream.stream.name] = stream_buffer = StreamRecordsCsvBuffer(
                csv_buffer=csv_buffer,
                configured_stream=configured_stream,
                dict_writer=dict_writer,
                id_type=self.lookup_id_type_from_configured_stream(
                    configured_stream
                )
            )
            stream_buffer.dict_writer.writeheader()

    def lookup_id_type_from_configured_stream(self, configured_stream: ConfiguredAirbyteStream) -> str:
        field_names: List[str] = configured_stream.stream.json_schema[
            'properties'].keys()
        id_field = list(
            filter(lambda field_name: field_name.lower().endswith('id'), field_names))[0]
        return {'UserId': 'USER_ID', 'ClientId': 'CLIENT_ID', 'Yclid': 'YCLID'}[id_field]

    def upload_stream_buffer(self, stream_buffer: StreamRecordsCsvBuffer) -> requests.Response:
        url = f"https://api-metrika.yandex.net/management/v1/counter/" \
            f"{self.counter_id}/offline_conversions/upload?client_id_type={stream_buffer.id_type}"
        with open(f'secrets/output/{datetime.now()}.csv', 'w') as f:
            f.write(stream_buffer.csv_buffer.getvalue())
        resp = requests.post(url, headers=self.auth.get_auth_header(), files={
            "file": stream_buffer.csv_buffer.getvalue()})
        if resp.status_code != 200:
            raise Exception(f'API Error {resp.status_code}: {resp.text}')
        logger.info(f'API response on write: {resp.text}')

    def clean_stream_csv_buffer(self, stream_buffer: StreamRecordsCsvBuffer) -> None:
        stream_buffer.csv_buffer.truncate(0)
        stream_buffer.csv_buffer.seek(0)

    def flush_stream_buffer(self, stream_buffer: StreamRecordsCsvBuffer) -> None:
        logger.info(
            f'Write {stream_buffer.current_records_count} records from stream {stream_buffer.configured_stream.stream.name}')
        self.upload_stream_buffer(stream_buffer)
        self.clean_stream_csv_buffer(stream_buffer)
        stream_buffer.dict_writer.writeheader()
        stream_buffer.current_records_count = 0
        return stream_buffer

    def lookup_stream_buffer_by_record(self, record: AirbyteRecordMessage) -> StreamRecordsCsvBuffer:
        return self.stream_buffers[record.stream]

    def write_record_to_buffer(self, record: AirbyteRecordMessage) -> None:
        stream_buffer = self.lookup_stream_buffer_by_record(record)
        stream_buffer.dict_writer.writerow(record.data)
        stream_buffer.current_records_count += 1
        if stream_buffer.current_records_count == self.flush_interval:
            self.flush_stream_buffer(stream_buffer)

    def flush_all_buffers(self) -> None:
        for buffer in self.stream_buffers.values():
            self.flush_stream_buffer(buffer)

    def write(self, record: AirbyteRecordMessage) -> None:
        self.write_record_to_buffer(record)

    @property
    def is_buffers_empty(self) -> bool:
        return not sum([buffer.current_records_count for buffer in self.stream_buffers.values()]) > 0


class DestinationYandexMetricaOfflineConv(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        check_configured_catalog_status, check_configured_catalog_message = self.check_configured_catalog(
            configured_catalog)
        if not check_configured_catalog_status:
            raise Exception(check_configured_catalog_message)

        auth = self.get_auth(config)
        writer = YandexMetricaOfflineConvWriter(
            auth=auth, counter_id=config['counter_id'], configured_streams=configured_catalog.streams)
        current_record_n = 0

        for message in input_messages:
            if message.type == Type.RECORD:
                current_record_n += 1
                writer.write(message.record)
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came
                # before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state
                # message to indicate it's safe to checkpoint state
                logger.info('Flush buffers on state.')
                writer.flush_all_buffers()
                yield message

        if not writer.is_buffers_empty:
            logger.info('Buffers are not empty at the end. Flushing it.')
            writer.flush_all_buffers()

    def check_configured_catalog(self, configured_catalog: ConfiguredAirbyteCatalog) -> Tuple[bool, str]:
        supported_fields = ['UserId', 'ClientId',
                            'Yclid', 'Target', 'DateTime', 'Price', 'Currency']
        required_non_id_fields = ['Target', 'DateTime']
        for configured_stream in configured_catalog.streams:
            stream_schema = configured_stream.stream.json_schema['properties']
            schema_fields = stream_schema.keys()
            id_fields_count = 0
            unsupported_fields_in_schema = []

            for field in schema_fields:
                if field.lower().endswith('id'):
                    id_fields_count += 1
                    if id_fields_count > 1:
                        return False, 'Only 1 Id field supported in stream schema (one of ' \
                            'UserId, ClientId and Yclid). See https://yandex.ru/dev/metrika/doc' \
                            '/api2/practice/offline-conv.html#offline-conv__csv'
                if field not in supported_fields:
                    unsupported_fields_in_schema.append(field)

            if unsupported_fields_in_schema:
                return False, f'Unsupported fields: {unsupported_fields_in_schema}. Allowed fields for ' \
                    'stream: {supported_fields}. See https://yandex.ru/dev/metrika/doc'\
                    '/api2/practice/offline-conv.html#offline-conv__csv'
            for required_non_id_field in required_non_id_fields:
                if required_non_id_field not in schema_fields:
                    return False, f'Field {required_non_id_field} is required. ' \
                        'See https://yandex.ru/dev/metrika/doc/api2/practice/offline-conv.html#offline-conv__csv'
            return True, None

    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                "Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth_status, check_auth_message = auth.check_connection()
            if not check_auth_status:
                return check_auth_message

        try:
            counters_on_token_response = requests.get(
                'https://api-metrika.yandex.net/management/v1/counters',
                headers=auth.get_auth_header()
            ).json()
            if counters_on_token_response.get('errors'):
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"An exception occurred: {counters_on_token_response}"
                )
            available_counters_ids = [
                counter['id'] for counter in counters_on_token_response.get('counters', [])]
            if config['counter_id'] not in available_counters_ids:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Counter ID {config['counter_id']} not found with access_token"
                )
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
