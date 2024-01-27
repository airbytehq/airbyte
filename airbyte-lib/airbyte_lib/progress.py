"""A simple progress bar for the command line and IPython notebooks."""
from __future__ import annotations

import math


try:
    from tqdm.notebook import tqdm
except ImportError:
    tqdm = None

try:
    from IPython import display as ipy_display
except ImportError:
    ipy_display = None


def log_records_read(total_count: int) -> None:
    """Log the number of records read.

    Args:
        total_count: The total number of records read.
    """
    if not ipy_display:
        return

    period = 10 ** math.floor(math.log10(total_count))
    if total_count % period != 0:
        return

    ipy_display.clear_output(wait=True)
    ipy_display.display(ipy_display.Markdown(f"Read {total_count} records."), raw=True)


def log_batch_written(stream_name: str, batch_size: int) -> None:
    """Log that a batch has been written.

    Args:
        stream_name: The name of the stream.
        batch_size: The number of records in the batch.
    """
    if not ipy_display:
        return

    ipy_display.clear_output(wait=True)
    ipy_display.display(
        ipy_display.Markdown(f"Wrote batch for stream '{stream_name}' with {batch_size} records."),
        raw=True,
    )


def log_batch_finalizing(stream_name: str) -> None:
    """Log that a batch is being finalized."""
    if not ipy_display:
        return

    ipy_display.clear_output(wait=True)
    ipy_display.display(
        ipy_display.Markdown(f"Finalizing batches for stream '{stream_name}'..."),
        raw=True,
    )


def log_batch_finalized(stream_name: str) -> None:
    """Log that a batch has been finalized."""
    if not ipy_display:
        return

    ipy_display.clear_output(wait=True)
    ipy_display.display(
        ipy_display.Markdown(f"Finalized batch for stream '{stream_name}'."),
        raw=True,
    )
