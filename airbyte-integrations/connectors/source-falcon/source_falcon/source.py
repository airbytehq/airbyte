#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
import traceback
from cgitb import reset
from copy import deepcopy
from typing import Any, List, Mapping, Tuple

from source_falcon.schema_helper import ReportXMLSchemaHelper
from typing_extensions import override

from airbyte_cdk import HttpAvailabilityStrategy, Stream
from airbyte_cdk.sources.declarative.yaml_declarative_source import (
    YamlDeclarativeSource,
)


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""
import json

from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DeclarativeStream as DeclarativeStreamModel,
)


REPORTS_STREAM_NAME = "Reports"


# Declarative Source
class SourceFalcon(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _raas_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self._emit_manifest_debug_message(
            extra_args={
                "source_name": self.name,
                "parsed_config": json.dumps(self._source_config),
            }
        )
        stream_configs = self._stream_configs(self._source_config)
        reports_stream_template = [x for x in stream_configs if x["name"] == REPORTS_STREAM_NAME][0]
        raas_streams = self._get_custom_stream_config_reports_from_template(config, reports_stream_template)
        source_streams = [
            self._constructor.create_component(
                DeclarativeStreamModel,
                stream_config,
                config,
                emit_connector_builder_messages=self._emit_connector_builder_messages,
            )
            for stream_config in self._initialize_cache_for_parent_streams(deepcopy(raas_streams))
        ]

        return source_streams

    def _rest_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_configs = self._stream_configs(self._source_config)
        # removes report based stream
        rest_streams = [x for x in stream_configs if x["name"] != REPORTS_STREAM_NAME]
        source_streams = [
            self._constructor.create_component(
                DeclarativeStreamModel,
                stream_config,
                config,
                emit_connector_builder_messages=self._emit_connector_builder_messages,
            )
            for stream_config in self._initialize_cache_for_parent_streams(deepcopy(rest_streams))
        ]
        return source_streams

    @override
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if config["credentials"]["auth_type"] == "RAAS":
            return self._raas_streams(config)

        return self._rest_streams(config)

    def _get_custom_stream_config_reports_from_template(
        self, config: Mapping[str, Any], reports_stream_template: Mapping[str, Any]
    ) -> List[Mapping[str, Any]]:
        stream_configs = []
        for report_id in config["credentials"]["report_ids"]:
            new_stream = deepcopy(reports_stream_template)
            new_stream["name"] = report_id
            new_stream["retriever"]["requester"]["path"] = report_id
            new_stream["schema_loader"]["parameters"] = {"report_id": report_id}
            # # AdFields transformations, should be updated when transformations in manifest were changed
            new_transformations = (
                new_stream["transformations"][0]["fields"] + ReportXMLSchemaHelper(config, report_id).fields_transform_string_array()
            )
            new_stream["transformations"][0]["fields"] = new_transformations

            stream_configs.append(new_stream)
        return stream_configs

    def _check_stream(self, logger: logging.Logger, stream: Stream) -> Tuple[bool, Any]:
        availability_strategy = HttpAvailabilityStrategy()
        try:
            stream_is_available, reason = availability_strategy.check_availability(stream, logger)
            if not stream_is_available:
                return False, reason
        except Exception as error:
            logger.error(f"Encountered an error trying to connect to stream {stream.name}. Error: \n {traceback.format_exc()}")
            return False, f"Unable to connect to stream {stream.name} - {error}"
        return True, None

    def _check_raas_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        streams = self.streams(config)  # type: ignore # source is always a DeclarativeSource, but this parameter type adheres to the outer interface
        if len(streams) == 0:
            return False, f"No streams to connect to from source {self.name}"
        stream = streams[0]
        return self._check_stream(logger, stream)

    def _check_rest_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        streams = self.streams(config)  # type: ignore # source is always a DeclarativeSource, but this parameter type adheres to the outer interface
        stream = [s for s in streams if s.name == "workers"][0]
        return self._check_stream(logger, stream)

    @override
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if config["credentials"]["auth_type"] == "RAAS":
            return self._check_raas_connection(logger, config)
        return self._check_rest_connection(logger, config)
