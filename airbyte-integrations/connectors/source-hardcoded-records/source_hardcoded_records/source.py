# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import cProfile
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Customers, DummyFields, Products


DEFAULT_COUNT = 1_000


class SourceHardcodedRecords(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            return True, None
        else:
            return False, "Count option is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT

        return [Products(count), Customers(count), DummyFields(count)]

    def __init__(self) -> None:
        self._profiler: cProfile.Profile | None = None

        super().__init__()
        self.start_tracer()

    def __del__(self) -> None:
        if self._profiler is not None:
            self.stop_tracer()

    def start_tracer(self) -> None:
        if "DD_AGENT_HOST" in os.environ:
            # DataDog tracing is enabled. No need to create cProfile profiler
            return

        self._profiler = cProfile.Profile()
        self._profiler.enable()

    def stop_tracer(self) -> None:
        # Stop the profiler if it's running
        self._profiler.disable()

        # Get the current timestamp and profile file path
        timestamp_str: str = datetime.now(tz=None).strftime("%Y%m%d_%H%M%S")  # noqa: DTZ005 # Intentional use of local timezone
        profile_file_path = Path(f"source_hardcoded_records_{timestamp_str}.prof").absolute()
        logging.info(f"Dumping profiler stats to '{profile_file_path:!s}'...")
        self._profiler.dump_stats(profile_file_path)
