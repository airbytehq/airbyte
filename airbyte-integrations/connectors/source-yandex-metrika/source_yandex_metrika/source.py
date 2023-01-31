#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging
import time
from collections import deque
from threading import Thread
from typing import Any, Callable, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteStream, SyncMode, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.event_timing import EventTimer, create_timer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_yandex_metrika.stream import YandexMetrikaStream

from .auth import CredentialsCraftAuthenticator
from .fields import HITS_AVAILABLE_FIELDS, VISITS_AVAILABLE_FIELDS

logger = logging.getLogger("airbyte")


class LogMessagesPoolConsumer:
    def log_info(self, message: str):
        logger.info(f'({self.__class__.__name__}) - {message}')


class PreprocessedSlicePartProcessorThread(Thread, LogMessagesPoolConsumer):
    def __init__(
        self,
        name: str,
        stream_slice: Mapping[str, Any],
        stream_instance: YandexMetrikaStream,
        on_process_end: Callable,
        on_raw_record_processed: Callable,
        timer: EventTimer
    ):
        Thread.__init__(self, name=name, daemon=True)
        self.stream_slice = stream_slice
        self.on_process_end = on_process_end
        self.stream_instance = stream_instance
        self.completed = False
        self.records_count = 0
        self.on_raw_record_processed = on_raw_record_processed
        self.timer = timer

    def process_log_request(self):
        try:
            for record in self.stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=self.stream_slice):
                print(self.on_raw_record_processed(
                    data=record, stream_name=self.stream_instance.name).json(exclude_unset=True))
                self.records_count += 1
        except AirbyteTracedException as e:
            raise e
        except Exception as e:
            logger.exception(
                f"Encountered an exception while reading stream {self.stream_instance.name}")
            display_message = self.stream_instance.get_error_display_message(e)
            if display_message:
                raise AirbyteTracedException.from_exception(
                    e, message=display_message) from e
            raise e
        finally:
            self.timer.finish_event()
            logger.info(f"Finished syncing {self.stream_instance.name}")
            logger.info(self.timer.report())

    def run(self):
        self.log_info(f'Start processing thread')
        self.process_log_request()
        self.log_info(
            f'End processing thread with {self.records_count} records')
        self.completed = True
        self.on_process_end()


class PreprocessedSlicePartThreadsController(LogMessagesPoolConsumer):
    def __init__(
        self,
        stream_instance: YandexMetrikaStream,
        stream_instance_kwargs: Mapping[str, Any],
        preprocessed_slices_batch: List[Mapping[str, Any]],
        raw_slice: Mapping[str, Any],
        on_raw_record_processed: Callable,
        timer: EventTimer,
        multithreading_threads_count: int = 1,
    ):
        self.raw_slice = raw_slice
        self.current_stream_slices = deque()
        self.stream_instance: YandexMetrikaStream = stream_instance
        for slice in preprocessed_slices_batch:
            self.current_stream_slices.append(slice)
        self.stream_instance_kwargs = stream_instance_kwargs
        self.threads: List[Thread] = []
        self.multithreading_threads_count = multithreading_threads_count
        self.on_raw_record_processed = on_raw_record_processed
        self.timer = timer

    @property
    def is_running(self) -> bool:
        return bool(list(filter(lambda stream: not stream.completed, self.threads)))

    def run_thread_instance(self):
        try:
            stream_slice: Mapping[str,
                                  Any] = self.current_stream_slices.pop()
            thread_name = 'Thread-' + "-".join(
                map(str, stream_slice.values())
            ) + '-' + self.stream_instance.name
            self.log_info(f"Run processor thread instanse {thread_name}")

            thread = PreprocessedSlicePartProcessorThread(
                name=thread_name,
                stream_slice=stream_slice,
                on_process_end=self.run_thread_instance,
                stream_instance=self.stream_instance,
                on_raw_record_processed=self.on_raw_record_processed,
                timer=self.timer
            )
            self.threads.append(thread)
            thread.start()
        except IndexError:
            self.log_info(
                f'There is no more parts slices for this raw slice ({self.raw_slice})')
            if not self.is_running:
                pass

    def process_threads(self):
        for _ in range(self.multithreading_threads_count):
            self.run_thread_instance()


# Source
class SourceYandexMetrika(AbstractSource):
    def preprocess_raw_stream_slice(self, stream_slice: Mapping[str, Any]):
        logger.info(f"Preprocessing raw stream slice {stream_slice}...")

        is_request_on_server, request_id = self.preprocessor.check_if_log_request_already_on_server(
            stream_slice)
        if is_request_on_server:
            logger.info(
                f"Log request {request_id} already on server.")
        else:
            logger.info(
                f"Log request was not found on server, creating it.")

            request_ability = self.preprocessor.check_log_request_ability(
                stream_slice)
            if not request_ability[0]:
                raise Exception(request_ability[1])

            request_id = self.preprocessor.create_log_request(
                stream_slice)
        preprocessed_slice = self.preprocessor.wait_for_log_request_processed(
            log_request_id=request_id, stream_slice=stream_slice
        )
        return [
            {
                'date_from': preprocessed_slice['date_from'],
                'date_to': preprocessed_slice['date_to'],
                'log_request_id': preprocessed_slice['log_request_id'],
                'part': part,
            }
            for part
            in preprocessed_slice['processed_parts']
        ]

    def postprocess_raw_stream_slice(self, stream_slice):
        if self.stream_instance_kwargs['clean_slice_after_successfully_loaded']:
            logger.info(
                f'clean_slice_after_successfully_loaded {stream_slice}')
            self.preprocessor.clean_log_request(
                self, stream_slice['log_request_id'])

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-protocol."""
        connector_state = copy.deepcopy(state or {})
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        stream_instances = {s.name: s for s in self.streams(config)}
        self._stream_to_instance_map = stream_instances
        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(
                    configured_stream.stream.name)
                if not stream_instance:
                    raise KeyError(
                        f"The requested stream {configured_stream.stream.name} was not found in the source."
                        f" Available streams: {stream_instances.keys()}"
                    )
                try:
                    timer.start_event(
                        f"Syncing stream {configured_stream.stream.name}")
                    self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        connector_state=connector_state,
                        internal_config=internal_config,
                    )
                except AirbyteTracedException as e:
                    raise e
                except Exception as e:
                    logger.exception(
                        f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    display_message = stream_instance.get_error_display_message(
                        e)
                    if display_message:
                        raise AirbyteTracedException.from_exception(
                            e, message=display_message) from e
                    raise e
                finally:
                    timer.finish_event()
                    logger.info(
                        f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")

    def _read_stream(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        self._apply_log_level_to_stream_logger(logger, stream_instance)
        if internal_config.page_size and isinstance(stream_instance, HttpStream):
            logger.info(
                f"Setting page size for {stream_instance.name} to {internal_config.page_size}")
            stream_instance.page_size = internal_config.page_size
        logger.debug(
            f"Syncing configured stream: {configured_stream.stream.name}",
            extra={
                "sync_mode": configured_stream.sync_mode,
                "primary_key": configured_stream.primary_key,
                "cursor_field": configured_stream.cursor_field,
            },
        )
        logger.debug(
            f"Syncing stream instance: {stream_instance.name}",
            extra={
                "primary_key": stream_instance.primary_key,
                "cursor_field": stream_instance.cursor_field,
            },
        )

        logger.info(f"Syncing stream: {configured_stream.stream.name} ")
        self._read_full_refresh(logger, stream_instance,
                                configured_stream, internal_config)
        logger.info(f"End of _read_stream stream")

    def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        raw_slices = stream_instance.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=configured_stream.cursor_field)
        logger.debug(f"Processing raw stream slices for {configured_stream.stream.name}", extra={
                     "stream_slices": raw_slices})
        logger.info(f'Raw slices: {raw_slices}')
        with create_timer(self.name) as timer:

            for raw_slice in raw_slices:
                logger.info(f'Current raw slice: {raw_slice}')
                preprocessed_slices = self.preprocess_raw_stream_slice(
                    stream_slice=raw_slice)
                logger.info(
                    f'Current preprocessed slices: {preprocessed_slices}')
                threads_controller = PreprocessedSlicePartThreadsController(
                    stream_instance=stream_instance,
                    stream_instance_kwargs=self.stream_instance_kwargs,
                    raw_slice=raw_slice,
                    preprocessed_slices_batch=preprocessed_slices,
                    multithreading_threads_count=self.stream_instance_kwargs[
                        'multithreading_threads_count'
                    ],
                    on_raw_record_processed=self._as_airbyte_record,
                    timer=timer
                )
                logger.info('Threads controller created')
                threads_controller.process_threads()
                logger.info('Run threads process, get into main loop')

                while threads_controller.is_running:
                    time.sleep(1)
                self.postprocess_raw_stream_slice(
                    dict(**raw_slice, log_request_id=preprocessed_slices[0]['log_request_id']))

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        if config["log_source"] == "hits":
            for f in config["fields"]:
                if f not in HITS_AVAILABLE_FIELDS.get_all_fields_names_list():
                    return (
                        False,
                        f'Logs for source "hits" can\'t contain "{f}" field. See '
                        "https://yandex.ru/dev/metrika/doc/api2/logs/fields/hits.html "
                        "for available fields list",
                    )

            for r_f in HITS_AVAILABLE_FIELDS.get_required_fields_names_list():
                if r_f not in config["fields"]:
                    return False, 'Logs for source "hits" must contain required fields "ym:pv:watchID" and "ym:pv:dateTime"'

        if config["log_source"] == "visits":
            for f in config["fields"]:
                if f not in VISITS_AVAILABLE_FIELDS.get_all_fields_names_list():
                    return (
                        False,
                        f'Logs for source "visits" can\'t contain "{f}" field. See '
                        "https://yandex.ru/dev/metrika/doc/api2/logs/fields/visits.html for available fields list",
                    )

            for r_f in VISITS_AVAILABLE_FIELDS.get_required_fields_names_list():
                if r_f not in config["fields"]:
                    return False, 'Logs for source "visits" must contain required fields "ym:s:visitID" and "ym:s:dateTime"'

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        self.streams(config)
        if self.stream_instance_kwargs['check_log_requests_ability']:
            can_replicate_all_slices, message = self.preprocessor.check_stream_slices_ability()
            if not can_replicate_all_slices:
                return can_replicate_all_slices, message
        return True, None

    def transform_config(self, raw_config: Mapping[str, Any]) -> Mapping[str, Any]:
        transformed_config = {"counter_id": int(
            raw_config["counter_id"]), "custom_data": json.loads(raw_config["custom_data_json"])}
        raw_config.update(transformed_config)
        return raw_config

    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"], auth_method="OAuth")
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                "Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def streams(self, config: Mapping[str, Any], created_for_test: bool = False) -> List[Stream]:
        config = self.transform_config(config)
        self.stream_instance_kwargs = dict(
            authenticator=self.get_auth(config),
            counter_id=config["counter_id"],
            date_from=config.get("date_from"),
            date_to=config.get("date_to"),
            last_days=config.get("last_days"),
            split_reports=config.get(
                "chunk_reports", {"split_mode_type": "do_not_split_mode"}),
            log_source=config["log_source"],
            fields=config["fields"],
            client_name_const=config.get("client_name"),
            product_name_const=config.get("product_name"),
            custom_data_const=config.get("custom_data"),
            clean_slice_after_successfully_loaded=config.get(
                "clean_every_log_request_after_success", False),
            clean_log_requests_before_replication=config.get(
                "clean_log_requests_before_replication", False),
            check_log_requests_ability=config.get(
                'check_log_requests_ability'),
            multithreading_threads_count=config.get(
                'multithreading_threads_count', 1),
            created_for_test=created_for_test,
        )
        stream = YandexMetrikaStream(**self.stream_instance_kwargs)
        self.preprocessor = stream.preprocessor
        return [stream]
