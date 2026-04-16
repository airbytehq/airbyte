---
id: airbyte-progress
title: airbyte.progress
---

Module airbyte.progress
=======================
A simple progress bar for the command line and IPython notebooks.

Note: Some runtimes (e.g. Dagger) may not support Rich Live views, and sometimes because they _also_
use Rich, and Rich only supports one live view at a time. PyAirbyte will try to use smart defaults
based on your execution environment.

If you experience issues, you can force plain text status reporting by setting the environment
variable `NO_LIVE_PROGRESS=1`.

Logging is controlled by the `AIRBYTE_LOGGING_ROOT` and `AIRBYTE_STRUCTURED_LOGGING` environment
variables, as described in `airbyte.logs`. If `AIRBYTE_STRUCTURED_LOGGING` is set, logs will be
written in JSONL format. Otherwise, log files will be written as text.

Variables
---------

`DEFAULT_REFRESHES_PER_SECOND`
:   The default number of times per second to refresh the progress view.

`MAX_ITEMIZED_STREAMS`
:   The maximum number of streams to itemize in the progress view.

`MAX_UPDATE_FREQUENCY`
:   The max number of records to read before updating the progress bar.

`TIME_TO_FIRST_RECORD_THRESHOLD_SECONDS`
:   Threshold for time_to_first_record above which adjusted metrics are calculated.

Classes
-------

`ProgressStyle(*args, **kwds)`
:   An enum of progress bar styles.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `AUTO`
    :   Automatically select the best style for the environment.

    `IPYTHON`
    :   Use IPython display methods.

    `NONE`
    :   Skip progress prints.

    `PLAIN`
    :   A plain text progress print.

    `RICH`
    :   A Rich progress bar.

`ProgressTracker(style: ProgressStyle = ProgressStyle.AUTO, *, source: Source | None, cache: CacheBase | None, destination: Destination | None, expected_streams: list[str] | None = None)`
:   A simple progress bar for the command line and IPython notebooks.
    
    Initialize the progress tracker.

    ### Instance variables

    `bytes_tracking_enabled: bool`
    :   Return True if bytes are being tracked.

    `destination_records_delivered_per_second: float`
    :   Return the number of records delivered per second.

    `elapsed_finalization_seconds: float`
    :   Return the number of seconds elapsed since the read operation started.

    `elapsed_finalization_time_str: str`
    :   Return duration as a string.

    `elapsed_read_seconds: float`
    :   Return the number of seconds elapsed since the read operation started.

    `elapsed_read_time_string: str`
    :   Return duration as a string.

    `elapsed_seconds: float`
    :   Return the number of seconds elapsed since the operation started.

    `elapsed_seconds_since_last_update: float | None`
    :   Return the number of seconds elapsed since the last update.

    `elapsed_time_string: str`
    :   Return duration as a string.

    `job_description: str`
    :   Return a description of the job, combining source, destination, and cache inputs.

    `total_bytes_read: int`
    :   Return the total number of bytes read.
        
        Return None if bytes are not being tracked.

    `total_destination_records_confirmed: int`
    :   Return the total number of records confirmed by the destination.

    `total_destination_records_delivered: int`
    :   Return the total number of records delivered to the destination.

    `total_destination_write_time_seconds: float`
    :   Return the total time elapsed in seconds.

    `total_destination_write_time_str: str`
    :   Return the total time elapsed as a string.

    `total_megabytes_read: float`
    :   Return the total number of bytes read.
        
        Return None if no bytes have been read, as this is generally due to bytes not being tracked.

    `total_time_elapsed_seconds: float`
    :   Return the total time elapsed in seconds.

    `total_time_elapsed_str: str`
    :   Return the total time elapsed as a string.

    ### Methods

    `log_batch_written(self, stream_name: str, batch_size: int) ‑> None`
    :   Log that a batch has been written.
        
        Args:
            stream_name: The name of the stream.
            batch_size: The number of records in the batch.

    `log_batches_finalized(self, stream_name: str, num_batches: int) ‑> None`
    :   Log that a batch has been finalized.

    `log_batches_finalizing(self, stream_name: str, num_batches: int) ‑> None`
    :   Log that batch are ready to be finalized.
        
        In our current implementation, we ignore the stream name and number of batches.
        We just use this as a signal that we're finished reading and have begun to
        finalize any accumulated batches.

    `log_cache_processing_complete(self) ‑> None`
    :   Log that cache processing is complete.

    `log_failure(self, exception: Exception) ‑> None`
    :   Log the failure of a sync operation.

    `log_read_complete(self) ‑> None`
    :   Log that reading is complete.

    `log_stream_finalized(self, stream_name: str) ‑> None`
    :   Log that a stream has been finalized.

    `log_stream_start(self, stream_name: str) ‑> None`
    :   Log that a stream has started reading.

    `log_success(self) ‑> None`
    :   Log the success of a sync operation.

    `reset_progress_style(self, style: ProgressStyle = ProgressStyle.AUTO) ‑> None`
    :   Set the progress bar style.
        
        You can call this method at any time to change the progress bar style as needed.
        
        Usage:
        
        ```python
        from airbyte.progress import progress, ProgressStyle
        
        progress.reset_progress_style(ProgressStyle.PLAIN)
        ```

    `tally_bytes_read(self, bytes_read: int, stream_name: str) ‑> None`
    :   Tally the number of bytes read.
        
        Unlike the other tally methods, this method does not yield messages.

    `tally_confirmed_writes(self, messages: Iterable[AirbyteMessage]) ‑> Generator[AirbyteMessage, Any, None]`
    :   This method watches for state messages and tally records that are confirmed written.
        
        The original messages are passed through unchanged.

    `tally_pending_writes(self, messages: IO[str] | AirbyteMessageIterator) ‑> Generator[AirbyteMessage, None, None]`
    :   This method simply tallies the number of records processed and yields the messages.

    `tally_records_read(self, messages: Iterable[AirbyteMessage], *, auto_close_streams: bool = False) ‑> Generator[AirbyteMessage, Any, None]`
    :   This method simply tallies the number of records processed and yields the messages.