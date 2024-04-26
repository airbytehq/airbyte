#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from time import sleep, time
from typing import Any, Final, Iterable, List, Mapping, Optional, Union

import pendulum as pdm
import requests
from airbyte_cdk import AirbyteLogger
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import AirbyteTracedException, ShopifyBulkExceptions
from .query import ShopifyBulkTemplates
from .tools import END_OF_FILE, BulkTools


class ShopifyBulkStatus(Enum):
    CREATED = "CREATED"
    CANCELED = "CANCELED"
    CANCELING = "CANCELING"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"


@dataclass
class ShopifyBulkManager:
    session: requests.Session
    base_url: str
    stream_name: str

    # default logger
    logger: Final[AirbyteLogger] = logging.getLogger("airbyte")

    # 10Mb chunk size to save the file
    retrieve_chunk_size: Final[int] = 1024 * 1024 * 10
    # time between job status checks
    job_check_interval_sec: Final[int] = 2

    # sleep time per creation attempt
    concurrent_interval_sec: Final[int] = 30
    # max attempts for job creation
    concurrent_max_retry: Final[int] = 120
    # Each job ideally should be executed within the specified time (in sec),
    # to maximize the performance for multi-connection syncs and control the bulk job size within +- 1 hours (3600 sec),
    # Ideally the source will balance on it's own rate, based on the time taken to return the data for the slice.
    job_max_elapsed_time_sec: Final[float] = 1800.0
    # 0.1 ~= P2H, default value, lower boundary for slice size
    job_size_min: Final[float] = 0.1
    # P365D, upper boundary for slice size
    job_size_max: Final[float] = 365.0
    # running job logger constrain
    log_job_state_msg_frequency: Final[int] = 10
    # attempt limit indicator
    concurrent_max_attempt_reached: bool = field(init=False, default=False)
    # attempt counter
    concurrent_attempt: int = field(init=False, default=0)
    # currents: job_id, job_state, job_created_at, job_self_canceled
    job_id: Optional[str] = field(init=False, default=None)
    job_created_at: Optional[str] = field(init=False, default=None)
    job_self_canceled: bool = field(init=False, default=False)
    job_state: ShopifyBulkStatus = field(init=False, default=None)
    # 2 sec is set as default value to cover the case with the empty-fast-completed jobs
    job_last_elapsed_time: float = field(init=False, default=2.0)
    # dynamically adjusted slice interval
    job_size: float = field(init=False, default=0.0)
    # expand slice factor
    job_size_expand_factor: int = field(init=False, default=2)
    # reduce slice factor
    job_size_reduce_factor: int = field(init=False, default=2)
    # whether or not the slicer should revert the previous start value
    job_should_revert_slice: bool = field(init=False, default=False)
    # running job log counter
    log_job_state_msg_count: int = field(init=False, default=0)
    # one time retryable error counter
    _one_time_error_retried: bool = field(init=False, default=False)

    @property
    def tools(self) -> BulkTools:
        return BulkTools()

    @property
    def job_state_to_fn_map(self) -> Mapping[str, Any]:
        return {
            ShopifyBulkStatus.CREATED.value: self.on_created_job,
            ShopifyBulkStatus.CANCELING.value: self.on_canceling_job,
            ShopifyBulkStatus.CANCELED.value: self.on_canceled_job,
            ShopifyBulkStatus.COMPLETED.value: self.on_completed_job,
            ShopifyBulkStatus.RUNNING.value: self.on_running_job,
            ShopifyBulkStatus.TIMEOUT.value: self.on_timeout_job,
            ShopifyBulkStatus.FAILED.value: self.on_failed_job,
            ShopifyBulkStatus.ACCESS_DENIED.value: self.on_access_denied_job,
        }

    @property
    def job_size_adjusted_expand_factor(self, coef: float = 0.5) -> float:
        """
        The Job Size expand factor is calculated using EMA (Expotentional Moving Average):
            coef - the expantion coefficient
            previous_expand_factor - previous factor value

        Formula: expand_factor = coef * previous_expand_factor + (1 - coef)
        """

        return coef * self.job_size_expand_factor + (1 - coef)

    @property
    def job_size_adjusted_reduce_factor(self) -> float:
        """
        The Job Size reduce factor is 2, by default.
        """

        return self.job_size_reduce_factor

    @property
    def job_elapsed_time_in_state(self) -> int:
        """
        Returns the elapsed time taken while Job is in certain status/state.
        """
        return (pdm.now() - pdm.parse(self.job_created_at)).in_seconds() if self.job_created_at else 0

    @property
    def is_long_running_job(self) -> bool:
        if self.job_elapsed_time_in_state:
            if self.job_elapsed_time_in_state > self.job_max_elapsed_time_sec:
                # set the slicer to revert mode
                self.job_should_revert_slice = True
                return True
        # reset slicer to normal mode
        self.job_should_revert_slice = False
        return False

    def expand_job_size(self) -> None:
        self.job_size += self.job_size_adjusted_expand_factor

    def reduce_job_size(self) -> None:
        self.job_size /= self.job_size_adjusted_reduce_factor

    def job_size_normalize(self, start: datetime, end: datetime) -> datetime:
        # adjust slice size when it's bigger than the loop point when it should end,
        # to preserve correct job size adjustments when this is the only job we need to run, based on STATE provided
        requested_slice_size = (end - start).total_days()
        self.job_size = requested_slice_size if requested_slice_size < self.job_size else self.job_size

    def get_adjusted_job_end(self, slice_start: datetime, slice_end: datetime) -> datetime:
        if self.is_long_running_job:
            self._job_size_reduce_next()
            return slice_start
        else:
            return slice_end

    def get_adjusted_job_start(self, slice_start: datetime) -> datetime:
        step = self.job_size if self.job_size else self.job_size_min
        return slice_start.add(days=step)

    def _job_size_reduce_next(self) -> None:
        # revert the flag
        self.job_should_revert_slice = False
        self.reduce_job_size()

    def __adjust_job_size(self, job_current_elapsed_time: float) -> None:
        if self.job_should_revert_slice:
            pass
        else:
            if job_current_elapsed_time < 1 or job_current_elapsed_time < self.job_last_elapsed_time:
                self.expand_job_size()
            elif job_current_elapsed_time > self.job_last_elapsed_time < self.job_max_elapsed_time_sec:
                pass
            # set the last job time
            self.job_last_elapsed_time = job_current_elapsed_time
            # check the job size slice interval are acceptable
            self.job_size = max(self.job_size_min, min(self.job_size, self.job_size_max))

    def __reset_state(self) -> None:
        # set current job state to default values
        self.job_state, self.job_id = None, None
        # setting self-cancelation to default
        self.job_self_canceled = False
        # set the running job message counter to default
        self.log_job_state_msg_count = 0
        # set one time retry flag to default
        self._one_time_error_retried = False

    def job_completed(self) -> bool:
        return self.job_state == ShopifyBulkStatus.COMPLETED.value

    def job_canceled(self) -> bool:
        return self.job_state == ShopifyBulkStatus.CANCELED.value

    def job_cancel(self) -> None:
        # re-use of `self._session(*, **)` to make BULK Job cancel request
        cancel_args = self.job_get_request_args(ShopifyBulkTemplates.cancel)
        with self.session as cancel_job:
            canceled_response = cancel_job.request(**cancel_args)
            # mark the job was self-canceled
            self.job_self_canceled = True
            # check CANCELED Job health
            self.job_healthcheck(canceled_response)
        # sleep to ensure the cancelation
        sleep(self.job_check_interval_sec)

    def log_job_state_with_count(self) -> None:
        """
        Print the status/state Job info message every N request, to minimize the noise in the logs.
        """
        if self.log_job_state_msg_count < self.log_job_state_msg_frequency:
            self.log_job_state_msg_count += 1
        else:
            message = f"Elapsed time: {self.job_elapsed_time_in_state} sec"
            self.log_state(message)
            self.log_job_state_msg_count = 0

    def log_state(self, message: Optional[str] = None) -> None:
        pattern = f"Stream: `{self.stream_name}`, the BULK Job: `{self.job_id}` is {self.job_state}"
        if message:
            self.logger.info(f"{pattern}. {message}.")
        else:
            self.logger.info(pattern)

    def job_get_request_args(self, template: ShopifyBulkTemplates) -> Mapping[str, Any]:
        return {
            "method": "POST",
            "url": self.base_url,
            "data": template(self.job_id),
            "headers": {"Content-Type": "application/graphql"},
        }

    def job_get_result(self, response: Optional[requests.Response] = None) -> Optional[str]:
        parsed_response = response.json().get("data", {}).get("node", {}) if response else None
        job_result_url = parsed_response.get("url") if parsed_response and not self.job_self_canceled else None
        if job_result_url:
            # save to local file using chunks to avoid OOM
            filename = self.tools.filename_from_url(job_result_url)
            with self.session.get(job_result_url, stream=True) as response:
                response.raise_for_status()
                with open(filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=self.retrieve_chunk_size):
                        file.write(chunk)
                    # add `<end_of_file>` line to the bottom  of the saved data for easy parsing
                    file.write(END_OF_FILE.encode())
            return filename

    def job_update_state(self, response: Optional[requests.Response] = None) -> None:
        if response:
            self.job_state = response.json().get("data", {}).get("node", {}).get("status")
            if self.job_state in [ShopifyBulkStatus.RUNNING.value, ShopifyBulkStatus.CANCELING.value]:
                self.log_job_state_with_count()
            else:
                self.log_state()

    def on_created_job(self, **kwargs) -> None:
        pass

    def on_canceled_job(self, response: requests.Response) -> Optional[AirbyteTracedException]:
        if not self.job_self_canceled:
            raise ShopifyBulkExceptions.BulkJobCanceled(
                f"The BULK Job: `{self.job_id}` exited with {self.job_state}, details: {response.text}",
            )
        else:
            pass

    def on_canceling_job(self, **kwargs) -> None:
        sleep(self.job_check_interval_sec)

    def on_running_job(self, **kwargs) -> None:
        if self.is_long_running_job:
            self.logger.info(
                f"Stream: `{self.stream_name}` the BULK Job: {self.job_id} runs longer than expected. Retry with the reduced `Slice Size` after self-cancelation."
            )
            # cancel the long-running bulk job
            self.job_cancel()
        else:
            sleep(self.job_check_interval_sec)

    def on_completed_job(self, **kwargs) -> None:
        pass

    def on_failed_job(self, response: requests.Response) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobFailed(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, details: {response.text}",
        )

    def on_timeout_job(self, **kwargs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobTimout(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, please reduce the `GraphQL BULK Date Range in Days` in SOURCES > Your Shopify Source > SETTINGS.",
        )

    def on_access_denied_job(self, **kwagrs) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobAccessDenied(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, please check your PERMISSION to fetch the data for this stream.",
        )

    def on_job_with_errors(self, errors: List[Mapping[str, Any]]) -> AirbyteTracedException:
        raise ShopifyBulkExceptions.BulkJobUnknownError(f"Could not validate the status of the BULK Job `{self.job_id}`. Errors: {errors}.")

    def job_check_for_errors(self, response: requests.Response) -> Union[AirbyteTracedException, Iterable[Mapping[str, Any]]]:
        try:
            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, status: {response.status_code}, response: `{response.text}`. Trace: {repr(e)}."
            )

    def job_one_time_retry_error(self, response: requests.Response, exception: Exception) -> Optional[requests.Response]:
        if not self._one_time_error_retried:
            request = response.request
            self.logger.info(f"Stream: `{self.stream_name}`, retrying `Bad Request`: {request.body}. Error: {repr(exception)}.")
            self._one_time_error_retried = True
            return self.job_retry_request(request)
        else:
            self.on_job_with_errors(self.job_check_for_errors(response))

    def job_track_running(self) -> Union[AirbyteTracedException, requests.Response]:
        # format Job state check args
        status_args = self.job_get_request_args(ShopifyBulkTemplates.status)
        # re-use of `self._session(*, **)` to make BULK Job status checks
        with self.session as track_running_job:
            response = track_running_job.request(**status_args)
        # errors check
        try:
            errors = self.job_check_for_errors(response)
            if not errors:
                self.job_update_state(response)
                self.job_state_to_fn_map.get(self.job_state)(response=response)
                return response
            else:
                # execute ERRORS scenario
                self.on_job_with_errors(errors)
        except (
            ShopifyBulkExceptions.BulkJobBadResponse,
            ShopifyBulkExceptions.BulkJobUnknownError,
        ) as error:
            return self.job_one_time_retry_error(response, error)

    def job_check_state(self) -> Optional[str]:
        response: Optional[requests.Response] = None
        while not self.job_completed():
            if self.job_canceled():
                break
            else:
                response = self.job_track_running()
        # return `job_result_url` when status is `COMPLETED`
        return self.job_get_result(response)

    def has_running_concurrent_job(self, errors: Optional[Iterable[Mapping[str, Any]]] = None) -> bool:
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
        # reset the `concurrent_attempt` counter, once there is no concurrent job error
        self.concurrent_attempt = 0
        return False

    def has_reached_max_concurrency_attempt(self) -> bool:
        return self.concurrent_attempt == self.concurrent_max_retry

    def job_retry_request(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        with self.session.send(request) as retried_request:
            return retried_request

    def job_retry_concurrent(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        self.concurrent_attempt += 1
        self.logger.warning(
            f"Stream: `{self.stream_name}`, the BULK concurrency limit has reached. Waiting {self.concurrent_interval_sec} sec before retry, atttempt: {self.concurrent_attempt}.",
        )
        sleep(self.concurrent_interval_sec)
        return self.job_healthcheck(self.job_retry_request(request))

    def job_get_id(self, response: requests.Response) -> Optional[str]:
        response_data = response.json()
        bulk_response = response_data.get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
        if bulk_response and bulk_response.get("status") == ShopifyBulkStatus.CREATED.value:
            job_id = bulk_response.get("id")
            self.job_created_at = bulk_response.get("createdAt")
            self.logger.info(f"Stream: `{self.stream_name}`, the BULK Job: `{job_id}` is {ShopifyBulkStatus.CREATED.value}")
            return job_id
        else:
            return None

    def job_retry_on_concurrency(self, request: requests.PreparedRequest) -> Union[AirbyteTracedException, Optional[requests.Response]]:
        if self.has_reached_max_concurrency_attempt():
            # indicate we're out of attempts to retry with job creation
            message = f"The BULK Job couldn't be created at this time, since another job is running."
            # log the message
            self.logger.error(message)
            # raise AibyteTracebackException with `INCOMPLETE` status
            raise ShopifyBulkExceptions.BulkJobConcurrentError(message)
        else:
            return self.job_retry_concurrent(request)

    def job_healthcheck(self, response: requests.Response) -> Optional[requests.Response]:
        # get the latest request to retry
        request: requests.PreparedRequest = response.request
        try:
            errors = self.job_check_for_errors(response)
            # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
            if not self.has_running_concurrent_job(errors):
                return response if not errors else None
            else:
                return self.job_retry_on_concurrency(request)
        except (ShopifyBulkExceptions.BulkJobBadResponse, ShopifyBulkExceptions.BulkJobUnknownError) as err:
            # sometimes we face with `HTTP-500 Internal Server Error`
            # we should retry such at least once
            self.logger.info(f"Stream: `{self.stream_name}`, retrying Bad Request: {request.body}, error: {repr(err)}.")
            return self.job_retry_request(request)

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check(self, created_job_response: requests.Response) -> Optional[str]:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """
        job_response = self.job_healthcheck(created_job_response)
        self.job_id: str = self.job_get_id(job_response)
        job_started = time()
        try:
            return self.job_check_state()
        except (
            ShopifyBulkExceptions.BulkJobCanceled,
            ShopifyBulkExceptions.BulkJobFailed,
            ShopifyBulkExceptions.BulkJobTimout,
            ShopifyBulkExceptions.BulkJobAccessDenied,
            # this one is one-time retriable
            ShopifyBulkExceptions.BulkJobUnknownError,
        ) as bulk_job_error:
            raise bulk_job_error
        finally:
            job_current_elapsed_time = round((time() - job_started), 3)
            self.logger.info(f"Stream: `{self.stream_name}`, the BULK Job: `{self.job_id}` time elapsed: {job_current_elapsed_time} sec.")
            # check whether or not we should expand or reduce the size of the slice
            self.__adjust_job_size(job_current_elapsed_time)
            # reset the state for COMPLETED job
            self.__reset_state()
