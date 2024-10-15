# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A simple progress bar for the command line and IPython notebooks.

Note: Some runtimes (e.g. Dagger) may not support Rich Live views, and sometimes because they _also_
use Rich, and Rich only supports one live view at a time. PyAirbyte will try to use smart defaults
based on your execution environment.

If you experience issues, you can force plain text status reporting by setting the environment
variable `NO_LIVE_PROGRESS=1`.

Logging is controlled by the `AIRBYTE_LOGGING_ROOT` and `AIRBYTE_STRUCTURED_LOGGING` environment
variables, as described in `airbyte.logs`. If `AIRBYTE_STRUCTURED_LOGGING` is set, logs will be
written in JSONL format. Otherwise, log files will be written as text.
"""

from __future__ import annotations

import datetime
import importlib
import json
import math
import os
import sys
import time
from collections import defaultdict
from contextlib import suppress
from enum import Enum, auto
from typing import IO, TYPE_CHECKING, Any, Literal, cast

import pendulum
from rich.errors import LiveError
from rich.live import Live as RichLive
from rich.markdown import Markdown as RichMarkdown

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStreamStatus,
)

from airbyte_cdk.sql import logs
from airbyte_cdk.sql._message_iterators import _new_stream_success_message
from airbyte_cdk.sql import meta
from airbyte_cdk.sql.telemetry import (
    EventState,
    EventType,
    send_telemetry,
)
from airbyte_cdk.sql.logs import get_global_file_logger


if TYPE_CHECKING:
    import logging
    from collections.abc import Generator, Iterable
    from types import ModuleType

    from structlog import BoundLogger

    from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator
    from airbyte_cdk.sql.caches.base import CacheBase
    from airbyte_cdk.sql.destinations.base import Destination
    from airbyte_cdk.sql.sources.base import Source

IS_REPL = hasattr(sys, "ps1")  # True if we're in a Python REPL, in which case we can use Rich.
HORIZONTAL_LINE = "------------------------------------------------\n"

DEFAULT_REFRESHES_PER_SECOND = 1.3
"""The default number of times per second to refresh the progress view."""

MAX_ITEMIZED_STREAMS = 3
"""The maximum number of streams to itemize in the progress view."""

ipy_display: ModuleType | None
try:
    # Default to IS_NOTEBOOK=False if a TTY is detected.
    IS_NOTEBOOK = not sys.stdout.isatty()
    ipy_display = importlib.import_module("IPython.display")

except ImportError:
    # If IPython is not installed, then we're definitely not in a notebook.
    ipy_display = None
    IS_NOTEBOOK = False


class ProgressStyle(Enum):
    """An enum of progress bar styles."""

    AUTO = auto()
    """Automatically select the best style for the environment."""

    RICH = auto()
    """A Rich progress bar."""

    IPYTHON = auto()
    """Use IPython display methods."""

    PLAIN = auto()
    """A plain text progress print."""

    NONE = auto()
    """Skip progress prints."""


MAX_UPDATE_FREQUENCY = 5_000
"""The max number of records to read before updating the progress bar."""


def _to_time_str(timestamp: float) -> str:
    """Convert a timestamp float to a local time string.

    For now, we'll just use UTC to avoid breaking tests. In the future, we should
    return a local time string.
    """
    datetime_obj = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    datetime_obj = datetime_obj.astimezone()
    return datetime_obj.strftime("%H:%M:%S")


def _get_elapsed_time_str(seconds: float) -> str:
    """Return duration as a string.

    Seconds are included until 10 minutes is exceeded.
    Minutes are always included after 1 minute elapsed.
    Hours are always included after 1 hour elapsed.
    """
    if seconds <= 2:  # noqa: PLR2004  # Magic numbers OK here.
        # Less than 1 minute elapsed
        return f"{seconds:.2f} seconds"

    if seconds < 10:  # noqa: PLR2004  # Magic numbers OK here.
        # Less than 10 seconds elapsed
        return f"{seconds:.1f} seconds"

    if seconds <= 60:  # noqa: PLR2004  # Magic numbers OK here.
        # Less than 1 minute elapsed
        return f"{seconds:.0f} seconds"

    if seconds < 60 * 10:
        # Less than 10 minutes elapsed
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:.0f}min {seconds:.0f}s"

    if seconds < 60 * 60:
        # Less than 1 hour elapsed
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes}min"

    # Greater than 1 hour elapsed
    hours = seconds // (60 * 60)
    minutes = (seconds % (60 * 60)) // 60
    return f"{hours}hr {minutes}min"


class ProgressTracker:  # noqa: PLR0904  # Too many public methods
    """A simple progress bar for the command line and IPython notebooks."""

    def __init__(
        self,
        style: ProgressStyle = ProgressStyle.AUTO,
        *,
        source: Source | None,
        cache: CacheBase | None,
        destination: Destination | None,
        expected_streams: list[str] | None = None,
    ) -> None:
        """Initialize the progress tracker."""
        # Components
        self._source = source
        self._cache = cache
        self._destination = destination

        self._file_logger: logging.Logger | None = get_global_file_logger()

        # Streams expected (for progress bar)
        self.num_streams_expected = len(expected_streams) if expected_streams else 0

        # Overall job status
        self.start_time = time.time()
        self.end_time: float | None = None

        # Reads
        self.read_start_time = time.time()
        self.read_end_time: float | None = None
        self.first_record_received_time: float | None = None
        self.first_destination_record_sent_time: float | None = None
        self.total_records_read = 0

        # Stream reads
        self.stream_read_counts: dict[str, int] = defaultdict(int)
        self.stream_read_start_times: dict[str, float] = {}
        self.stream_read_end_times: dict[str, float] = {}
        self.stream_bytes_read: dict[str, int] = defaultdict(int)

        # Cache Writes
        self.total_records_written = 0
        self.total_batches_written = 0
        self.written_stream_names: set[str] = set()

        # Cache Finalization
        self.finalize_start_time: float | None = None
        self.finalize_end_time: float | None = None
        self.total_records_finalized = 0
        self.total_batches_finalized = 0
        self.finalized_stream_names: list[str] = []

        # Destination stream writes
        self.destination_stream_records_delivered: dict[str, int] = defaultdict(int)
        self.destination_stream_records_confirmed: dict[str, int] = defaultdict(int)

        # Progress bar properties
        self._last_update_time: float | None = None
        self._rich_view: RichLive | None = None

        self.reset_progress_style(style)

    def _print_info_message(
        self,
        message: str,
    ) -> None:
        """Print a message to the console and the file logger."""
        if self._file_logger:
            self._file_logger.info(message)

    @property
    def bytes_tracking_enabled(self) -> bool:
        """Return True if bytes are being tracked."""
        return bool(self.stream_bytes_read)

    @property
    def total_bytes_read(self) -> int:
        """Return the total number of bytes read.

        Return None if bytes are not being tracked.
        """
        return sum(self.stream_bytes_read.values())

    @property
    def total_megabytes_read(self) -> float:
        """Return the total number of bytes read.

        Return None if no bytes have been read, as this is generally due to bytes not being tracked.
        """
        return self.total_bytes_read / 1_000_000

    def tally_records_read(
        self,
        messages: Iterable[AirbyteMessage],
        *,
        auto_close_streams: bool = False,
    ) -> Generator[AirbyteMessage, Any, None]:
        """This method simply tallies the number of records processed and yields the messages."""
        # Update the display before we start.
        self._log_sync_start()
        self._start_rich_view()
        self._update_display()

        update_period = 1  # Reset the update period to 1 before start.

        for count, message in enumerate(messages, start=1):
            # Yield the message immediately.
            yield message

            if message.record:
                # If this is the first record, set the start time.
                if self.first_record_received_time is None:
                    self.first_record_received_time = time.time()

                # Tally the record.
                self.total_records_read += 1

                if message.record.stream:
                    self.stream_read_counts[message.record.stream] += 1

                    if message.record.stream not in self.stream_read_start_times:
                        self.log_stream_start(stream_name=message.record.stream)

            elif message.trace and message.trace.stream_status:
                if message.trace.stream_status.status is AirbyteStreamStatus.STARTED:
                    self.log_stream_start(
                        stream_name=message.trace.stream_status.stream_descriptor.name
                    )
                if message.trace.stream_status.status is AirbyteStreamStatus.COMPLETE:
                    self._log_stream_read_end(
                        stream_name=message.trace.stream_status.stream_descriptor.name
                    )

            # Bail if we're not due for a progress update.
            if count % update_period != 0:
                continue

            # Update the update period to the latest scale of data.
            update_period = self._get_update_period(count)

            # Update the display.
            self._update_display()

        if auto_close_streams:
            for stream_name in self._unclosed_stream_names:
                yield _new_stream_success_message(stream_name)
                self._log_stream_read_end(stream_name)

    def tally_pending_writes(
        self,
        messages: IO[str] | AirbyteMessageIterator,
    ) -> Generator[AirbyteMessage, None, None]:
        """This method simply tallies the number of records processed and yields the messages."""
        # Update the display before we start.
        self._update_display()
        self._start_rich_view()

        update_period = 1  # Reset the update period to 1 before start.

        for count, message in enumerate(messages, start=1):
            yield message  # Yield the message immediately.
            if isinstance(message, str):
                # This is a string message, not an AirbyteMessage.
                # For now at least, we don't need to pay the cost of parsing it.
                continue

            if message.record and message.record.stream:
                self.destination_stream_records_delivered[message.record.stream] += 1

            if count % update_period != 0:
                continue

            # If this is the first record, set the start time.
            if self.first_destination_record_sent_time is None:
                self.first_destination_record_sent_time = time.time()

            # Update the update period to the latest scale of data.
            update_period = self._get_update_period(count)

            # Update the display.
            self._update_display()

    def tally_confirmed_writes(
        self,
        messages: Iterable[AirbyteMessage],
    ) -> Generator[AirbyteMessage, Any, None]:
        """This method watches for state messages and tally records that are confirmed written.

        The original messages are passed through unchanged.
        """
        self._start_rich_view()  # Start Rich's live view if not already running.
        for message in messages:
            if message.state:
                # This is a state message from the destination. Tally the records written.
                if message.state.stream and message.state.destinationStats:
                    stream_name = message.state.stream.stream_descriptor.name
                    self.destination_stream_records_confirmed[stream_name] += int(
                        message.state.destinationStats.recordCount or 0
                    )
                self._update_display()

            yield message

        self._update_display(force_refresh=True)

    def tally_bytes_read(self, bytes_read: int, stream_name: str) -> None:
        """Tally the number of bytes read.

        Unlike the other tally methods, this method does not yield messages.
        """
        self.stream_bytes_read[stream_name] += bytes_read

    # Logging methods

    @property
    def job_description(self) -> str:
        """Return a description of the job, combining source, destination, and cache inputs."""
        steps: list[str] = []
        if self._source is not None:
            steps.append(self._source.name)

        if self._cache is not None:
            steps.append(self._cache.__class__.__name__)

        if self._destination is not None:
            steps.append(self._destination.name)

        return " -> ".join(steps)

    def _send_telemetry(
        self,
        state: EventState,
        number_of_records: int | None = None,
        event_type: EventType = EventType.SYNC,
        exception: Exception | None = None,
    ) -> None:
        """Send telemetry for the current job state.

        A thin wrapper around `send_telemetry` that includes the job description.
        """
        send_telemetry(
            source=self._source._get_connector_runtime_info() if self._source else None,  # noqa: SLF001
            cache=self._cache._get_writer_runtime_info() if self._cache else None,  # noqa: SLF001
            destination=(
                self._destination._get_connector_runtime_info()  # noqa: SLF001
                if self._destination
                else None
            ),
            state=state,
            number_of_records=number_of_records,
            event_type=event_type,
            exception=exception,
        )

    def _log_sync_start(self) -> None:
        """Log the start of a sync operation."""
        self._print_info_message(
            f"Started `{self.job_description}` sync at `{pendulum.now().format('HH:mm:ss')}`..."
        )
        # We access a non-public API here (noqa: SLF001) to get the runtime info for participants.
        self._send_telemetry(
            state=EventState.STARTED,
            event_type=EventType.SYNC,
        )

    def log_stream_start(self, stream_name: str) -> None:
        """Log that a stream has started reading."""
        if stream_name not in self.stream_read_start_times:
            self._print_info_message(
                f"Read started on stream `{stream_name}` at "
                f"`{pendulum.now().format('HH:mm:ss')}`..."
            )
            self.stream_read_start_times[stream_name] = time.time()

    def _log_stream_read_end(self, stream_name: str) -> None:
        self._print_info_message(
            f"Read completed on stream `{stream_name}` at `{pendulum.now().format('HH:mm:ss')}`..."
        )
        self.stream_read_end_times[stream_name] = time.time()

    @property
    def _job_info(self) -> dict[str, Any]:
        """Return a dictionary of job information."""
        job_info: dict[str, str | dict] = {
            "description": self.job_description,
        }
        if self._source:
            job_info["source"] = self._source._get_connector_runtime_info().to_dict()  # noqa: SLF001

        if self._cache:
            job_info["cache"] = self._cache._get_writer_runtime_info().to_dict()  # noqa: SLF001

        if self._destination:
            job_info["destination"] = self._destination._get_connector_runtime_info().to_dict()  # noqa: SLF001

        return job_info

    def _log_read_metrics(self) -> None:
        """Log read performance metrics."""
        # Source performance metrics
        if not self.total_records_read or not self._file_logger:
            return

        log_dict = {
            "job_type": "read",
            "job_info": self._job_info,
        }

        perf_metrics: dict[str, Any] = {}
        perf_metrics["records_read"] = self.total_records_read
        perf_metrics["read_time_seconds"] = self.elapsed_read_seconds
        perf_metrics["read_start_time"] = self.read_start_time
        perf_metrics["read_end_time"] = self.read_end_time
        if self.elapsed_read_seconds > 0:
            perf_metrics["records_per_second"] = round(
                self.total_records_read / self.elapsed_read_seconds, 4
            )
            if self.bytes_tracking_enabled:
                mb_read = self.total_megabytes_read
                perf_metrics["mb_read"] = mb_read
                perf_metrics["mb_per_second"] = round(mb_read / self.elapsed_read_seconds, 4)

        stream_metrics = {}
        for stream_name, count in self.stream_read_counts.items():
            stream_metrics[stream_name] = {
                "records_read": count,
                "read_start_time": self.stream_read_start_times.get(stream_name),
                "read_end_time": self.stream_read_end_times.get(stream_name),
            }
            if (
                stream_name in self.stream_read_end_times
                and stream_name in self.stream_read_start_times
                and count > 0
            ):
                duration: float = (
                    self.stream_read_end_times[stream_name]
                    - self.stream_read_start_times[stream_name]
                )
                stream_metrics[stream_name]["read_time_seconds"] = duration
                if duration > 0:
                    stream_metrics[stream_name]["records_per_second"] = round(
                        count
                        / (
                            self.stream_read_end_times[stream_name]
                            - self.stream_read_start_times[stream_name]
                        ),
                        4,
                    )
                    if self.bytes_tracking_enabled:
                        mb_read = self.stream_bytes_read[stream_name] / 1_000_000
                        stream_metrics[stream_name]["mb_read"] = mb_read
                        stream_metrics[stream_name]["mb_per_second"] = round(mb_read / duration, 4)

        perf_metrics["stream_metrics"] = stream_metrics
        log_dict["performance_metrics"] = perf_metrics

        self._file_logger.info(json.dumps(log_dict))

        perf_logger: BoundLogger = logs.get_global_stats_logger()
        perf_logger.info(**log_dict)

    @property
    def _unclosed_stream_names(self) -> list[str]:
        """Return a list of streams that have not yet been fully read."""
        return [
            stream_name
            for stream_name in self.stream_read_counts
            if stream_name not in self.stream_read_end_times
        ]

    def log_success(
        self,
    ) -> None:
        """Log the success of a sync operation."""
        if self.end_time is None:
            # If we haven't already finalized, do so now.

            self.end_time = time.time()

        self._update_display(force_refresh=True)
        self._stop_rich_view()
        self._print_info_message(
            f"Completed `{self.job_description}` sync at `{pendulum.now().format('HH:mm:ss')}`."
        )
        self._log_read_metrics()
        self._send_telemetry(
            state=EventState.SUCCEEDED,
            number_of_records=self.total_records_read,
            event_type=EventType.SYNC,
        )

    def log_failure(
        self,
        exception: Exception,
    ) -> None:
        """Log the failure of a sync operation."""
        self._update_display(force_refresh=True)
        self._stop_rich_view()
        self._print_info_message(
            f"Failed `{self.job_description}` sync at `{pendulum.now().format('HH:mm:ss')}`."
        )
        self._send_telemetry(
            state=EventState.FAILED,
            number_of_records=self.total_records_read,
            exception=exception,
            event_type=EventType.SYNC,
        )

    def log_read_complete(self) -> None:
        """Log that reading is complete."""
        self.read_end_time = time.time()
        self._update_display(force_refresh=True)

    def reset_progress_style(
        self,
        style: ProgressStyle = ProgressStyle.AUTO,
    ) -> None:
        """Set the progress bar style.

        You can call this method at any time to change the progress bar style as needed.

        Usage:

        ```python
        from airbyte.progress import progress, ProgressStyle

        progress.reset_progress_style(ProgressStyle.PLAIN)
        ```
        """
        self._stop_rich_view()  # Stop Rich's live view if running.
        self.style: ProgressStyle = style
        if self.style == ProgressStyle.AUTO:
            self.style = ProgressStyle.PLAIN
            if IS_NOTEBOOK:
                self.style = ProgressStyle.IPYTHON

            elif IS_REPL or "NO_LIVE_PROGRESS" in os.environ:
                self.style = ProgressStyle.PLAIN

            elif meta.is_ci():
                # Some CI environments support Rich, but Dagger does not.
                self.style = ProgressStyle.PLAIN

            else:
                # Test for Rich availability:
                self._rich_view = RichLive()
                try:
                    self._rich_view.start()
                    self._rich_view.stop()
                    self._rich_view = None
                except LiveError:
                    # Rich live view not available. Using plain text progress.
                    self._rich_view = None
                    self.style = ProgressStyle.PLAIN
                else:
                    # No exceptions raised, so we can use Rich.
                    self.style = ProgressStyle.RICH

    def _start_rich_view(self) -> None:
        """Start the rich view display, if applicable per `self.style`.

        Otherwise, this is a no-op.
        """
        if self.style == ProgressStyle.RICH and not self._rich_view:
            try:
                self._rich_view = RichLive(
                    auto_refresh=True,
                    refresh_per_second=DEFAULT_REFRESHES_PER_SECOND,
                )
                self._rich_view.start()
            except Exception:
                logs.warn_once(
                    "Failed to start Rich live view. Falling back to plain text progress.",
                    with_stack=False,
                )
                self.style = ProgressStyle.PLAIN
                self._stop_rich_view()

    def _stop_rich_view(self) -> None:
        """Stop the rich view display, if applicable.

        Otherwise, this is a no-op.
        """
        if self._rich_view:
            with suppress(Exception):
                self._rich_view.stop()
                self._rich_view = None

    def __del__(self) -> None:
        """Close the Rich view."""
        self._stop_rich_view()

    @property
    def elapsed_seconds(self) -> float:
        """Return the number of seconds elapsed since the operation started."""
        if self.end_time:
            return self.end_time - self.read_start_time

        return time.time() - self.read_start_time

    @property
    def elapsed_read_seconds(self) -> float:
        """Return the number of seconds elapsed since the read operation started."""
        if self.read_end_time:
            return self.read_end_time - (self.first_record_received_time or self.read_start_time)

        return time.time() - (self.first_record_received_time or self.read_start_time)

    @property
    def elapsed_time_string(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_seconds)

    @property
    def elapsed_seconds_since_last_update(self) -> float | None:
        """Return the number of seconds elapsed since the last update."""
        if self._last_update_time is None:
            return None

        return time.time() - self._last_update_time

    @property
    def elapsed_read_time_string(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_read_seconds)

    @property
    def elapsed_finalization_seconds(self) -> float:
        """Return the number of seconds elapsed since the read operation started."""
        if self.finalize_start_time is None:
            return 0
        if self.finalize_end_time is None:
            return time.time() - self.finalize_start_time
        return self.finalize_end_time - self.finalize_start_time

    @property
    def elapsed_finalization_time_str(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_finalization_seconds)

    @staticmethod
    def _get_update_period(
        current_count: int,
    ) -> int:
        """Return the number of records to read before updating the progress bar.

        This is some math to make updates adaptive to the scale of records read.
        We want to update the display more often when the count is low, and less
        often when the count is high.
        """
        return min(MAX_UPDATE_FREQUENCY, 10 ** math.floor(math.log10(max(current_count, 1)) / 4))

    def log_batch_written(self, stream_name: str, batch_size: int) -> None:
        """Log that a batch has been written.

        Args:
            stream_name: The name of the stream.
            batch_size: The number of records in the batch.
        """
        self.total_records_written += batch_size
        self.total_batches_written += 1
        self.written_stream_names.add(stream_name)
        self._update_display()

    def log_batches_finalizing(self, stream_name: str, num_batches: int) -> None:
        """Log that batch are ready to be finalized.

        In our current implementation, we ignore the stream name and number of batches.
        We just use this as a signal that we're finished reading and have begun to
        finalize any accumulated batches.
        """
        _ = stream_name, num_batches  # unused for now
        if self.finalize_start_time is None:
            self.read_end_time = time.time()
            self.finalize_start_time = self.read_end_time

        self._update_display(force_refresh=True)

    def log_batches_finalized(self, stream_name: str, num_batches: int) -> None:
        """Log that a batch has been finalized."""
        _ = stream_name  # unused for now
        self.total_batches_finalized += num_batches
        self._update_display(force_refresh=True)

    def log_cache_processing_complete(self) -> None:
        """Log that cache processing is complete."""
        self.finalize_end_time = time.time()
        self._update_display(force_refresh=True)

    def log_stream_finalized(self, stream_name: str) -> None:
        """Log that a stream has been finalized."""
        if stream_name not in self.finalized_stream_names:
            self.finalized_stream_names.append(stream_name)
            self._update_display(force_refresh=True)

    def _update_display(self, *, force_refresh: bool = False) -> None:
        """Update the display."""
        # Don't update more than twice per second unless force_refresh is True.
        if (
            not force_refresh
            and self._last_update_time  # if not set, then we definitely need to update
            and cast(float, self.elapsed_seconds_since_last_update) < 0.8  # noqa: PLR2004
        ):
            return

        status_message = self._get_status_message()

        if self.style == ProgressStyle.IPYTHON and ipy_display is not None:
            # We're in a notebook so use the IPython display.
            assert ipy_display is not None
            ipy_display.clear_output(wait=True)
            ipy_display.display(ipy_display.Markdown(status_message))

        elif self.style == ProgressStyle.RICH and self._rich_view is not None:
            self._rich_view.update(RichMarkdown(status_message))

        elif self.style in {ProgressStyle.PLAIN, ProgressStyle.NONE}:
            pass

        self._last_update_time = time.time()

    def _get_status_message(self) -> str:
        """Compile and return a status message."""
        # Format start time as a friendly string in local timezone:
        start_time_str = _to_time_str(self.read_start_time)
        records_per_second: float = 0.0
        mb_per_second_str = ""
        if self.elapsed_read_seconds > 0:
            records_per_second = self.total_records_read / self.elapsed_read_seconds
            if self.bytes_tracking_enabled:
                mb_per_second = self.total_megabytes_read / self.elapsed_read_seconds
                mb_per_second_str = f", {mb_per_second:,.2f} MB/s"

        status_message = HORIZONTAL_LINE + f"\n### Sync Progress: `{self.job_description}`\n\n"

        def join_streams_strings(streams_list: list[str]) -> str:
            separator: Literal["\n  - ", ", "] = (
                "\n  - " if len(streams_list) <= MAX_ITEMIZED_STREAMS else ", "
            )
            return separator.join(streams_list)

        # Source read progress:
        if self.first_record_received_time:
            status_message += (
                f"**Started reading from source at `{start_time_str}`:**\n\n"
                f"- Read **{self.total_records_read:,}** records "
                f"over **{self.elapsed_read_time_string}** "
                f"({records_per_second:,.1f} records/s{mb_per_second_str}).\n\n"
            )

        if self.stream_read_counts:
            status_message += (
                f"- Received records for {len(self.stream_read_counts)}"
                + (
                    f" out of {self.num_streams_expected} expected"
                    if self.num_streams_expected
                    else ""
                )
                + " streams:\n  - "
                + join_streams_strings(
                    [
                        f"{self.stream_read_counts[stream_name]:,} {stream_name}"
                        for stream_name in self.stream_read_counts
                    ]
                )
                + "\n\n"
            )

        # Source cache writes
        if self.total_records_written > 0:
            status_message += (
                f"- Cached **{self.total_records_written:,}** records "
                f"into {self.total_batches_written:,} local cache file(s).\n\n"
            )

        # Source read completed
        if self.read_end_time is not None:
            read_end_time_str = _to_time_str(self.read_end_time)
            status_message += f"- Finished reading from source at `{read_end_time_str}`.\n\n"

        # Cache processing progress
        if self.finalize_start_time is not None:
            finalize_start_time_str = _to_time_str(self.finalize_start_time)
            status_message += f"**Started cache processing at `{finalize_start_time_str}`:**\n\n"
            status_message += (
                f"- Processed **{self.total_batches_finalized}** "
                f"cache file(s) over **{self.elapsed_finalization_time_str}**.\n\n"
            )

            # Cache processing completion (per stream)
            if self.finalized_stream_names:
                status_message += (
                    f"- Completed cache processing for {len(self.finalized_stream_names)} "
                    + (f"out of {self.num_streams_expected} " if self.num_streams_expected else "")
                    + "streams:\n  - "
                    + join_streams_strings(self.finalized_stream_names)
                    + "\n\n"
                )

            if self.finalize_end_time is not None:
                completion_time_str = _to_time_str(self.finalize_end_time)
                status_message += f"- Finished cache processing at `{completion_time_str}`.\n\n"

        status_message += "\n\n"

        if self.first_destination_record_sent_time:
            status_message += (
                f"**Started writing to destination at "
                f"`{_to_time_str(self.first_destination_record_sent_time)}`:**\n\n"
            )
            if self.destination_stream_records_delivered:
                status_message += (
                    f"- Sent **{self.total_destination_records_delivered:,} records** "
                    f"to destination over **{self.total_destination_write_time_str}** "
                    f"({self.destination_records_delivered_per_second:,.1f} records/s)."
                    "\n\n"
                )
                status_message += (
                    "- Stream records delivered:\n  - "
                    + join_streams_strings(
                        [
                            f"{count:,} {stream}"
                            for stream, count in self.destination_stream_records_delivered.items()
                        ]
                    )
                    + "\n\n"
                )

        status_message += "\n"

        if self.end_time is not None:
            status_message += (
                f"\n\n**Sync completed at `{_to_time_str(self.end_time)}`. "
                f"Total time elapsed: {self.total_time_elapsed_str}**\n\n"
            )

        status_message += HORIZONTAL_LINE

        return status_message

    @property
    def total_time_elapsed_seconds(self) -> float:
        """Return the total time elapsed in seconds."""
        if self.end_time is None:
            return time.time() - self.start_time

        return self.end_time - self.start_time

    @property
    def total_destination_write_time_seconds(self) -> float:
        """Return the total time elapsed in seconds."""
        if self.first_destination_record_sent_time is None:
            return 0

        if self.end_time is None:
            return time.time() - self.first_destination_record_sent_time

        return self.end_time - self.first_destination_record_sent_time

    @property
    def destination_records_delivered_per_second(self) -> float:
        """Return the number of records delivered per second."""
        if self.total_destination_write_time_seconds > 0:
            return (
                self.total_destination_records_delivered / self.total_destination_write_time_seconds
            )

        return 0

    @property
    def total_destination_write_time_str(self) -> str:
        """Return the total time elapsed as a string."""
        return _get_elapsed_time_str(self.total_destination_write_time_seconds)

    @property
    def total_time_elapsed_str(self) -> str:
        """Return the total time elapsed as a string."""
        return _get_elapsed_time_str(self.total_time_elapsed_seconds)

    @property
    def total_destination_records_delivered(self) -> int:
        """Return the total number of records delivered to the destination."""
        if not self.destination_stream_records_delivered:
            return 0

        return sum(self.destination_stream_records_delivered.values())

    @property
    def total_destination_records_confirmed(self) -> int:
        """Return the total number of records confirmed by the destination."""
        if not self.destination_stream_records_confirmed:
            return 0

        return sum(self.destination_stream_records_confirmed.values())
