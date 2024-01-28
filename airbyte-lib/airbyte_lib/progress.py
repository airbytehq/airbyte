"""A simple progress bar for the command line and IPython notebooks."""
from __future__ import annotations

import math
import time
from typing import cast


try:
    from tqdm.notebook import tqdm
except ImportError:
    tqdm = None

try:
    from IPython import display as ipy_display
except ImportError:
    ipy_display = None


MAX_UPDATE_FREQUENCY = 1000
"""The max number of records to read before updating the progress bar."""

class ReadProgress:
    """A simple progress bar for the command line and IPython notebooks."""

    def __init__(self) -> None:
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

    @property
    def elapsed_seconds(self) -> int:
        """Return the number of seconds elapsed since the read operation started."""
        return int(time.time() - self.read_start_time)

    @property
    def elapsed_time_string(self) -> str:
        """Return duration as a string."""
        return get_elapsed_time_str(self.elapsed_seconds())

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
        return get_elapsed_time_str(self.elapsed_seconds())

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
        return get_elapsed_time_str(self.elapsed_seconds())

    def log_records_read(self, new_total_count: int) -> None:
        """Load a number of records read."""
        self.total_records_read = new_total_count

        # This is some math to make updates adaptive to the scale of records read.
        # We want to update the display more often when the count is low, and less
        # often when the count is high.
        updated_period = min(
            MAX_UPDATE_FREQUENCY,
            10 ** math.floor(math.log10(self.total_records_read) / 8)
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

    def log_batch_finalizing(self, stream_name: str) -> None:
        """Log that a batch has been finalized."""
        _ = stream_name
        if self.finalize_start_time is None:
            self.finalize_start_time = time.time()

        self.update_display()

    def log_batch_finalized(self, stream_name: str) -> None:
        """Log that a batch has been finalized."""
        _ = stream_name
        self.total_batches_finalized += 1
        self.update_display()

    def log_stream_finalized(self, stream_name: str) -> None:
        """Log that a stream has been finalized."""
        self.finalized_stream_names.add(stream_name)
        self.update_display()

    def update_display(self) -> None:
        """Update the display."""
        if not ipy_display:
            return

        if self.last_update_time and cast(float, self.elapsed_seconds_since_last_update()) < 0.5:  # noqa: PLR2004
            # Don't update more than twice per second.
            return

        status_message = (
            f"Read **{self.total_records_read}** records "
            f"over **{self.elapsed_read_time_string}**.\n"
        )
        if self.total_records_written > 0:
            status_message += (
                f"Wrote **{self.total_records_written}** records "
                f"in {self.total_batches_written} batches.\n"
            )
        if self.finalize_start_time is not None:
            status_message += (
                f"Finalized **{self.total_records_finalized}** records "
                f"over {self.elapsed_finalization_time_str}.\n"
            )
        status_message += "\n------------------------------------------------\n"

        ipy_display.clear_output(wait=True)
        ipy_display.display(ipy_display.Markdown(status_message))

        self.last_update_time = time.time()

progress = ReadProgress()

def get_elapsed_time_str(seconds: int) -> str:
    """Return duration as a string.

    Seconds are included until 10 minutes is exceeded.
    Minutes are always included after 1 minute elapsed.
    Hours are always included after 1 hour elapsed.
    """
    if seconds <= 60:  # noqa: PLR2004  # Magic numbers OK here.
        return f"{seconds} seconds elapsed"

    if seconds < 60 * 10:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}min {seconds}s elapsed"

    if seconds < 60 * 60:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}min elapsed"

    hours = seconds // (60 * 60)
    minutes = (seconds % (60 * 60)) // 60
    return f"{hours}hr {minutes}min elapsed"
