# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A simple progress bar for the command line and IPython notebooks."""
from __future__ import annotations

import datetime
import math
import sys
import time
from contextlib import suppress
from enum import Enum, auto
from typing import cast

from rich.errors import LiveError
from rich.live import Live as RichLive
from rich.markdown import Markdown as RichMarkdown


DEFAULT_REFRESHES_PER_SECOND = 2
IS_REPL = hasattr(sys, "ps1")  # True if we're in a Python REPL, in which case we can use Rich.

try:
    IS_NOTEBOOK = True
    from IPython import display as ipy_display

except ImportError:
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


MAX_UPDATE_FREQUENCY = 1000
"""The max number of records to read before updating the progress bar."""


def _to_time_str(timestamp: float) -> str:
    """Convert a timestamp float to a local time string.

    For now, we'll just use UTC to avoid breaking tests. In the future, we should
    return a local time string.
    """
    datetime_obj = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    # TODO: Uncomment this line when we can get tests to properly account for local timezones.
    #       For now, we'll just use UTC to avoid breaking tests.
    # datetime_obj = datetime_obj.astimezone()
    return datetime_obj.strftime("%H:%M:%S")


def _get_elapsed_time_str(seconds: int) -> str:
    """Return duration as a string.

    Seconds are included until 10 minutes is exceeded.
    Minutes are always included after 1 minute elapsed.
    Hours are always included after 1 hour elapsed.
    """
    if seconds <= 60:  # noqa: PLR2004  # Magic numbers OK here.
        return f"{seconds} seconds"

    if seconds < 60 * 10:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}min {seconds}s"

    if seconds < 60 * 60:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}min"

    hours = seconds // (60 * 60)
    minutes = (seconds % (60 * 60)) // 60
    return f"{hours}hr {minutes}min"


class ReadProgress:
    """A simple progress bar for the command line and IPython notebooks."""

    def __init__(
        self,
        style: ProgressStyle = ProgressStyle.AUTO,
    ) -> None:
        """Initialize the progress tracker."""
        # Streams expected (for progress bar)
        self.num_streams_expected = 0

        # Reads
        self.read_start_time = time.time()
        self.read_end_time: float | None = None
        self.total_records_read = 0

        # Writes
        self.total_records_written = 0
        self.total_batches_written = 0
        self.written_stream_names: set[str] = set()

        # Finalization
        self.finalize_start_time: float | None = None
        self.finalize_end_time: float | None = None
        self.total_records_finalized = 0
        self.total_batches_finalized = 0
        self.finalized_stream_names: set[str] = set()

        self.last_update_time: float | None = None

        self._rich_view: RichLive | None = None
        self.style: ProgressStyle = style
        if self.style == ProgressStyle.AUTO:
            self.style = ProgressStyle.PLAIN
            if IS_NOTEBOOK:
                self.style = ProgressStyle.IPYTHON

            elif IS_REPL:
                self.style = ProgressStyle.PLAIN

            else:
                # Test for Rich availability:
                self._rich_view = RichLive()
                try:
                    self._rich_view.start()
                    self._rich_view.stop()
                    self._rich_view = None
                    self.style = ProgressStyle.RICH
                except LiveError:
                    # Rich live view not available. Using plain text progress.
                    self._rich_view = None
                    self.style = ProgressStyle.PLAIN

    def _start(self) -> None:
        """Start the progress bar."""
        if self.style == ProgressStyle.RICH and not self._rich_view:
            self._rich_view = RichLive(
                auto_refresh=True,
                refresh_per_second=DEFAULT_REFRESHES_PER_SECOND,
            )
            self._rich_view.start()

    def _stop(self) -> None:
        """Stop the progress bar."""
        if self._rich_view:
            with suppress(Exception):
                self._rich_view.stop()
                self._rich_view = None

    def __del__(self) -> None:
        """Close the Rich view."""
        self._stop()

    def log_success(self) -> None:
        """Log success and stop tracking progress."""
        if self.finalize_end_time is None:
            # If we haven't already finalized, do so now.

            self.finalize_end_time = time.time()

            self.update_display(force_refresh=True)
            self._stop()

    def reset(self, num_streams_expected: int) -> None:
        """Reset the progress tracker."""
        # Streams expected (for progress bar)
        self.num_streams_expected = num_streams_expected

        # Reads
        self.read_start_time = time.time()
        self.read_end_time = None
        self.total_records_read = 0

        # Writes
        self.total_records_written = 0
        self.total_batches_written = 0
        self.written_stream_names = set()

        # Finalization
        self.finalize_start_time = None
        self.finalize_end_time = None
        self.total_records_finalized = 0
        self.total_batches_finalized = 0
        self.finalized_stream_names = set()

        self._start()

    @property
    def elapsed_seconds(self) -> int:
        """Return the number of seconds elapsed since the read operation started."""
        if self.finalize_end_time:
            return int(self.finalize_end_time - self.read_start_time)

        return int(time.time() - self.read_start_time)

    @property
    def elapsed_time_string(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_seconds)

    @property
    def elapsed_seconds_since_last_update(self) -> float | None:
        """Return the number of seconds elapsed since the last update."""
        if self.last_update_time is None:
            return None

        return time.time() - self.last_update_time

    @property
    def elapsed_read_seconds(self) -> int:
        """Return the number of seconds elapsed since the read operation started."""
        if self.read_end_time is None:
            return int(time.time() - self.read_start_time)

        return int(self.read_end_time - self.read_start_time)

    @property
    def elapsed_read_time_string(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_read_seconds)

    @property
    def elapsed_finalization_seconds(self) -> int:
        """Return the number of seconds elapsed since the read operation started."""
        if self.finalize_start_time is None:
            return 0
        if self.finalize_end_time is None:
            return int(time.time() - self.finalize_start_time)
        return int(self.finalize_end_time - self.finalize_start_time)

    @property
    def elapsed_finalization_time_str(self) -> str:
        """Return duration as a string."""
        return _get_elapsed_time_str(self.elapsed_finalization_seconds)

    def log_records_read(self, new_total_count: int) -> None:
        """Load a number of records read."""
        self.total_records_read = new_total_count

        # This is some math to make updates adaptive to the scale of records read.
        # We want to update the display more often when the count is low, and less
        # often when the count is high.
        updated_period = min(
            MAX_UPDATE_FREQUENCY, 10 ** math.floor(math.log10(max(self.total_records_read, 1)) / 4)
        )
        if self.total_records_read % updated_period != 0:
            return

        self.update_display()

    def log_batch_written(self, stream_name: str, batch_size: int) -> None:
        """Log that a batch has been written.

        Args:
            stream_name: The name of the stream.
            batch_size: The number of records in the batch.
        """
        self.total_records_written += batch_size
        self.total_batches_written += 1
        self.written_stream_names.add(stream_name)
        self.update_display()

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

        self.update_display(force_refresh=True)

    def log_batches_finalized(self, stream_name: str, num_batches: int) -> None:
        """Log that a batch has been finalized."""
        _ = stream_name  # unused for now
        self.total_batches_finalized += num_batches
        self.update_display(force_refresh=True)

    def log_stream_finalized(self, stream_name: str) -> None:
        """Log that a stream has been finalized."""
        self.finalized_stream_names.add(stream_name)
        self.update_display(force_refresh=True)
        if len(self.finalized_stream_names) == self.num_streams_expected:
            self.log_success()

    def update_display(self, *, force_refresh: bool = False) -> None:
        """Update the display."""
        # Don't update more than twice per second unless force_refresh is True.
        if (
            not force_refresh
            and self.last_update_time  # if not set, then we definitely need to update
            and cast(float, self.elapsed_seconds_since_last_update) < 0.5  # noqa: PLR2004
        ):
            return

        status_message = self._get_status_message()

        if self.style == ProgressStyle.IPYTHON:
            # We're in a notebook so use the IPython display.
            ipy_display.clear_output(wait=True)
            ipy_display.display(ipy_display.Markdown(status_message))

        elif self.style == ProgressStyle.RICH and self._rich_view is not None:
            self._rich_view.update(RichMarkdown(status_message))

        elif self.style == ProgressStyle.PLAIN:
            # TODO: Add a plain text progress print option that isn't too noisy.
            pass

        elif self.style == ProgressStyle.NONE:
            pass

        self.last_update_time = time.time()

    def _get_status_message(self) -> str:
        """Compile and return a status message."""
        # Format start time as a friendly string in local timezone:
        start_time_str = _to_time_str(self.read_start_time)
        records_per_second: float = 0.0
        if self.elapsed_read_seconds > 0:
            records_per_second = round(self.total_records_read / self.elapsed_read_seconds, 1)
        status_message = (
            f"## Read Progress\n\n"
            f"Started reading at {start_time_str}.\n\n"
            f"Read **{self.total_records_read:,}** records "
            f"over **{self.elapsed_read_time_string}** "
            f"({records_per_second:,} records / second).\n\n"
        )
        if self.total_records_written > 0:
            status_message += (
                f"Wrote **{self.total_records_written:,}** records "
                f"over {self.total_batches_written:,} batches.\n\n"
            )
        if self.read_end_time is not None:
            read_end_time_str = _to_time_str(self.read_end_time)
            status_message += f"Finished reading at {read_end_time_str}.\n\n"
        if self.finalize_start_time is not None:
            finalize_start_time_str = _to_time_str(self.finalize_start_time)
            status_message += f"Started finalizing streams at {finalize_start_time_str}.\n\n"
            status_message += (
                f"Finalized **{self.total_batches_finalized}** batches "
                f"over {self.elapsed_finalization_time_str}.\n\n"
            )
        if self.finalized_stream_names:
            status_message += (
                f"Completed {len(self.finalized_stream_names)} "
                + (f"out of {self.num_streams_expected} " if self.num_streams_expected else "")
                + "streams:\n\n"
            )
            for stream_name in self.finalized_stream_names:
                status_message += f"  - {stream_name}\n"

        status_message += "\n\n"

        if self.finalize_end_time is not None:
            completion_time_str = _to_time_str(self.finalize_end_time)
            status_message += (
                f"Completed writing at {completion_time_str}. "
                f"Total time elapsed: {self.elapsed_time_string}\n\n"
            )
        status_message += "\n------------------------------------------------\n"

        return status_message


progress = ReadProgress()
