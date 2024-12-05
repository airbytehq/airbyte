#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from datetime import datetime
from time import sleep, time
from typing import Any, Final, Iterable, List, Mapping, Optional

import pendulum as pdm
import requests
from airbyte_cdk.sources.streams.http import HttpClient
from requests.exceptions import JSONDecodeError
from source_shopify.utils import LOGGER, ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import AirbyteTracedException, ShopifyBulkExceptions
from .query import ShopifyBulkQuery, ShopifyBulkTemplates
from .record import ShopifyBulkRecord
from .retry import bulk_retry_on_exception
from .status import ShopifyBulkJobStatus
from .tools import END_OF_FILE, BulkTools


@dataclass
class ShopifyBulkManager:
    http_client: HttpClient
    base_url: str
    query: ShopifyBulkQuery
    job_termination_threshold: float
    job_size: float
    job_checkpoint_interval: int

    parent_stream_name: Optional[str] = None
    parent_stream_cursor: Optional[str] = None

    # 10Mb chunk size to save the file
    _retrieve_chunk_size: Final[int] = 1024 * 1024 * 10
    _job_max_retries: Final[int] = 6
    _job_backoff_time: int = 5

    # running job logger constrain, every 100-ish message will be printed
    _log_job_msg_frequency: Final[int] = 100
    # running job log counter
    _log_job_msg_count: int = field(init=False, default=0)

    # attempt counter
    _concurrent_attempt: int = field(init=False, default=0)
    # sleep time per creation attempt
    _concurrent_interval: Final[int] = 30
    # max attempts for job creation
    _concurrent_max_retry: Final[int] = 120

    # currents: _job_id, _job_state, _job_created_at, _job_self_canceled
    _job_id: Optional[str] = field(init=False, default=None)
    _job_state: str = field(init=False, default=None)  # this string is based on ShopifyBulkJobStatus
    # completed and saved Bulk Job result filename
    _job_result_filename: Optional[str] = field(init=False, default=None)
    # date-time when the Bulk Job was created on the server
    _job_created_at: Optional[str] = field(init=False, default=None)
    # indicated whether or not we manually force-cancel the current job
    _job_self_canceled: bool = field(init=False, default=False)
    # time between job status checks
    _job_check_interval: Final[int] = 3

    # 0.1 ~= P2H, default value, lower boundary for slice size
    _job_size_min: Final[float] = 0.1

    # last running job object count
    _job_last_rec_count: int = field(init=False, default=0)
    # the flag to adjust the next slice from the checkpointed cursor vaue
    _job_adjust_slice_from_checkpoint: bool = field(init=False, default=False)

    # expand slice factor
    _job_size_expand_factor: int = field(init=False, default=2)
    # reduce slice factor
    _job_size_reduce_factor: int = field(init=False, default=2)
    # whether or not the slicer should revert the previous start value
    _job_should_revert_slice: bool = field(init=False, default=False)

    # 2 sec is set as default value to cover the case with the empty-fast-completed jobs
    _job_last_elapsed_time: float = field(init=False, default=2.0)

    def __post_init__(self) -> None:
        self._job_size = self.job_size
        # The upper boundary for slice size is limited by the value from the config, default value is `P30D`
        self._job_size_max = self.job_size
        # Each job ideally should be executed within the specified time (in sec),
        # to maximize the performance for multi-connection syncs and control the bulk job size within +- 1 hours (3600 sec),
        # Ideally the source will balance on it's own rate, based on the time taken to return the data for the slice.
        # This behaviour could be overidden by providing the `BULK Job termination threshold` option in the `config`.
        self._job_max_elapsed_time = self.job_termination_threshold
        # how many records should be collected before we use the checkpoining
        self._job_checkpoint_interval = self.job_checkpoint_interval
        # define Record Producer instance
        self.record_producer: ShopifyBulkRecord = ShopifyBulkRecord(self.query, self.parent_stream_name, self.parent_stream_cursor)

    @property
    def _tools(self) -> BulkTools:
        return BulkTools()

    @property
    def _job_state_to_fn_map(self) -> Mapping[str, Any]:
        return {
            ShopifyBulkJobStatus.CREATED.value: self._on_created_job,
            ShopifyBulkJobStatus.CANCELING.value: self._on_canceling_job,
            ShopifyBulkJobStatus.CANCELED.value: self._on_canceled_job,
            ShopifyBulkJobStatus.COMPLETED.value: self._on_completed_job,
            ShopifyBulkJobStatus.RUNNING.value: self._on_running_job,
            ShopifyBulkJobStatus.TIMEOUT.value: self._on_timeout_job,
            ShopifyBulkJobStatus.FAILED.value: self._on_failed_job,
            ShopifyBulkJobStatus.ACCESS_DENIED.value: self._on_access_denied_job,
        }

    @property
    def _job_size_adjusted_expand_factor(self, coef: float = 0.5) -> float:
        """
        The Job Size expand factor is calculated using EMA (Expotentional Moving Average):
            coef - the expantion coefficient
            previous_expand_factor - previous factor value

        Formula: expand_factor = coef * previous_expand_factor + (1 - coef)
        """

        return coef * self._job_size_expand_factor + (1 - coef)

    @property
    def _job_size_adjusted_reduce_factor(self) -> float:
        """
        The Job Size reduce factor is 2, by default.
        """

        return self._job_size_reduce_factor

    @property
    def _job_elapsed_time_in_state(self) -> int:
        """
        Returns the elapsed time taken while Job is in certain status/state.
        """
        return (pdm.now() - pdm.parse(self._job_created_at)).in_seconds() if self._job_created_at else 0

    @property
    def _is_long_running_job(self) -> bool:
        if self._job_elapsed_time_in_state:
            if self._job_elapsed_time_in_state > self._job_max_elapsed_time:
                # set the slicer to revert mode
                self._job_should_revert_slice = True
                return True
        # reset slicer to normal mode
        self._job_should_revert_slice = False
        return False

    @property
    def _supports_checkpointing(self) -> bool:
        """
        The flag to determine whether or not the BULK Stream supports the `BULK checkpointing`.
        """
        return self.query.supports_checkpointing

    @property
    def _job_should_checkpoint(self) -> bool:
        return self._supports_checkpointing and self._job_last_rec_count >= self._job_checkpoint_interval

    @property
    def _job_any_lines_collected(self) -> bool:
        return self._job_last_rec_count > 0

    def _expand_job_size(self) -> None:
        self._job_size += self._job_size_adjusted_expand_factor

    def _reduce_job_size(self) -> None:
        self._job_size /= self._job_size_adjusted_reduce_factor

    def _job_size_reduce_next(self) -> None:
        # revert the flag
        self._job_should_revert_slice = False
        self._reduce_job_size()

    def __adjust_job_size(self, job_current_elapsed_time: float) -> None:
        if self._job_should_revert_slice:
            pass
        else:
            if job_current_elapsed_time < 1 or job_current_elapsed_time < self._job_last_elapsed_time:
                self._expand_job_size()
            elif job_current_elapsed_time > self._job_last_elapsed_time < self._job_max_elapsed_time:
                pass
            # set the last job time
            self._job_last_elapsed_time = job_current_elapsed_time
            # check the job size slice interval are acceptable
            self._job_size = max(self._job_size_min, min(self._job_size, self._job_size_max))

    def __reset_state(self) -> None:
        # reset the job state to default
        self._job_state = None
        # reset the filename to default
        self._job_result_filename = None
        # setting self-cancelation to default
        self._job_self_canceled = False
        # set the running job message counter to default
        self._log_job_msg_count = 0
        # set the running job object count to default
        self._job_last_rec_count = 0

    def _set_checkpointing(self) -> None:
        # set the flag to adjust the next slice from the checkpointed cursor value
        self._job_adjust_slice_from_checkpoint = True

    def _reset_checkpointing(self) -> None:
        # reseting the checkpoint flag, if bulk job has completed normally
        self._job_adjust_slice_from_checkpoint = False

    def _job_completed(self) -> bool:
        return self._job_state == ShopifyBulkJobStatus.COMPLETED.value

    def _job_canceled(self) -> bool:
        return self._job_state == ShopifyBulkJobStatus.CANCELED.value

    def _job_failed(self) -> bool:
        return self._job_state == ShopifyBulkJobStatus.FAILED.value

    def _job_cancel(self) -> None:
        _, canceled_response = self.http_client.send_request(
            http_method="POST",
            url=self.base_url,
            data=ShopifyBulkTemplates.cancel(self._job_id),
            headers={"Content-Type": "application/graphql"},
            request_kwargs={},
        )
        # mark the job was self-canceled
        self._job_self_canceled = True
        # check CANCELED Job health
        self._job_healthcheck(canceled_response)
        # sleep to ensure the cancelation
        sleep(self._job_check_interval)

    def _log_job_state_with_count(self) -> None:
        """
        Print the status/state Job info message every N request, to minimize the noise in the logs.
        """
        if self._log_job_msg_count < self._log_job_msg_frequency:
            self._log_job_msg_count += 1
        else:
            message = f"Elapsed time: {self._job_elapsed_time_in_state} sec"
            if self._job_last_rec_count > 0:
                count_message = f". Rows collected: {self._job_last_rec_count}"
                message = message + count_message
            self._log_state(message)
            self._log_job_msg_count = 0

    def _log_state(self, message: Optional[str] = None) -> None:
        pattern = f"Stream: `{self.http_client.name}`, the BULK Job: `{self._job_id}` is {self._job_state}"
        if message:
            LOGGER.info(f"{pattern}. {message}.")
        else:
            LOGGER.info(pattern)

    def _job_get_result(self, response: Optional[requests.Response] = None) -> Optional[str]:
        parsed_response = response.json().get("data", {}).get("node", {}) if response else None
        # get `complete` or `partial` result from collected Bulk Job results
        full_result_url = parsed_response.get("url") if parsed_response else None
        partial_result_url = parsed_response.get("partialDataUrl") if parsed_response else None
        job_result_url = full_result_url if full_result_url else partial_result_url
        if job_result_url:
            # save to local file using chunks to avoid OOM
            filename = self._tools.filename_from_url(job_result_url)
            _, response = self.http_client.send_request(http_method="GET", url=job_result_url, request_kwargs={"stream": True})
            response.raise_for_status()
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=self._retrieve_chunk_size):
                    file.write(chunk)
                # add `<end_of_file>` line to the bottom  of the saved data for easy parsing
                file.write(END_OF_FILE.encode())
            return filename

    def _job_get_checkpointed_result(self, response: Optional[requests.Response]) -> None:
        if self._job_any_lines_collected or self._job_should_checkpoint:
            # set the flag to adjust the next slice from the checkpointed cursor value
            self._set_checkpointing()
            # fetch the collected records from CANCELED Job on checkpointing
            self._job_result_filename = self._job_get_result(response)

    def _job_update_state(self, response: Optional[requests.Response] = None) -> None:
        if response:
            self._job_state = response.json().get("data", {}).get("node", {}).get("status")
            self._job_last_rec_count = int(response.json().get("data", {}).get("node", {}).get("objectCount", 0))

            if self._job_state == ShopifyBulkJobStatus.RUNNING.value:
                self._log_job_state_with_count()
            elif self._job_state in [ShopifyBulkJobStatus.CANCELED.value, ShopifyBulkJobStatus.CANCELING.value]:
                # do not emit `CANCELED / CANCELING` Bulk Job status, while checkpointing
                if not self._job_should_checkpoint:
                    self._log_job_state_with_count()
            else:
                self._log_state()

    def _on_created_job(self, **kwargs) -> None:
        pass

    def _on_canceled_job(self, response: requests.Response) -> Optional[AirbyteTracedException]:
        if not self._job_self_canceled:
            raise ShopifyBulkExceptions.BulkJobCanceled(
                f"The BULK Job: `{self._job_id}` exited with {self._job_state}, details: {response.text}"
            )
        else:
            self._job_get_checkpointed_result(response)

    def _on_canceling_job(self, **kwargs) -> None:
        sleep(self._job_check_interval)

    def _cancel_on_long_running_job(self) -> None:
        LOGGER.info(
            f"Stream: `{self.http_client.name}` the BULK Job: {self._job_id} runs longer than expected ({self._job_max_elapsed_time} sec). Retry with the reduced `Slice Size` after self-cancelation."
        )
        self._job_cancel()

    def _cancel_on_checkpointing(self) -> None:
        LOGGER.info(f"Stream: `{self.http_client.name}`, checkpointing after >= `{self._job_checkpoint_interval}` rows collected.")
        # set the flag to adjust the next slice from the checkpointed cursor value
        self._job_cancel()

    def _on_running_job(self, **kwargs) -> None:
        if self._is_long_running_job:
            self._cancel_on_long_running_job()
        elif self._job_should_checkpoint:
            self._cancel_on_checkpointing()
        else:
            sleep(self._job_check_interval)

    def _on_completed_job(self, response: Optional[requests.Response] = None) -> None:
        self._job_result_filename = self._job_get_result(response)

    def _on_failed_job(self, response: requests.Response) -> AirbyteTracedException:
        if not self._supports_checkpointing:
            raise ShopifyBulkExceptions.BulkJobFailed(
                f"The BULK Job: `{self._job_id}` exited with {self._job_state}, details: {response.text}",
            )
        else:
            # when the Bulk Job fails, usually there is a `partialDataUrl` available,
            # we leverage the checkpointing in this case.
            self._job_get_checkpointed_result(response)

    def _on_timeout_job(self, **kwargs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobTimout(
            f"The BULK Job: `{self._job_id}` exited with {self._job_state}, please reduce the `GraphQL BULK Date Range in Days` in SOURCES > Your Shopify Source > SETTINGS.",
        )

    def _on_access_denied_job(self, **kwagrs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobAccessDenied(
            f"The BULK Job: `{self._job_id}` exited with {self._job_state}, please check your PERMISSION to fetch the data for this stream.",
        )

    def _on_job_with_errors(self, errors: List[Mapping[str, Any]]) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobError(f"Could not validate the status of the BULK Job `{self._job_id}`. Errors: {errors}.")

    def _on_non_handable_job_error(self, errors: List[Mapping[str, Any]]) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobNonHandableError(f"The Stream: `{self.http_client.name}`, Non-handable error occured: {errors}")

    def _get_server_errors(self, response: requests.Response) -> List[Optional[Mapping[str, Any]]]:
        server_errors = response.json().get("errors", [])
        return [server_errors] if isinstance(server_errors, str) else server_errors

    def _get_user_errors(self, response: requests.Response) -> List[Optional[Mapping[str, Any]]]:
        user_errors = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        return [user_errors] if isinstance(user_errors, str) else user_errors

    def _collect_bulk_errors(self, response: requests.Response) -> List[Optional[Mapping[str, Any]]]:
        try:
            return self._get_server_errors(response) + self._get_user_errors(response)
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, status: {response.status_code}, response: `{response.text}`. Trace: {repr(e)}."
            )

    def _job_healthcheck(self, response: requests.Response) -> Optional[Exception]:
        errors = self._collect_bulk_errors(response)

        if self._job_state and errors:
            self._on_job_with_errors(errors)

    def _job_track_running(self) -> None:
        _, response = self.http_client.send_request(
            http_method="POST",
            url=self.base_url,
            data=ShopifyBulkTemplates.status(self._job_id),
            headers={"Content-Type": "application/graphql"},
            request_kwargs={},
        )
        self._job_healthcheck(response)
        self._job_update_state(response)
        self._job_state_to_fn_map.get(self._job_state)(response=response)

    def _has_running_concurrent_job(self, errors: Optional[Iterable[Mapping[str, Any]]] = None) -> bool:
        """
        When concurrent BULK Job is already running for the same SHOP we receive:
        Error example:
        [
            {
                'field': None,
                'message': 'A bulk query operation for this app and shop is already in progress: gid://shopify/BulkOperation/4039184154813.',
            }
        ]
        """

        concurrent_job_pattern = "A bulk query operation for this app and shop is already in progress"
        # the errors are handled in `job_job_check_for_errors`
        if errors:
            for error in errors:
                message = error.get("message", "") if isinstance(error, dict) else ""
                if concurrent_job_pattern in message:
                    return True
        return False

    def _has_reached_max_concurrency(self) -> bool:
        return self._concurrent_attempt == self._concurrent_max_retry

    def _should_switch_shop_name(self, response: requests.Response) -> bool:
        """
        Sometimes the API returns the redirected response that points to the same Store but with different Name:
        >> case:
           -- The user inputs the `shop name` as "A":
                while attempting to place the BULK Job
           -- The response contains the redirected results to the `shop name` as "B", like:
           response.url == "https://B.myshopify.com"

        This redirection is related to:
        1) `aliased` or `hidden` store names from being exposed
        2) `migrated` store data to the `new store`, but referenced within the old one stil

        reference issue: https://github.com/airbytehq/oncall/issues/5866
        """
        if self.base_url != response.url:
            self.base_url = response.url
            return True
        return False

    @bulk_retry_on_exception()
    def _job_check_state(self) -> None:
        while not self._job_completed():
            if self._job_canceled():
                break
            elif self._job_failed():
                break
            else:
                self._job_track_running()

    @bulk_retry_on_exception()
    def create_job(self, stream_slice: Mapping[str, str], filter_field: str) -> None:
        if stream_slice:
            query = self.query.get(filter_field, stream_slice["start"], stream_slice["end"])
        else:
            query = self.query.get()

        _, response = self.http_client.send_request(
            http_method="POST",
            url=self.base_url,
            json={"query": ShopifyBulkTemplates.prepare(query)},
            request_kwargs={},
        )

        errors = self._collect_bulk_errors(response)
        if self._has_running_concurrent_job(errors):
            # when the concurrent job takes place, another job could not be created
            # we typically need to wait and retry, but no longer than 10 min. (see retry in `bulk_retry_on_exception`)
            raise ShopifyBulkExceptions.BulkJobCreationFailedConcurrentError(f"Failed to create job for stream {self.http_client.name}")
        elif self._should_switch_shop_name(response):
            # assign new shop name, since the one that specified in `config` was redirected to the different one.
            raise ShopifyBulkExceptions.BulkJobRedirectToOtherShopError(f"Switching the `store` name, redirected to: {response.url}")
        else:
            # There were no concurrent error for this job so even if there were other errors, we can reset this
            self._concurrent_attempt = 0

        if errors:
            self._on_non_handable_job_error(errors)

        self._job_process_created(response)

    def _job_process_created(self, response: requests.Response) -> None:
        """
        The Bulk Job with CREATED status, should be processed, before we move forward with Job Status Checks.
        """
        bulk_response = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {}) if response else None
        if bulk_response and bulk_response.get("status") == ShopifyBulkJobStatus.CREATED.value:
            self._job_id = bulk_response.get("id")
            self._job_created_at = bulk_response.get("createdAt")
            self._job_state = ShopifyBulkJobStatus.CREATED.value
            LOGGER.info(f"Stream: `{self.http_client.name}`, the BULK Job: `{self._job_id}` is {ShopifyBulkJobStatus.CREATED.value}")

    def job_size_normalize(self, start: datetime, end: datetime) -> datetime:
        # adjust slice size when it's bigger than the loop point when it should end,
        # to preserve correct job size adjustments when this is the only job we need to run, based on STATE provided
        requested_slice_size = (end - start).total_days()
        self._job_size = requested_slice_size if requested_slice_size < self._job_size else self._job_size

    def get_adjusted_job_start(self, slice_start: datetime) -> datetime:
        step = self._job_size if self._job_size else self._job_size_min
        return slice_start.add(days=step)

    def _adjust_slice_end(self, slice_end: datetime, checkpointed_cursor: Optional[str] = None) -> datetime:
        """
        Choose between the existing `slice_end` value or `checkpointed_cursor` value, if provided.
        """
        return pdm.parse(checkpointed_cursor) if checkpointed_cursor else slice_end

    def get_adjusted_job_end(self, slice_start: datetime, slice_end: datetime, checkpointed_cursor: Optional[str] = None) -> datetime:
        if self._job_adjust_slice_from_checkpoint:
            # set the checkpointing to default, before the next slice is emitted, to avoid inf.loop
            self._reset_checkpointing()
            return self._adjust_slice_end(slice_end, checkpointed_cursor)

        if self._is_long_running_job:
            self._job_size_reduce_next()
            return slice_start

        return slice_end

    def _emit_final_job_message(self, job_current_elapsed_time: int) -> None:
        final_message = f"Stream: `{self.http_client.name}`, the BULK Job: `{self._job_id}` time elapsed: {job_current_elapsed_time} sec."

        if self._job_any_lines_collected:
            lines_collected_message = f" Rows collected: {self._job_last_rec_count} --> records: `{self.record_producer.record_composed}`."
            final_message = final_message + lines_collected_message

        # emit final Bulk job status message
        LOGGER.info(f"{final_message}")

    def _process_bulk_results(self) -> Iterable[Mapping[str, Any]]:
        if self._job_result_filename:
            # produce records from saved bulk job result
            yield from self.record_producer.read_file(self._job_result_filename)
        else:
            yield from []

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_get_results(self) -> Optional[Iterable[Mapping[str, Any]]]:
        """
        This method checks the status for the `CREATED` Shopify BULK Job, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """

        job_started = time()
        try:
            # track created job until it's COMPLETED
            self._job_check_state()
            yield from self._process_bulk_results()
        except (
            ShopifyBulkExceptions.BulkJobFailed,
            ShopifyBulkExceptions.BulkJobTimout,
            ShopifyBulkExceptions.BulkJobAccessDenied,
            # when the job is canceled by non-source actions,
            # we should raise the system_error
            ShopifyBulkExceptions.BulkJobCanceled,
        ) as bulk_job_error:
            raise bulk_job_error
        finally:
            job_current_elapsed_time = round((time() - job_started), 3)
            # emit the final Bulk Job log message
            self._emit_final_job_message(job_current_elapsed_time)
            # check whether or not we should expand or reduce the size of the slice
            self.__adjust_job_size(job_current_elapsed_time)
            # reset the state for COMPLETED job
            self.__reset_state()
