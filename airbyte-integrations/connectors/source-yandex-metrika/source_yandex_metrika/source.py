#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging
import shutil

from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteStream, SyncMode, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_yandex_metrika.stream import YandexMetrikaStream

from source_yandex_metrika.threads import PreprocessedSlicePartThreadsController, YandexMetrikaRawSliceMissingChunksObserver
from .auth import CredentialsCraftAuthenticator
from .fields import HITS_AVAILABLE_FIELDS, VISITS_AVAILABLE_FIELDS
from .exceptions import MissingChunkIdsError

logger = logging.getLogger("airbyte")


# Source
class SourceYandexMetrika(AbstractSource):
    def preprocess_raw_stream_slice(self, stream_slice: Mapping[str, Any], check_log_request_ability: bool = False,) -> List[Mapping[str, Any]]:
        logger.info(f"Preprocessing raw stream slice {stream_slice}...")

        is_request_on_server, request_id = self.preprocessor.check_if_log_request_already_on_server(
            stream_slice)
        if is_request_on_server:
            logger.info(
                f"Log request {request_id} already on server.")
        else:
            logger.info(
                f"Log request was not found on server, creating it.")
            if check_log_request_ability:
                is_request_available, request_ability_msg = self.preprocessor.check_log_request_ability(
                    stream_slice)
                if not is_request_available:
                    raise Exception(request_ability_msg)

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
            self.preprocessor.clean_log_request(stream_slice['log_request_id'])

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-protocol."""
        shutil.rmtree('output', ignore_errors=True)
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
                    try:
                        shutil.rmtree('output', ignore_errors=True)
                    except:
                        pass

        logger.info(f"Finished syncing {self.name}")
        yield from []

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
                    stream_slice=raw_slice, check_log_request_ability=self.stream_instance_kwargs[
                        'check_log_requests_ability'
                    ])
                logger.info(
                    f'Current preprocessed slices: {preprocessed_slices}')
                completed_chunks_observer = YandexMetrikaRawSliceMissingChunksObserver(
                        expected_chunks_ids=[chunk['part']['part_number'] for chunk in preprocessed_slices]
                    )
                threads_controller = PreprocessedSlicePartThreadsController(
                    stream_instance=stream_instance,
                    stream_instance_kwargs=self.stream_instance_kwargs,
                    raw_slice=raw_slice,
                    preprocessed_slices_batch=preprocessed_slices,
                    multithreading_threads_count=self.stream_instance_kwargs[
                        'multithreading_threads_count'
                    ],
                    on_raw_record_processed=self._as_airbyte_record,
                    timer=timer,
                    completed_chunks_observer=completed_chunks_observer,
                )
                logger.info('Threads controller created')
                logger.info('Run threads process, get into main loop')
                threads_controller.process_threads()

                if completed_chunks_observer.is_missing_chunks():
                    raise MissingChunkIdsError(f"Missing chunks {completed_chunks_observer.missing_chunks} for raw slice {raw_slice}")
                else:
                    logger.info(
                        'YandexMetrikaRawSliceMissingChunksObserver test completed with no exceptions. '
                        f'completed_chunks_observer.missing_chunks result: {completed_chunks_observer.missing_chunks}'
                    )

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
            auth.check_connection(raise_exception=True)

        self.streams(config)
        if self.stream_instance_kwargs['check_log_requests_ability']:
            can_replicate_all_slices, message = self.preprocessor.check_stream_slices_ability()
            if not can_replicate_all_slices:
                return can_replicate_all_slices, message
        return True, None

    def transform_config(self, raw_config: dict[str, Any]) -> Mapping[str, Any]:
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
                check_connection=True,
                raise_exception_on_check=True,
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
                'check_log_requests_ability', False),
            multithreading_threads_count=config.get(
                'multithreading_threads_count', 1),
            created_for_test=created_for_test,
        )
        stream = YandexMetrikaStream(**self.stream_instance_kwargs)
        self.preprocessor = stream.preprocessor
        return [stream]
