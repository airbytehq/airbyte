#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from enum import Enum
from os import remove
from time import sleep, time
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk import AirbyteLogger
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import ShopifyBulkExceptions
from .query import ShopifyBulkQuery, ShopifyBulkTemplates
from .record import END_OF_FILE, ShopifyBulkRecord
from .tools import BulkTools


class ShopifyBulkStatus(Enum):
    CREATED = "CREATED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ACCESS_DENIED = "ACCESS_DENIED"


class ShopifyBulkJob:

    """
    Class to create, check, retrieve the result for Shopify GraphQL Bulk Jobs.
    """

    def __init__(self, session: requests.Session, logger: AirbyteLogger, query: ShopifyBulkQuery) -> None:
        self.session = session
        self.logger = logger
        self.record_producer: ShopifyBulkRecord = ShopifyBulkRecord(query)
        self.tools: BulkTools = BulkTools()

    # 5Mb chunk size to save the file
    retrieve_chunk_size = 1024 * 1024 * 5

    # time between job status checks
    job_check_interval_sec: int = 5

    # max attempts for job creation
    concurrent_max_retry = 10
    # attempt counter
    concurrent_attempt = 0
    # attempt limit indicator
    concurrent_max_attempt_reached = False
    # sleep time per creation attempt
    concurrent_interval_sec = 45

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def get_errors_from_response(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, response: `{response.text}`. Trace: {repr(e)}."
            )

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

    def retry_concurrent_request(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        # increment attempt
        self.concurrent_attempt += 1
        # try to execute previous request, it's handy because we can retry / each slice yielded
        self.logger.warning(
            f"The BULK concurrency limit has reached. Waiting {self.concurrent_interval_sec} sec before retry, atttempt: {self.concurrent_attempt}.",
        )
        sleep(self.concurrent_interval_sec)
        # retry current `request`
        return self.job_create(request)

    def job_check_for_errors(self, errors: Optional[Iterable[Mapping[str, Any]]] = None) -> None:
        if errors:
            # when we have the scenario we didn't face yet.
            raise ShopifyBulkExceptions.BulkJobError(f"Something wong with the BULK job, errors: {errors}")

    def job_get_id(self, response: Optional[requests.Response] = None) -> Optional[str]:
        response_data = response.json() if response else {}
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

    def job_create(self, request: requests.PreparedRequest) -> Optional[requests.Response]:
        # create the server-side job
        response = self.session.send(request)
        # errors check
        errors = self.get_errors_from_response(response)
        # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
        if not self.has_running_concurrent_job(errors):
            # the errors are handled in `job_check_for_errors`
            return response if not self.job_check_for_errors(errors) else None
        else:
            return self.job_retry_on_concurrency(request)

    def job_log_status(self, bulk_job_id: str, status: str) -> None:
        self.logger.info(f"The BULK Job: `{bulk_job_id}` is {status}.")

    def job_check_status(self, url: str, bulk_job_id: str, is_test: bool = False) -> Optional[str]:
        request_args = {
            "method": "POST",
            "url": url,
            "data": ShopifyBulkTemplates.status(bulk_job_id),
            "headers": {"Content-Type": "application/graphql"},
        }
        status: str = None
        while status != ShopifyBulkStatus.COMPLETED.value:
            # re-use of `self._session(*, **)` to make BULK Job status checks
            response = self.session.request(**request_args)
            # errors check
            errors = self.get_errors_from_response(response)
            if not errors:
                status = response.json().get("data", {}).get("node", {}).get("status")
                if status == ShopifyBulkStatus.RUNNING.value:
                    self.job_log_status(bulk_job_id, status)
                    sleep(self.job_check_interval_sec)
                    # this is needed for test purposes,
                    if is_test:
                        return None
                elif status == ShopifyBulkStatus.FAILED.value:
                    self.job_log_status(bulk_job_id, status)
                    raise ShopifyBulkExceptions.BulkJobFailed(
                        f"The BULK Job: `{bulk_job_id}` exited with {status}, details: {self.get_errors_from_response(response)}",
                    )
                elif status == ShopifyBulkStatus.TIMEOUT.value:
                    self.job_log_status(bulk_job_id, status)
                    raise ShopifyBulkExceptions.BulkJobTimout(
                        f"The BULK Job: `{bulk_job_id}` exited with {status}, please reduce the `GraphQL BULK Date Range in Days` in SOURCES > Your Shopify Source > SETTINGS.",
                    )
                elif status == ShopifyBulkStatus.ACCESS_DENIED.value:
                    self.job_log_status(bulk_job_id, status)
                    raise ShopifyBulkExceptions.BulkJobAccessDenied(
                        f"The BULK Job: `{bulk_job_id}` exited with {status}, please check your PERMISSION to fetch the data for this stream.",
                    )
            else:
                raise Exception(f"Could not validate the status of the BULK Job `{bulk_job_id}`. Errors: {errors}.")

        # return when status is `COMPLETED`
        self.job_log_status(bulk_job_id, status)
        return response.json().get("data", {}).get("node", {}).get("url")

    def job_check(self, url: str, created_job_response: requests.Response, is_test: bool = False) -> Optional[str]:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.

        :: is_test: bool (default = False) - service flag to be able to manage unit_tests for `RUNNING` status.
        """
        bulk_job_id: str = self.job_get_id(created_job_response)
        if bulk_job_id:
            job_started = time()
            try:
                return self.job_check_status(url, bulk_job_id, is_test)
            except (
                ShopifyBulkExceptions.BulkJobFailed,
                ShopifyBulkExceptions.BulkJobTimout,
                ShopifyBulkExceptions.BulkJobAccessDenied,
            ) as bulk_job_error:
                raise bulk_job_error
            except Exception as e:
                raise ShopifyBulkExceptions.BulkJobUnknownError(f"The BULK Job: `{bulk_job_id}` has unknown status. Trace: {repr(e)}.")
            finally:
                time_elapsed = round((time() - job_started), 3)
                self.logger.info(f"The BULK Job: `{bulk_job_id}` time elapsed: {time_elapsed} sec.")
        else:
            # the `bulk_job_id` could be `None`, indicating the `concurrent` backoff,
            # since the BULK job was  not created, it doesn't have the ID.
            return None

    def job_retrieve_result(self, job_result_url: str) -> str:
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

    def job_record_producer(self, job_result_url: str, remove_file: Optional[bool] = True) -> Iterable[Mapping[str, Any]]:
        try:
            # save the content to the local file
            filename = self.job_retrieve_result(job_result_url)
            # produce records from saved result
            yield from self.record_producer.produce_records(filename)
        except Exception as e:
            raise ShopifyBulkExceptions.BulkRecordProduceError(
                f"An error occured while producing records from BULK Job result. Trace: {repr(e)}.",
            )
        finally:
            # removing the tmp file, if requested
            if remove_file and filename:
                try:
                    remove(filename)
                except Exception as e:
                    self.logger.info(f"Failed to remove the `tmp job result` file, the file doen't exist. Details: {repr(e)}.")
                    # we should pass here, if the file wasn't removed , it's either:
                    # - doesn't exist
                    # - will be dropped with the container shut down.
                    pass
