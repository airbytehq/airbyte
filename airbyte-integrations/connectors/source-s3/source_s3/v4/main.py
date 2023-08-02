#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import sys
import traceback
from datetime import datetime
from typing import List, Any, Mapping, Tuple, Optional

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.models import ConnectorSpecification

from airbyte_cdk.sources.streams import Stream
from source_s3.source import SourceS3Spec, SourceS3
from source_s3.v4 import Config, SourceS3StreamReader
from airbyte_cdk.sources import AbstractSource


class AdaptedSourceS3(AbstractSource):
    def __init__(self, source: FileBasedSource):
        self._source = source

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return self._source.check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._source.streams(config)

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        parent_connection_spec = self._source.spec(*args, **kwargs)
        parent_schema = parent_connection_spec.connectionSpecification
        # There cannot be required fields because legacy configs wouldn't have them
        parent_schema["required"] = []
        return parent_connection_spec


def get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    try:
        return AdaptedSourceS3(FileBasedSource(SourceS3StreamReader(), Config, catalog_path))
    except Exception:
        print(
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=int(datetime.now().timestamp() * 1000),
                    error=AirbyteErrorTraceMessage(
                        message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance.",
                        stack_trace=traceback.format_exc(),
                    ),
                )
            ).json()
        )
        return None


if __name__ == "__main__":
    _args = sys.argv[1:]
    source = get_source(_args)
    if source:
        launch(source, _args)
