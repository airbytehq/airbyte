#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
import logging
import shutil
from datetime import datetime, timedelta
from typing import Iterator, Mapping, MutableMapping

from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_yandex_metrika.aggregated_data_streams.streams import (
    AggregateDataYandexMetrikaReport,
    ReportConfig,
)
from source_yandex_metrika.raw_data_streams.stream import YandexMetrikaRawDataStream
from source_yandex_metrika.raw_data_streams.threads import (
    PreprocessedSlicePartThreadsController,
    YandexMetrikaRawSliceMissingChunksObserver,
)

from .auth import CredentialsCraftAuthenticator
from .raw_data_streams.exceptions import MissingChunkIdsError
from .raw_data_streams.fields import HITS_AVAILABLE_FIELDS, VISITS_AVAILABLE_FIELDS

logger = logging.getLogger("airbyte")
CONFIG_DATE_FORMAT = "%Y-%m-%d"


# Source
class SourceYandexMetrika(AbstractSource):
    def __init__(self):
        self.field_name_map: dict[str, str] | None = None

    def preprocess_raw_stream_slice(
        self,
        stream_name: str,
        stream_slice: Mapping[str, any],
        check_log_request_ability: bool = False,
    ) -> tuple[list[Mapping[str, any]], str]:
        logger.info(f"Preprocessing raw stream slice {stream_slice} for stream {stream_name}...")
        preprocessor = getattr(self, self.raw_data_stream_to_field_map[stream_name]["preprocessor_field_name"])
        is_request_on_server, request_id = preprocessor.check_if_log_request_already_on_server(stream_slice)
        if is_request_on_server:
            logger.info(f"Log request {request_id} already on server.")
        else:
            logger.info(f"Log request was not found on server, creating it.")
            if check_log_request_ability:
                is_request_available, request_ability_msg = preprocessor.check_log_request_ability(stream_slice)
                if not is_request_available:
                    raise Exception(request_ability_msg)

            request_id = preprocessor.create_log_request(stream_slice)
        preprocessed_slice = preprocessor.wait_for_log_request_processed(log_request_id=request_id, stream_slice=stream_slice)
        return [
            {
                "date_from": preprocessed_slice["date_from"],
                "date_to": preprocessed_slice["date_to"],
                "log_request_id": preprocessed_slice["log_request_id"],
                "part": part,
            }
            for part in preprocessed_slice["processed_parts"]
        ], preprocessed_slice["log_request_id"]

    def postprocess_raw_stream_slice(self, stream_name: str, stream_slice, log_request_id: str):
        stream_instance_kwargs = getattr(self, self.raw_data_stream_to_field_map[stream_name]["kwargs_field_name"])
        preprocessor = getattr(self, self.raw_data_stream_to_field_map[stream_name]["preprocessor_field_name"])
        if stream_instance_kwargs["clean_slice_after_successfully_loaded"]:
            logger.info(f"clean_slice_after_successfully_loaded {stream_slice}")
            preprocessor.clean_log_request(log_request_id=log_request_id)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, any] = None,
    ) -> Iterator[AirbyteMessage]:
        connector_state = copy.deepcopy(state or {})

        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)

        stream_instances = {s.name: s for s in self.streams(config)}
        self._stream_to_instance_map = stream_instances

        with create_timer(self.name) as timer:
            shutil.rmtree("output", ignore_errors=True)
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                if not stream_instance:
                    raise KeyError(
                        f"The requested stream {configured_stream.stream.name} was not found in the source."
                        f" Available streams: {stream_instances.keys()}"
                    )
                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        connector_state=connector_state,
                        internal_config=internal_config,
                    )
                except AirbyteTracedException as e:
                    raise e
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        raise AirbyteTracedException.from_exception(e, message=display_message) from e
                    raise e
                finally:
                    timer.finish_event()
                    logger.info(f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())
                    try:
                        shutil.rmtree("output", ignore_errors=True)
                    except:
                        pass

        logger.info(f"Finished syncing {self.name}")
        yield from []

    def _read_stream(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        # self._apply_log_level_to_stream_logger(logger, stream_instance)
        if internal_config.page_size and isinstance(stream_instance, HttpStream):
            logger.info(f"Setting page size for {stream_instance.name} to {internal_config.page_size}")
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
        yield from self._read_full_refresh(logger, stream_instance, configured_stream, internal_config)
        logger.info(f"End of _read_stream stream")

    def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        if stream_instance.__class__.__name__ == "YandexMetrikaRawDataStream":
            stream_instance: YandexMetrikaRawDataStream = stream_instance
            raw_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=configured_stream.cursor_field)
            logger.debug(
                f"Processing raw stream slices for {configured_stream.stream.name}",
                extra={"stream_slices": raw_slices},
            )
            logger.info(f"Raw slices: {raw_slices}")
            with create_timer(self.name) as timer:
                for raw_slice in raw_slices:
                    logger.info(f"Current raw slice: {raw_slice}")
                    preprocessed_slices, log_request_id = self.preprocess_raw_stream_slice(
                        stream_name=stream_instance.name,
                        stream_slice=raw_slice,
                        check_log_request_ability=stream_instance.check_log_requests_ability,
                    )
                    logger.info(f"Current preprocessed slices: {preprocessed_slices}")
                    completed_chunks_observer = YandexMetrikaRawSliceMissingChunksObserver(
                        expected_chunks_ids=[chunk["part"]["part_number"] for chunk in preprocessed_slices]
                    )
                    stream_instance_kwargs = getattr(
                        self,
                        self.raw_data_stream_to_field_map[stream_instance.name]["kwargs_field_name"],
                    )
                    threads_controller = PreprocessedSlicePartThreadsController(
                        stream_instance=stream_instance,
                        stream_instance_kwargs=stream_instance_kwargs,
                        raw_slice=raw_slice,
                        preprocessed_slices_batch=preprocessed_slices,
                        multithreading_threads_count=stream_instance_kwargs["multithreading_threads_count"],
                        timer=timer,
                        completed_chunks_observer=completed_chunks_observer,
                    )
                    logger.info("Threads controller created")
                    logger.info("Run threads process, get into main loop")
                    threads_controller.process_threads()

                    if completed_chunks_observer.is_missing_chunks():
                        raise MissingChunkIdsError(
                            f"Missing chunks {completed_chunks_observer.missing_chunks} for raw slice {raw_slice}",
                        )
                    else:
                        logger.info(
                            "YandexMetrikaRawSliceMissingChunksObserver test completed with no exceptions. "
                            f"completed_chunks_observer.missing_chunks result: {completed_chunks_observer.missing_chunks}"
                        )

                    self.postprocess_raw_stream_slice(
                        stream_name=stream_instance.name, stream_slice=raw_slice, log_request_id=log_request_id
                    )
                    for thread in threads_controller.threads:
                        for record in thread.records:
                            yield self._get_message(record_data_or_message=record, stream=stream_instance)
            yield from []
        else:
            yield from super()._read_full_refresh(logger, stream_instance, configured_stream, internal_config)

    def check_connection(self, logger, config) -> tuple[bool, any]:
        raw_hits_config: dict = config.get("raw_data_hits_report")
        if raw_hits_config.get("is_enabled") == "enabled":
            for f in raw_hits_config.get("fields", []):
                if f not in HITS_AVAILABLE_FIELDS.get_all_fields_names_list():
                    return (
                        False,
                        f'Сырые отчёты - источник "Просмотры" (hits) не может содержать поле "{f}". См. доступные поля: '
                        "https://yandex.ru/dev/metrika/doc/api2/logs/fields/hits.html",
                    )

            for r_f in HITS_AVAILABLE_FIELDS.get_required_fields_names_list():
                if r_f not in raw_hits_config.get("fields", []):
                    return (
                        False,
                        'Сырые отчёты - источник "Просмотры" (hits) должен содержать поля "ym:pv:watchID" и "ym:pv:dateTime"',
                    )

        raw_visits_config: dict = config.get("raw_data_visits_report")
        if raw_visits_config.get("is_enabled") == "enabled":
            for f in raw_visits_config.get("fields", []):
                if f not in VISITS_AVAILABLE_FIELDS.get_all_fields_names_list():
                    return (
                        False,
                        f'Сырые отчёты - источник "Визиты" (visits) не может содержать поле "{f}". См. доступные поля: '
                        "https://yandex.ru/dev/metrika/doc/api2/logs/fields/visits.html",
                    )

            for r_f in VISITS_AVAILABLE_FIELDS.get_required_fields_names_list():
                if r_f not in raw_visits_config.get("fields", []):
                    return (
                        False,
                        'Сырые отчёты - источник "Просмотры" (hits) должен содержать поля "ym:s:visitID" и "ym:s:dateTime"',
                    )

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            auth.check_connection(raise_exception=True)

        self.streams(config)

        for stream_n, stream in enumerate(
            filter(
                lambda stream: stream.__class__.__name__ == "AggregateDataYandexMetrikaReport",
                self.streams(config),
            )
        ):
            test_response = stream.make_test_request()
            test_response_data = test_response.json()
            if test_response_data.get("errors"):
                return False, f"Table #{stream_n} ({stream.name}) error: " + test_response_data.get("message")

        for stream_n, stream in enumerate(
            filter(
                lambda stream: stream.__class__.__name__ == "YandexMetrikaRawDataStream",
                self.streams(config),
            )
        ):
            stream: YandexMetrikaRawDataStream
            preprocessor = stream.preprocessor
            if stream.check_log_requests_ability:
                can_replicate_all_slices, message = preprocessor.check_stream_slices_ability()
                if not can_replicate_all_slices:
                    return can_replicate_all_slices, message

        return True, None

    def transform_config(self, raw_config: dict[str, any]) -> Mapping[str, any]:
        transformed_config = {
            "counter_id": int(raw_config["counter_id"]),
            "aggregate_tables": [
                ReportConfig(
                    name=agg_report_config.get("name"),
                    counter_id=raw_config["counter_id"],
                    preset_name=agg_report_config.get("preset_name"),
                    metrics=agg_report_config.get("metrics"),
                    dimensions=agg_report_config.get("dimensions"),
                    filters=agg_report_config.get("filters"),
                    direct_client_logins=agg_report_config.get("direct_client_logins"),
                    attribution=agg_report_config.get("attribution"),
                    goal_id=agg_report_config.get("goal_id"),
                    date_group=agg_report_config.get("date_group"),
                    currency=agg_report_config.get("currency"),
                    experiment_ab_id=agg_report_config.get("experiment_ab_id"),
                )
                for agg_report_config in raw_config.get("aggregated_reports", [])
            ],
        }
        transformed_config.update(self.transform_date_range(raw_config))
        raw_config.update(transformed_config)

        self.field_name_map = self.get_field_name_map(config=raw_config)
        return raw_config

    def transform_date_range(self, config: Mapping[str, any]) -> dict[str, any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - timedelta(days=date_range["last_days_count"])
            if date_range.get("should_load_today", False):
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(prepared_range["date_from"], CONFIG_DATE_FORMAT)

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(prepared_range["date_to"], CONFIG_DATE_FORMAT)
        config["prepared_date_range"] = prepared_range
        return config

    def get_auth(self, config: Mapping[str, any]) -> TokenAuthenticator:
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
            raise Exception("Неверный типа авторизации. Доступные: access_token_auth и credentials_craft_auth")

    @staticmethod
    def get_field_name_map(config: Mapping[str, any]) -> dict[str, str]:
        """Get values that needs to be replaced and their replacements"""
        field_name_map: list[dict[str, str]] | None
        if not (field_name_map := config.get("field_name_map")):
            return {}
        else:
            return {item["old_value"]: item["new_value"] for item in field_name_map}

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        # properties = spec.connectionSpecification["properties"]
        # raw_data_hits_report_property = properties["raw_data_hits_report"]["oneOf"][0]["properties"]
        # raw_data_visits_report_property = properties["raw_data_visits_report"]["oneOf"][0]["properties"]
        # agg_data_metrics_property = properties["aggregated_reports"]["items"]["properties"]["metrics"]
        # agg_data_dimendions_property = properties["aggregated_reports"]["items"]["properties"]["dimensions"]

        # agg_data_metrics_property["items"] = {
        #     "title": "AggDataMetricsField",
        #     "enum": list(map(lambda field: field[0], _RAW_METRICS_FIELDS)),
        # }
        # agg_data_dimendions_property["items"] = {
        #     "title": "AggDataDimensionsField",
        #     "enum": _RAW_GROUP_FIELDS,
        # }

        # raw_data_hits_report_property["fields"]["items"] = {
        #     "title": "RawDataHitsReportField",
        #     "enum": list(map(lambda field: field["name"], HITS_AVAILABLE_FIELDS.get_all_fields())),
        # }
        # raw_data_visits_report_property["fields"]["items"] = {
        #     "title": "RawDataVisitsReportField",
        #     "enum": list(map(lambda field: field["name"], VISITS_AVAILABLE_FIELDS.get_all_fields())),
        # }
        return spec

    def streams(self, config: Mapping[str, any], init_for_test: bool = False) -> list[Stream]:
        config = self.transform_config(config)
        auth = self.get_auth(config)

        self.raw_data_stream_to_field_map = {
            "raw_data_hits": {
                "kwargs_field_name": "raw_data_hits_stream_kwargs",
                "in_config_field_name": "raw_data_hits_report",
                "source": "hits",
                "preprocessor_field_name": "raw_data_hits_preprocessor",
            },
            "raw_data_visits": {
                "kwargs_field_name": "raw_data_visits_stream_kwargs",
                "in_config_field_name": "raw_data_visits_report",
                "source": "visits",
                "preprocessor_field_name": "raw_data_visits_preprocessor",
            },
        }
        raw_data_streams = []
        for stream_name in self.raw_data_stream_to_field_map.keys():
            source_to_stream_config = self.raw_data_stream_to_field_map[stream_name]
            stream_config = config.get(source_to_stream_config["in_config_field_name"], {})
            if stream_config["is_enabled"] == "enabled":
                if not stream_config:
                    raise Exception(f"Конфигурация для {source_to_stream_config['in_config_field_name']} не предоставлена.")
                setattr(
                    self,
                    source_to_stream_config["kwargs_field_name"],
                    dict(
                        authenticator=auth,
                        counter_id=config["counter_id"],
                        date_from=config["prepared_date_range"]["date_from"],
                        date_to=config["prepared_date_range"]["date_to"],
                        split_range_days_count=stream_config.get("split_range_days_count"),
                        log_source=source_to_stream_config["source"],
                        fields=stream_config["fields"],
                        clean_slice_after_successfully_loaded=stream_config.get("clean_every_log_request_after_success", False),
                        clean_log_requests_before_replication=stream_config.get("clean_log_requests_before_replication", False),
                        check_log_requests_ability=stream_config.get("check_log_requests_ability", False),
                        multithreading_threads_count=stream_config.get("multithreading_threads_count", 1),
                        created_for_test=init_for_test,
                    ),
                )

                stream = YandexMetrikaRawDataStream(
                    **getattr(
                        self,
                        source_to_stream_config["kwargs_field_name"],
                    ),
                    field_name_map=self.field_name_map,
                )
                raw_data_streams.append(stream)
                setattr(self, source_to_stream_config["preprocessor_field_name"], stream.preprocessor)

        agg_data_streams = [
            AggregateDataYandexMetrikaReport(
                authenticator=auth, global_config=config, report_config=stream_config, field_name_map=self.field_name_map
            )
            for stream_config in config.get("aggregated_reports", [])
        ]
        return [*raw_data_streams, *agg_data_streams]
