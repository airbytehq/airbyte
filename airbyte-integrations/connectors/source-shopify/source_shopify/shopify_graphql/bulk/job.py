#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from enum import Enum
from time import sleep, time
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk import AirbyteLogger
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import ShopifyBulkExceptions
from .query import ShopifyBulkTemplates
from .tools import END_OF_FILE, BulkTools


class ShopifyBulkStatus(Enum):
    CREATED = "CREATED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"


class ShopifyBulkManager:
    def __init__(self, session: requests.Session, base_url: str, logger: AirbyteLogger) -> None:
        self.session = session
        self.base_url = base_url
        self.logger = logger
        self.tools: BulkTools = BulkTools()
        # current job attributes
        self.job_id: str = None
        self.job_state: ShopifyBulkStatus[str] = None

    # 5Mb chunk size to save the file
    retrieve_chunk_size: int = 1024 * 1024 * 5

    # time between job status checks
    job_check_interval_sec: int = 5

    # max attempts for job creation
    concurrent_max_retry: int = 19
    # attempt counter
    concurrent_attempt: int = 0
    # attempt limit indicator
    concurrent_max_attempt_reached: bool = False
    # sleep time per creation attempt
    concurrent_interval_sec = 30

    @property
    def process_job_fn_mapping(self) -> Mapping[str, Any]:
        return {
            ShopifyBulkStatus.RUNNING.value: self.on_running_job,
            ShopifyBulkStatus.TIMEOUT.value: self.on_timeout_job,
            ShopifyBulkStatus.FAILED.value: self.on_failed_job,
            ShopifyBulkStatus.ACCESS_DENIED.value: self.on_access_denied_job,
        }

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def check_for_errors(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, response: `{response.text}`. Trace: {repr(e)}."
            )

    def update_status(self, response: Optional[requests.Response] = None) -> None:
        if response:
            response_data = response.json().get("data", {}).get("node", {})
            self.job_id = response_data.get("id")
            self.job_state = response_data.get("status")
            self.log_state()

    def reset_state(self) -> None:
        # set current job status and id to default value
        self.job_state, self.job_id = None, None

    def completed(self) -> bool:
        return self.job_state == ShopifyBulkStatus.COMPLETED.value

    def running(self) -> bool:
        return self.job_state == ShopifyBulkStatus.RUNNING.value

    def failed(self) -> bool:
        return self.job_state == ShopifyBulkStatus.FAILED.value

    def timeout(self) -> bool:
        return self.job_state == ShopifyBulkStatus.TIMEOUT.value

    def access_denied(self) -> bool:
        return self.job_state == ShopifyBulkStatus.ACCESS_DENIED.value

    def get_status_args(self, bulk_job_id: str) -> Mapping[str, Any]:
        return {
            "method": "POST",
            "url": self.base_url,
            "data": ShopifyBulkTemplates.status(bulk_job_id),
            "headers": {"Content-Type": "application/graphql"},
        }

    def log_state(self) -> None:
        self.logger.info(f"The BULK Job: `{self.job_id}` is {self.job_state}.")

    def on_running_job(self, **kwargs) -> None:
        sleep(self.job_check_interval_sec)

    def on_completed_job(self, response: Optional[requests.Response] = None) -> Optional[requests.Response]:
        # reset status on COMPLETED job
        self.reset_state()
        return self.retrieve_result(response)

    def retrieve_result(self, response: Optional[requests.Response] = None) -> Optional[str]:
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

    def on_failed_job(self, response: requests.Response) -> None:
        raise ShopifyBulkExceptions.BulkJobFailed(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, details: {response.text}",
        )

    def on_timeout_job(self, **kwargs) -> None:
        raise ShopifyBulkExceptions.BulkJobTimout(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, please reduce the `GraphQL BULK Date Range in Days` in SOURCES > Your Shopify Source > SETTINGS.",
        )

    def on_access_denied_job(self, **kwagrs) -> None:
        raise ShopifyBulkExceptions.BulkJobAccessDenied(
            f"The BULK Job: `{self.job_id}` exited with {self.job_state}, please check your PERMISSION to fetch the data for this stream.",
        )

    def on_job_with_errors(self, errors: List[Mapping[str, Any]]) -> None:
        raise ShopifyBulkExceptions.BulkJobUnknownError(f"Could not validate the status of the BULK Job `{self.job_id}`. Errors: {errors}.")

    def on_successful_job(self, response: requests.Response) -> None:
        self.update_status(response)
        process_fn = self.process_job_fn_mapping.get(self.job_state)
        if process_fn:
            process_fn(response=response)

    def check_state(self, bulk_job_id: str, is_running_test: bool = False) -> Optional[str]:
        response = None
        status_args = self.get_status_args(bulk_job_id)
        while not self.completed():
            # re-use of `self._session(*, **)` to make BULK Job status checks
            response = self.session.request(**status_args)
            errors = self.check_for_errors(response)
            if not errors:
                self.on_successful_job(response)
                if is_running_test:
                    return None
            else:
                # execute ERRORS scenario
                self.on_job_with_errors(errors)
        # return `job_result_url`: str when status is `COMPLETED`
        return self.on_completed_job(response)

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
        # the errors are handled in `job_check_for_errors`
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

    def _job_create(self, request: requests.PreparedRequest) -> requests.Response:
        """
        Sends HTTPS request to create Shopify BULK Operatoion.
        https://shopify.dev/docs/api/usage/bulk-operations/queries#bulk-query-overview
        """
        return self.session.send(request)

    def retry_concurrent_request(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        # increment attempt
        self.concurrent_attempt += 1
        # try to execute previous request, it's handy because we can retry / each slice yielded
        self.logger.warning(
            f"The BULK concurrency limit has reached. Waiting {self.concurrent_interval_sec} sec before retry, atttempt: {self.concurrent_attempt}.",
        )
        sleep(self.concurrent_interval_sec)
        # retry current `request`
        return self.job_healthcheck(self._job_create(request))

    def job_get_id(self, response: requests.Response) -> Optional[str]:
        response_data = response.json()
        bulk_response = response_data.get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
        if bulk_response and bulk_response.get("status") == ShopifyBulkStatus.CREATED.value:
            job_id = bulk_response.get("id")
            self.logger.info(f"The BULK Job: `{job_id}` is {ShopifyBulkStatus.CREATED.value}")
            return job_id
        else:
            return None

    def job_retry_on_concurrency(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        if self.has_reached_max_concurrency_attempt():
            # indicate we're out of attempts to retry with job creation
            self.logger.error(f"The BULK Job couldn't be created at this time, since another job is running.")
            return None
        else:
            return self.retry_concurrent_request(request)

    def job_healthcheck(self, response: requests.Response) -> Optional[requests.Response]:
        # errors check
        errors = self.check_for_errors(response)
        # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
        if not self.has_running_concurrent_job(errors):
            return response if not errors else None
        else:
            # get the latest request to retry
            request: requests.PreparedRequest = response.request
            return self.job_retry_on_concurrency(request)

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check(self, created_job_response: requests.Response, is_running_test: bool = False) -> Optional[str]:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.

        :: is_running_test: bool (default = False) - service flag to be able to manage unit_tests for `RUNNING` status.
        """
        job_response = self.job_healthcheck(created_job_response)
        if job_response:
            bulk_job_id: str = self.job_get_id(job_response)
            job_started = time()
            try:
                return self.check_state(bulk_job_id, is_running_test)
            except (
                ShopifyBulkExceptions.BulkJobFailed,
                ShopifyBulkExceptions.BulkJobTimout,
                ShopifyBulkExceptions.BulkJobAccessDenied,
                ShopifyBulkExceptions.BulkJobUnknownError,
            ) as bulk_job_error:
                raise bulk_job_error
            finally:
                time_elapsed = round((time() - job_started), 3)
                self.logger.info(f"The BULK Job: `{bulk_job_id}` time elapsed: {time_elapsed} sec.")
        else:
            # the `job_response` could be `None`, indicating the `concurrent` backoff,
            # since the BULK job was not created, most likely due to the running concurent BULK job.
            return None
