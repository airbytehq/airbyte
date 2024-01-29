#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass, field
from enum import Enum
from time import sleep, time
from typing import Any, Iterable, List, Mapping, Optional, Union

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
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"


@dataclass
class ShopifyBulkManager:
    session: requests.Session
    base_url: str

    # 5Mb chunk size to save the file
    retrieve_chunk_size: int = 1024 * 1024 * 5
    # time between job status checks
    job_check_interval_sec: int = 5

    # PLATFORM HEARTBEAT NOTES:
    # 30 sec / attempt * 19 attempts = 570 sec of wait time in total,
    # which is < 10 min of retrying, before Heartbeat will kill the source as non-responsive

    # sleep time per creation attempt
    concurrent_interval_sec = 30
    # max attempts for job creation
    concurrent_max_retry: int = 19

    # attempt limit indicator
    concurrent_max_attempt_reached: bool = field(init=False, default=False)
    # attempt counter
    concurrent_attempt: int = field(init=False, default=0)

    # default logger
    logger: AirbyteLogger = field(init=False, default=logging.getLogger("airbyte"))

    # currents: job_id, job_state
    job_id: Optional[str] = field(init=False, default=None)
    job_state: ShopifyBulkStatus = field(init=False, default=None)

    @property
    def tools(self) -> BulkTools:
        return BulkTools()

    @property
    def job_state_to_fn_map(self) -> Mapping[str, Any]:
        return {
            ShopifyBulkStatus.CREATED.value: self.on_created_job,
            ShopifyBulkStatus.COMPLETED.value: self.on_completed_job,
            ShopifyBulkStatus.RUNNING.value: self.on_running_job,
            ShopifyBulkStatus.TIMEOUT.value: self.on_timeout_job,
            ShopifyBulkStatus.FAILED.value: self.on_failed_job,
            ShopifyBulkStatus.ACCESS_DENIED.value: self.on_access_denied_job,
        }

    def __reset_state(self) -> None:
        # set current job state to default value
        self.job_state, self.job_id = None, None

    def job_completed(self) -> bool:
        return self.job_state == ShopifyBulkStatus.COMPLETED.value

    def log_state(self) -> None:
        self.logger.info(f"The BULK Job: `{self.job_id}` is {self.job_state}.")

    def job_get_state_args(self) -> Mapping[str, Any]:
        return {
            "method": "POST",
            "url": self.base_url,
            "data": ShopifyBulkTemplates.status(self.job_id),
            "headers": {"Content-Type": "application/graphql"},
        }

    def job_get_result(self, response: Optional[requests.Response] = None) -> Optional[str]:
        job_result_url = response.json().get("data", {}).get("node", {}).get("url") if response else None
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
            self.log_state()

    def on_created_job(self, **kwargs) -> None:
        pass

    def on_running_job(self, **kwargs) -> None:
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

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check_for_errors(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, response: `{response.text}`. Trace: {repr(e)}."
            )

    def job_track_running(self) -> Union[AirbyteTracedException, requests.Response]:
        # format Job state check args
        status_args = self.job_get_state_args()
        # re-use of `self._session(*, **)` to make BULK Job status checks
        response = self.session.request(**status_args)
        # errors check
        errors = self.job_check_for_errors(response)
        if not errors:
            self.job_update_state(response)
            self.job_state_to_fn_map.get(self.job_state)(response=response)
            return response
        else:
            # execute ERRORS scenario
            self.on_job_with_errors(errors)

    def job_check_state(self) -> Optional[str]:
        while not self.job_completed():
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
                message = error.get("message", "")
                if concurent_job_pattern in message:
                    return True
        # reset the `concurrent_attempt` counter, once there is no concurrent job error
        self.concurrent_attempt = 0
        return False

    def has_reached_max_concurrency_attempt(self) -> bool:
        return self.concurrent_attempt == self.concurrent_max_retry

    def job_retry_concurrent(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        # increment attempt
        self.concurrent_attempt += 1
        # try to execute previous request, it's handy because we can retry / each slice yielded
        self.logger.warning(
            f"The BULK concurrency limit has reached. Waiting {self.concurrent_interval_sec} sec before retry, atttempt: {self.concurrent_attempt}.",
        )
        sleep(self.concurrent_interval_sec)
        # retry current `request`
        return self.job_healthcheck(self.session.send(request))

    def job_get_id(self, response: requests.Response) -> Optional[str]:
        response_data = response.json()
        bulk_response = response_data.get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
        if bulk_response and bulk_response.get("status") == ShopifyBulkStatus.CREATED.value:
            job_id = bulk_response.get("id")
            self.logger.info(f"The BULK Job: `{job_id}` is {ShopifyBulkStatus.CREATED.value}")
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
        # errors check
        errors = self.job_check_for_errors(response)
        # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
        if not self.has_running_concurrent_job(errors):
            return response if not errors else None
        else:
            # get the latest request to retry
            request: requests.PreparedRequest = response.request
            return self.job_retry_on_concurrency(request)

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
            ShopifyBulkExceptions.BulkJobFailed,
            ShopifyBulkExceptions.BulkJobTimout,
            ShopifyBulkExceptions.BulkJobAccessDenied,
            ShopifyBulkExceptions.BulkJobUnknownError,
        ) as bulk_job_error:
            raise bulk_job_error
        finally:
            time_elapsed = round((time() - job_started), 3)
            self.logger.info(f"The BULK Job: `{self.job_id}` time elapsed: {time_elapsed} sec.")
            # reset the state for COMPLETED job
            self.__reset_state()
