# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A Parquet cache implementation."""

from __future__ import annotations

import gzip
import json
from typing import IO, TYPE_CHECKING, cast

import orjson
from overrides import overrides

from airbyte._writers.file_writers import (
    FileWriterBase,
)


if TYPE_CHECKING:
    from pathlib import Path

    from airbyte.records import StreamRecord


class JsonlWriter(FileWriterBase):
    """A Jsonl cache implementation."""

    default_cache_file_suffix = ".jsonl.gz"
    prune_extra_fields = True

    @overrides
    def _open_new_file(
        self,
        file_path: Path,
    ) -> IO[str]:
        """Open a new file for writing."""
        return cast(
            IO[str],
            gzip.open(  # noqa: SIM115  # Avoiding context manager
                file_path,
                mode="wt",
                encoding="utf-8",
            ),
        )

    @overrides
    def _write_record_dict(
        self,
        record_dict: StreamRecord,
        open_file_writer: IO[str],
    ) -> None:
        # If the record is too nested, `orjson` will fail with error `TypeError: Recursion
        # limit reached`. If so, fall back to the slower `json.dumps`.
        try:
            open_file_writer.write(orjson.dumps(record_dict).decode(encoding="utf-8") + "\n")
        except TypeError:
            # Using isoformat method for datetime serialization
            open_file_writer.write(
                json.dumps(record_dict, default=lambda _: _.isoformat()) + "\n",
            )
