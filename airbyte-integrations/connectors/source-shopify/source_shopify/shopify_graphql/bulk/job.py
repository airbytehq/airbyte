#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass, field
from datetime import datetime
from time import sleep, time
from typing import Any, Final, Iterable, List, Mapping, Optional

import pendulum as pdm
import requests
from airbyte_cdk import AirbyteLogger
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import AirbyteTracedException, ShopifyBulkExceptions
from .query import ShopifyBulkTemplates
from .retry import bulk_retry_on_exception
from .status import ShopifyBulkJobStatus
from .tools import END_OF_FILE, BulkTools


@dataclass
class ShopifyBulkManager:
    session: requests.Session
    base_url: str
    stream_name: str

    # default logger
    logger: Final[AirbyteLogger] = logging.getLogger("airbyte")

    # 10Mb chunk size to save the file
    _retrieve_chunk_size: Final[int] = 1024 * 1024 * 10
    _job_max_retries: Final[int] = 6
    _job_backoff_time: int = 5
    # saved latest request
    _request: Optional[requests.Request] = None

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
    _job_state: ShopifyBulkJobStatus = field(init=False, default=None)
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
    # P365D, upper boundary for slice size
    _job_size_max: Final[float] = 365.0
    # dynamically adjusted slice interval
    _job_size: float = field(init=False, default=0.0)
    # expand slice factor
    _job_size_expand_factor: int = field(init=False, default=2)
    # reduce slice factor
    _job_size_reduce_factor: int = field(init=False, default=2)
    # whether or not the slicer should revert the previous start value
    _job_should_revert_slice: bool = field(init=False, default=False)

    # Each job ideally should be executed within the specified time (in sec),
    # to maximize the performance for multi-connection syncs and control the bulk job size within +- 1 hours (3600 sec),
    # Ideally the source will balance on it's own rate, based on the time taken to return the data for the slice.
    _job_max_elapsed_time: Final[float] = 2700.0
    # 2 sec is set as default value to cover the case with the empty-fast-completed jobs
    _job_last_elapsed_time: float = field(init=False, default=2.0)

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

    def _expand_job_size(self) -> None:
        self._job_size += self._job_size_adjusted_expand_factor

    def _reduce_job_size(self) -> None:
        self._job_size /= self._job_size_adjusted_reduce_factor

    def _save_latest_request(self, response: requests.Response) -> None:
        self._request = response.request

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

    def _job_completed(self) -> bool:
        return self._job_state == ShopifyBulkJobStatus.COMPLETED.value

    def _job_canceled(self) -> bool:
        return self._job_state == ShopifyBulkJobStatus.CANCELED.value

    def _job_cancel(self) -> None:
        # re-use of `self._session(*, **)` to make BULK Job cancel request
        cancel_args = self._job_get_request_args(ShopifyBulkTemplates.cancel)
        with self.session as cancel_job:
            canceled_response = cancel_job.request(**cancel_args)
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
            self._log_state(message)
            self._log_job_msg_count = 0

    def _log_state(self, message: Optional[str] = None) -> None:
        pattern = f"Stream: `{self.stream_name}`, the BULK Job: `{self._job_id}` is {self._job_state}"
        if message:
            self.logger.info(f"{pattern}. {message}.")
        else:
            self.logger.info(pattern)

    def _job_get_request_args(self, template: ShopifyBulkTemplates) -> Mapping[str, Any]:
        return {
            "method": "POST",
            "url": self.base_url,
            "data": template(self._job_id),
            "headers": {"Content-Type": "application/graphql"},
        }

    def _job_get_result(self, response: Optional[requests.Response] = None) -> Optional[str]:
        parsed_response = response.json().get("data", {}).get("node", {}) if response else None
        job_result_url = parsed_response.get("url") if parsed_response and not self._job_self_canceled else None
        if job_result_url:
            # save to local file using chunks to avoid OOM
            filename = self._tools.filename_from_url(job_result_url)
            with self.session.get(job_result_url, stream=True) as response:
                response.raise_for_status()
                with open(filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=self._retrieve_chunk_size):
                        file.write(chunk)
                    # add `<end_of_file>` line to the bottom  of the saved data for easy parsing
                    file.write(END_OF_FILE.encode())
            return filename

    def _job_update_state(self, response: Optional[requests.Response] = None) -> None:
        if response:
            self._job_state = response.json().get("data", {}).get("node", {}).get("status")
            if self._job_state in [ShopifyBulkJobStatus.RUNNING.value, ShopifyBulkJobStatus.CANCELING.value]:
                self._log_job_state_with_count()
            else:
                self._log_state()

    def _on_created_job(self, **kwargs) -> None:
        pass

    def _on_canceled_job(self, response: requests.Response) -> Optional[AirbyteTracedException]:
        if not self._job_self_canceled:
            raise ShopifyBulkExceptions.BulkJobCanceled(
                f"The BULK Job: `{self._job_id}` exited with {self._job_state}, details: {response.text}",
            )

    def _on_canceling_job(self, **kwargs) -> None:
        sleep(self._job_check_interval)

    def _on_running_job(self, **kwargs) -> None:
        if self._is_long_running_job:
            self.logger.info(
                f"Stream: `{self.stream_name}` the BULK Job: {self._job_id} runs longer than expected. Retry with the reduced `Slice Size` after self-cancelation."
            )
            # cancel the long-running bulk job
            self._job_cancel()
        else:
            sleep(self._job_check_interval)

    def _on_completed_job(self, response: Optional[requests.Response] = None) -> None:
        self._job_result_filename = self._job_get_result(response)

    def _on_failed_job(self, response: requests.Response) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobFailed(
            f"The BULK Job: `{self._job_id}` exited with {self._job_state}, details: {response.text}",
        )

    def _on_timeout_job(self, **kwargs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobTimout(
            f"The BULK Job: `{self._job_id}` exited with {self._job_state}, please reduce the `GraphQL BULK Date Range in Days` in SOURCES > Your Shopify Source > SETTINGS.",
        )

    def _on_access_denied_job(self, **kwagrs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobAccessDenied(
            f"The BULK Job: `{self._job_id}` exited with {self._job_state}, please check your PERMISSION to fetch the data for this stream.",
        )

    def _on_job_with_errors(self, errors: List[Mapping[str, Any]]) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobUnknownError(
            f"Could not validate the status of the BULK Job `{self._job_id}`. Errors: {errors}."
        )

    def _job_check_for_errors(self, response: requests.Response) -> Optional[Iterable[Mapping[str, Any]]]:
        try:

            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, status: {response.status_code}, response: `{response.text}`. Trace: {repr(e)}."
            )

    def _job_send_state_request(self) -> requests.Response:
        with self.session as job_state_request:
            status_args = self._job_get_request_args(ShopifyBulkTemplates.status)
            self._request = requests.Request(**status_args, auth=self.session.auth).prepare()
            return job_state_request.send(self._request)

    def _job_track_running(self) -> None:
        job_state_response = self._job_send_state_request()
        errors = self._job_check_for_errors(job_state_response)
        if errors:
            # the exception raised when there are job-related errors, and the Job cannot be run futher.
            self._on_job_with_errors(errors)

        self._job_update_state(job_state_response)
        self._job_state_to_fn_map.get(self._job_state)(response=job_state_response)

    def _has_running_concurrent_job(self, errors: Optional[Iterable[Mapping[str, Any]]] = None) -> bool:
        """
        When concurent BULK Job is already running for the same SHOP we receive:
        Error example:
        [
            {
                'field': None,
                'message': 'A bulk query operation for this app and shop is already in progress: gid://shopify/BulkOperation/4039184154813.',
            }
        ]
        """

        concurent_job_pattern = "A bulk query operation for this app and shop is already in progress"
        # the errors are handled in `job_job_check_for_errors`
        if errors:
            for error in errors:
                message = error.get("message", "") if isinstance(error, dict) else ""
                if concurent_job_pattern in message:
                    return True
        # reset the `_concurrent_attempt` counter, once there is no concurrent job error
        self._concurrent_attempt = 0
        return False

    def _has_reached_max_concurrency(self) -> bool:
        return self._concurrent_attempt == self._concurrent_max_retry

    def _job_retry_request(self) -> Optional[requests.Response]:
        with self.session.send(self._request) as retried_request:
            return retried_request

    def _job_retry_concurrent(self) -> Optional[requests.Response]:
        self._concurrent_attempt += 1
        self.logger.warning(
            f"Stream: `{self.stream_name}`, the BULK concurrency limit has reached. Waiting {self._concurrent_interval} sec before retry, atttempt: {self._concurrent_attempt}.",
        )
        sleep(self._concurrent_interval)
        retried_response = self._job_retry_request()
        return self._job_healthcheck(retried_response)

    def _job_retry_on_concurrency(self) -> Optional[requests.Response]:
        if self._has_reached_max_concurrency():
            # indicate we're out of attempts to retry with job creation
            message = f"The BULK Job couldn't be created at this time, since another job is running."
            self.logger.error(message)
            # raise AibyteTracebackException with `INCOMPLETE` status
            raise ShopifyBulkExceptions.BulkJobConcurrentError(message)
        else:
            return self._job_retry_concurrent()

    def _job_healthcheck(self, response: requests.Response) -> Optional[requests.Response]:
        # save the latest request to retry
        self._save_latest_request(response)
        # check for query errors
        errors = self._job_check_for_errors(response)
        # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
        if self._has_running_concurrent_job(errors):
            return self._job_retry_on_concurrency()

        return response if not errors else None

    @bulk_retry_on_exception(logger)
    def _job_check_state(self) -> Optional[str]:
        while not self._job_completed():
            if self._job_canceled():
                break
            else:
                self._job_track_running()

    # external method to be used within other components

    def job_process_created(self, response: requests.Response) -> None:
        """
        The Bulk Job with CREATED status, should be processed, before we move forward with Job Status Checks.
        """
        response = self._job_healthcheck(response)
        bulk_response = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
        if bulk_response and bulk_response.get("status") == ShopifyBulkJobStatus.CREATED.value:
            self._job_id = bulk_response.get("id")
            self._job_created_at = bulk_response.get("createdAt")
            self.logger.info(f"Stream: `{self.stream_name}`, the BULK Job: `{self._job_id}` is {ShopifyBulkJobStatus.CREATED.value}")

    def job_size_normalize(self, start: datetime, end: datetime) -> datetime:
        # adjust slice size when it's bigger than the loop point when it should end,
        # to preserve correct job size adjustments when this is the only job we need to run, based on STATE provided
        requested_slice_size = (end - start).total_days()
        self._job_size = requested_slice_size if requested_slice_size < self._job_size else self._job_size

    def get_adjusted_job_start(self, slice_start: datetime) -> datetime:
        step = self._job_size if self._job_size else self._job_size_min
        return slice_start.add(days=step)

    def get_adjusted_job_end(self, slice_start: datetime, slice_end: datetime) -> datetime:
        if self._is_long_running_job:
            self._job_size_reduce_next()
            return slice_start
        else:
            return slice_end

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check_for_completion(self) -> Optional[str]:
        """
        This method checks the status for the `CREATED` Shopify BULK Job, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """
        # track created job until it's COMPLETED
        job_started = time()
        try:
            self._job_check_state()
            return self._job_result_filename
        except (
            ShopifyBulkExceptions.BulkJobCanceled,
            ShopifyBulkExceptions.BulkJobFailed,
            ShopifyBulkExceptions.BulkJobTimout,
            ShopifyBulkExceptions.BulkJobAccessDenied,
            # this one is retryable, but stil needs to be raised,
            # if the max attempts value is reached.
            ShopifyBulkExceptions.BulkJobUnknownError,
        ) as bulk_job_error:
            raise bulk_job_error
        finally:
            job_current_elapsed_time = round((time() - job_started), 3)
            self.logger.info(f"Stream: `{self.stream_name}`, the BULK Job: `{self._job_id}` time elapsed: {job_current_elapsed_time} sec.")
            # check whether or not we should expand or reduce the size of the slice
            self.__adjust_job_size(job_current_elapsed_time)
            # reset the state for COMPLETED job
            self.__reset_state()
