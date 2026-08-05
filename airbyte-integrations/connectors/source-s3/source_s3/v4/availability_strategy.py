#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
import traceback
from typing import Optional, Tuple

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.availability_strategy import (
    DefaultFileBasedAvailabilityStrategy,
)
from airbyte_cdk.sources.file_based.exceptions import (
    CheckAvailabilityError,
    FileBasedSourceError,
)
from airbyte_cdk.sources.file_based.file_types.parquet_parser import ParquetParser
from source_s3.v4.config import S3FileBasedStreamConfig


class SourceS3AvailabilityStrategy(DefaultFileBasedAvailabilityStrategy):
    """
    Custom availability strategy that optionally skips the full parse check for Parquet
    streams to avoid OOM errors on large files.  The skip is gated behind the per-stream
    ``skip_full_check_for_parquet`` flag (default False).  Non-Parquet streams and streams
    without the flag always use the default check path.
    """

    def check_availability_and_parsability(
        self,
        stream,
        logger: logging.Logger,
        source: Optional[Source],
    ) -> Tuple[bool, Optional[str]]:
        parser = stream.get_parser()

        skip_flag = isinstance(stream.config, S3FileBasedStreamConfig) and stream.config.skip_full_check_for_parquet
        if not (isinstance(parser, ParquetParser) and skip_flag):
            return super().check_availability_and_parsability(stream, logger, source)

        # Parquet path: validate config, list files, and open the file to verify
        # accessibility — but skip the full record parse to avoid loading entire
        # row groups into memory.
        config_check_result, config_check_error_message = parser.check_config(stream.config)
        if config_check_result is False:
            return False, config_check_error_message

        try:
            file = self._check_list_files(stream)
            handle = stream.stream_reader.open_file(file, parser.file_read_mode, None, logger)
            handle.close()
        except AirbyteTracedException as ate:
            raise ate
        except CheckAvailabilityError:
            return False, "".join(traceback.format_exc())
        except Exception as exc:
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri) from exc

        return True, None
