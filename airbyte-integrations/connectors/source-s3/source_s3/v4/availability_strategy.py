#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
import traceback
from typing import Optional, Tuple

import pyarrow as pa
import pyarrow.parquet as pq

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.availability_strategy import (
    DefaultFileBasedAvailabilityStrategy,
)
from airbyte_cdk.sources.file_based.exceptions import (
    CheckAvailabilityError,
    CustomFileBasedException,
    FileBasedSourceError,
)
from airbyte_cdk.sources.file_based.file_types.parquet_parser import ParquetParser
from source_s3.v4.config import S3FileBasedStreamConfig


class SourceS3AvailabilityStrategy(DefaultFileBasedAvailabilityStrategy):
    """
    Custom availability strategy that optionally performs a lightweight Parquet parse during CHECK
    to avoid OOMs. Controlled by stream.config.light_parquet_check (default False).
    """

    def check_availability_and_parsability(
        self,
        stream,
        logger: logging.Logger,
        source: Optional[Source],
    ) -> Tuple[bool, Optional[str]]:
        parser = stream.get_parser()
        use_light_check = (
            isinstance(parser, ParquetParser)
            and isinstance(getattr(stream, "config", None), S3FileBasedStreamConfig)
            and stream.config.light_parquet_check
        )

        if not use_light_check:
            return super().check_availability_and_parsability(stream, logger, source)

        # Lightweight path: list & open file, then sample one column/row only.
        config_check_result, config_check_error_message = parser.check_config(stream.config)
        if config_check_result is False:
            return False, config_check_error_message

        try:
            file = self._check_list_files(stream)
            self._check_parse_record_light(stream, file, logger)
        except AirbyteTracedException as ate:
            raise ate
        except CheckAvailabilityError:
            return False, "".join(traceback.format_exc())

        return True, None

    def _check_parse_record_light(self, stream, file, logger: logging.Logger) -> None:
        parser = stream.get_parser()

        try:
            with stream.stream_reader.open_file(file, parser.file_read_mode, getattr(parser, "ENCODING", None), logger) as fp:
                parquet_file = pq.ParquetFile(fp)
                column_names = parquet_file.schema_arrow.names
                if not column_names:
                    raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri)

                first_col = column_names[0]
                batches = parquet_file.iter_batches(batch_size=1, columns=[first_col], use_threads=False)
                try:
                    batch = next(batches)
                except StopIteration:
                    # Empty file is still OK for availability; align with default behavior.
                    return

                # Materialize one row to ensure decoding succeeds. Note: we intentionally skip full schema validation
                # here to avoid loading entire row groups; schema mismatches will surface during sync.
                _ = batch.to_pylist()[0]

        except CustomFileBasedException as exc:
            raise CheckAvailabilityError(str(exc), stream=stream.name) from exc
        except AirbyteTracedException as ate:
            raise ate
        except (pa.ArrowInvalid, OSError, ValueError) as exc:  # pragma: no cover - expected read/parse failures
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri) from exc
        except Exception as exc:  # pragma: no cover - defensive broad fallback
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri) from exc

