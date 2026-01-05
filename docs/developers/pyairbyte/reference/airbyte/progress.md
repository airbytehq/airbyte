---
sidebar_label: progress
title: airbyte.progress
---

A simple progress bar for the command line and IPython notebooks.

Note: Some runtimes (e.g. Dagger) may not support Rich Live views, and sometimes because they _also_
use Rich, and Rich only supports one live view at a time. PyAirbyte will try to use smart defaults
based on your execution environment.

If you experience issues, you can force plain text status reporting by setting the environment
variable `NO_LIVE_PROGRESS=1`.

Logging is controlled by the `AIRBYTE_LOGGING_ROOT` and `AIRBYTE_STRUCTURED_LOGGING` environment
variables, as described in `airbyte.logs`. If `AIRBYTE_STRUCTURED_LOGGING` is set, logs will be
written in JSONL format. Otherwise, log files will be written as text.

## annotations

## datetime

## importlib

## json

## math

## os

## sys

## time

## defaultdict

## suppress

## Enum

## auto

## IO

## TYPE\_CHECKING

## Any

## Literal

## cast

## Console

## LiveError

## RichLive

## RichMarkdown

## ab\_datetime\_now

## AirbyteMessage

## AirbyteStreamStatus

## logs

## \_new\_stream\_success\_message

## meta

## EventState

## EventType

## send\_telemetry

## get\_global\_file\_logger

#### IS\_REPL

True if we&#x27;re in a Python REPL, in which case we can use Rich.

#### HORIZONTAL\_LINE

#### DEFAULT\_REFRESHES\_PER\_SECOND

The default number of times per second to refresh the progress view.

#### MAX\_ITEMIZED\_STREAMS

The maximum number of streams to itemize in the progress view.

#### ipy\_display

## ProgressStyle Objects

```python
class ProgressStyle(Enum)
```

An enum of progress bar styles.

#### AUTO

Automatically select the best style for the environment.

#### RICH

A Rich progress bar.

#### IPYTHON

Use IPython display methods.

#### PLAIN

A plain text progress print.

#### NONE

Skip progress prints.

#### MAX\_UPDATE\_FREQUENCY

The max number of records to read before updating the progress bar.

#### TIME\_TO\_FIRST\_RECORD\_THRESHOLD\_SECONDS

Threshold for time_to_first_record above which adjusted metrics are calculated.

#### \_to\_time\_str

```python
def _to_time_str(timestamp: float) -> str
```

Convert a timestamp float to a local time string.

For now, we&#x27;ll just use UTC to avoid breaking tests. In the future, we should
return a local time string.

#### \_get\_elapsed\_time\_str

```python
def _get_elapsed_time_str(seconds: float) -> str
```

Return duration as a string.

Seconds are included until 10 minutes is exceeded.
Minutes are always included after 1 minute elapsed.
Hours are always included after 1 hour elapsed.

## ProgressTracker Objects

```python
class ProgressTracker()
```

A simple progress bar for the command line and IPython notebooks.

#### \_\_init\_\_

```python
def __init__(style: ProgressStyle = ProgressStyle.AUTO,
             *,
             source: Source | None,
             cache: CacheBase | None,
             destination: Destination | None,
             expected_streams: list[str] | None = None) -> None
```

Initialize the progress tracker.

#### \_print\_info\_message

```python
def _print_info_message(message: str) -> None
```

Print a message to the console and the file logger.

#### bytes\_tracking\_enabled

```python
@property
def bytes_tracking_enabled() -> bool
```

Return True if bytes are being tracked.

#### total\_bytes\_read

```python
@property
def total_bytes_read() -> int
```

Return the total number of bytes read.

Return None if bytes are not being tracked.

#### total\_megabytes\_read

```python
@property
def total_megabytes_read() -> float
```

Return the total number of bytes read.

Return None if no bytes have been read, as this is generally due to bytes not being tracked.

#### tally\_records\_read

```python
def tally_records_read(messages: Iterable[AirbyteMessage],
                       *,
                       auto_close_streams: bool = False
                       ) -> Generator[AirbyteMessage, Any, None]
```

This method simply tallies the number of records processed and yields the messages.

#### tally\_pending\_writes

```python
def tally_pending_writes(
    messages: IO[str] | AirbyteMessageIterator
) -> Generator[AirbyteMessage, None, None]
```

This method simply tallies the number of records processed and yields the messages.

#### tally\_confirmed\_writes

```python
def tally_confirmed_writes(
    messages: Iterable[AirbyteMessage]
) -> Generator[AirbyteMessage, Any, None]
```

This method watches for state messages and tally records that are confirmed written.

The original messages are passed through unchanged.

#### tally\_bytes\_read

```python
def tally_bytes_read(bytes_read: int, stream_name: str) -> None
```

Tally the number of bytes read.

Unlike the other tally methods, this method does not yield messages.

#### job\_description

```python
@property
def job_description() -> str
```

Return a description of the job, combining source, destination, and cache inputs.

#### \_send\_telemetry

```python
def _send_telemetry(state: EventState,
                    number_of_records: int | None = None,
                    event_type: EventType = EventType.SYNC,
                    exception: Exception | None = None) -> None
```

Send telemetry for the current job state.

A thin wrapper around `send_telemetry` that includes the job description.

#### \_log\_sync\_start

```python
def _log_sync_start() -> None
```

Log the start of a sync operation.

#### \_log\_sync\_cancel

```python
def _log_sync_cancel() -> None
```

#### \_log\_stream\_read\_start

```python
def _log_stream_read_start(stream_name: str) -> None
```

#### log\_stream\_start

```python
def log_stream_start(stream_name: str) -> None
```

Log that a stream has started reading.

#### \_log\_stream\_read\_end

```python
def _log_stream_read_end(stream_name: str) -> None
```

#### \_job\_info

```python
@property
def _job_info() -> dict[str, Any]
```

Return a dictionary of job information.

#### \_calculate\_adjusted\_metrics

```python
def _calculate_adjusted_metrics(stream_name: str, count: int,
                                time_to_first_record: float,
                                mb_read: float) -> dict[str, float]
```

Calculate adjusted performance metrics when time_to_first_record exceeds threshold.

#### \_log\_read\_metrics

```python
def _log_read_metrics() -> None
```

Log read performance metrics.

#### \_unclosed\_stream\_names

```python
@property
def _unclosed_stream_names() -> list[str]
```

Return a list of streams that have not yet been fully read.

#### log\_success

```python
def log_success() -> None
```

Log the success of a sync operation.

#### log\_failure

```python
def log_failure(exception: Exception) -> None
```

Log the failure of a sync operation.

#### log\_read\_complete

```python
def log_read_complete() -> None
```

Log that reading is complete.

#### reset\_progress\_style

```python
def reset_progress_style(style: ProgressStyle = ProgressStyle.AUTO) -> None
```

Set the progress bar style.

You can call this method at any time to change the progress bar style as needed.

Usage:

```python
from airbyte.progress import progress, ProgressStyle

progress.reset_progress_style(ProgressStyle.PLAIN)
```

#### \_start\_rich\_view

```python
def _start_rich_view() -> None
```

Start the rich view display, if applicable per `self.style`.

Otherwise, this is a no-op.

#### \_stop\_rich\_view

```python
def _stop_rich_view() -> None
```

Stop the rich view display, if applicable.

Otherwise, this is a no-op.

#### \_\_del\_\_

```python
def __del__() -> None
```

Close the Rich view.

#### elapsed\_seconds

```python
@property
def elapsed_seconds() -> float
```

Return the number of seconds elapsed since the operation started.

#### elapsed\_read\_seconds

```python
@property
def elapsed_read_seconds() -> float
```

Return the number of seconds elapsed since the read operation started.

#### elapsed\_time\_string

```python
@property
def elapsed_time_string() -> str
```

Return duration as a string.

#### elapsed\_seconds\_since\_last\_update

```python
@property
def elapsed_seconds_since_last_update() -> float | None
```

Return the number of seconds elapsed since the last update.

#### elapsed\_read\_time\_string

```python
@property
def elapsed_read_time_string() -> str
```

Return duration as a string.

#### elapsed\_finalization\_seconds

```python
@property
def elapsed_finalization_seconds() -> float
```

Return the number of seconds elapsed since the read operation started.

#### elapsed\_finalization\_time\_str

```python
@property
def elapsed_finalization_time_str() -> str
```

Return duration as a string.

#### \_get\_update\_period

```python
@staticmethod
def _get_update_period(current_count: int) -> int
```

Return the number of records to read before updating the progress bar.

This is some math to make updates adaptive to the scale of records read.
We want to update the display more often when the count is low, and less
often when the count is high.

#### log\_batch\_written

```python
def log_batch_written(stream_name: str, batch_size: int) -> None
```

Log that a batch has been written.

**Arguments**:

- `stream_name` - The name of the stream.
- `batch_size` - The number of records in the batch.

#### log\_batches\_finalizing

```python
def log_batches_finalizing(stream_name: str, num_batches: int) -> None
```

Log that batch are ready to be finalized.

In our current implementation, we ignore the stream name and number of batches.
We just use this as a signal that we&#x27;re finished reading and have begun to
finalize any accumulated batches.

#### log\_batches\_finalized

```python
def log_batches_finalized(stream_name: str, num_batches: int) -> None
```

Log that a batch has been finalized.

#### log\_cache\_processing\_complete

```python
def log_cache_processing_complete() -> None
```

Log that cache processing is complete.

#### log\_stream\_finalized

```python
def log_stream_finalized(stream_name: str) -> None
```

Log that a stream has been finalized.

#### \_update\_display

```python
def _update_display(*, force_refresh: bool = False) -> None
```

Update the display.

#### \_get\_status\_message

```python
def _get_status_message() -> str
```

Compile and return a status message.

#### total\_time\_elapsed\_seconds

```python
@property
def total_time_elapsed_seconds() -> float
```

Return the total time elapsed in seconds.

#### total\_destination\_write\_time\_seconds

```python
@property
def total_destination_write_time_seconds() -> float
```

Return the total time elapsed in seconds.

#### destination\_records\_delivered\_per\_second

```python
@property
def destination_records_delivered_per_second() -> float
```

Return the number of records delivered per second.

#### total\_destination\_write\_time\_str

```python
@property
def total_destination_write_time_str() -> str
```

Return the total time elapsed as a string.

#### total\_time\_elapsed\_str

```python
@property
def total_time_elapsed_str() -> str
```

Return the total time elapsed as a string.

#### total\_destination\_records\_delivered

```python
@property
def total_destination_records_delivered() -> int
```

Return the total number of records delivered to the destination.

#### total\_destination\_records\_confirmed

```python
@property
def total_destination_records_confirmed() -> int
```

Return the total number of records confirmed by the destination.

