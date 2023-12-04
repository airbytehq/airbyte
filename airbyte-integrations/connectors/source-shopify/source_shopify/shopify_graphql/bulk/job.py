#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from os import remove
from time import sleep, time
from typing import Any, Callable, Iterable, Mapping, Optional

import requests
from airbyte_cdk import AirbyteLogger
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from .exceptions import ShopifyBulkExceptions
from .query import ShopifyBulkTemplates
from .record import ShopifyBulkRecord
from .status import ShopifyBulkStatus
from .tools import BulkTools


class ShopifyBulkJob:

    """
    Class to create, check, retrieve the result for Shopify GraphQL Bulk Jobs.
    """

    def __init__(self, session: requests.Session, logger: AirbyteLogger) -> None:
        self.session = session
        self.logger = logger
        self.record_producer: ShopifyBulkRecord = ShopifyBulkRecord()
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

    def get_errors_from_response(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            return response.json().get("errors") or response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
        except (Exception, JSONDecodeError) as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"Couldn't check the `response` for `errors`, response: `{response.text}`. Trace: {repr(e)}."
            )

    def has_running_concurrent_job(self, response: requests.Response) -> bool:
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
        errors = self.get_errors_from_response(response)
        if errors:
            for error in errors:
                message = error.get("message", "")
                if concurent_job_pattern in message:
                    return True
                else:
                    continue
        else:
            return False

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check_for_errors(self, response: requests.Response) -> None:
        try:
            # checking for other errors
            errors = self.get_errors_from_response(response)
            if errors:
                # when we have the scenario we didn't face yet.
                raise ShopifyBulkExceptions.BulkJobError(f"Something wong with the BULK job, errors: {errors}")
        except JSONDecodeError as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"The BULK Job result contains errors or could not be parsed. Details: {response.text}. Trace: {e}"
            )

    def job_get_id(self, response: Optional[requests.Response] = None) -> Optional[str]:
        response_data = response.json() if response else {}
        bulk_response = response_data.get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
        if bulk_response and bulk_response.get("status") == ShopifyBulkStatus.CREATED.value:
            job_id = bulk_response.get("id")
            if job_id:
                self.logger.info(f"The BULK Job: `{job_id}` is {ShopifyBulkStatus.CREATED.value}")
                return job_id
        else:
            return None

    def job_retry_on_concurrency(self, request: requests.Request) -> Optional[requests.Response]:
        if self.concurrent_attempt == self.concurrent_max_retry:
            # indicate we'are out of attempts to retry with job creation
            self.concurrent_max_attempt_reached = True
            self.logger.error(f"The BULK Job couldn't be created at this time, since another job is running.")
            return None
        elif self.concurrent_attempt < self.concurrent_max_retry:
            # increment attempt
            self.concurrent_attempt += 1
            # try to execute previous request, it's handy because we can retry / each slice yielded
            self.logger.warning(
                f"The BULK concurrency limit has reached. Waiting {self.concurrent_interval_sec} sec before retry, atttempt: {self.concurrent_attempt}.",
            )
            sleep(self.concurrent_interval_sec)
            # retry current `request`
            return self.job_create(request)

    def job_create(self, request: requests.Request) -> Optional[requests.Response]:
        # create the server-side job
        response = self.session.send(request)
        # when the concurrent job takes place, we typically need to wait and retry, but no longer than 10 min.
        if not self.has_running_concurrent_job(response):
            # process created job response
            return response if not self.job_check_for_errors(response) else None
        else:
            return self.job_retry_on_concurrency(request)

    def log_job_status(self, bulk_job_id: str, status: str) -> None:
        self.logger.info(f"The BULK Job: `{bulk_job_id}` is {status}.")

    def job_check_status(self, url: str, bulk_job_id: str) -> Optional[str]:
        # re-use of `self._session(*, **)` to make BULK Job status checks
        response = self.session.request(
            method="POST",
            url=url,
            data=ShopifyBulkTemplates.status(bulk_job_id),
            headers={"Content-Type": "application/graphql"},
        )
        # check for errors and status, return when COMPLETED.
        if not self.job_check_for_errors(response):
            status = response.json().get("data", {}).get("node", {}).get("status")
            if status == ShopifyBulkStatus.COMPLETED.value:
                self.log_job_status(bulk_job_id, status)
                return response.json().get("data", {}).get("node", {}).get("url")
            elif status == ShopifyBulkStatus.RUNNING.value:
                self.log_job_status(bulk_job_id, status)
                # wait for the `job_check_interval_sec` value in sec before check again.
                sleep(self.job_check_interval_sec)
                return self.job_check_status(url, bulk_job_id)
            elif status == ShopifyBulkStatus.FAILED.value:
                self.log_job_status(bulk_job_id, status)
                raise ShopifyBulkExceptions.BulkJobFailed(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, details: {self.job_check_for_errors(response)}",
                )
            elif status == ShopifyBulkStatus.TIMEOUT.value:
                self.log_job_status(bulk_job_id, status)
                raise ShopifyBulkExceptions.BulkJobTimout(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please retry the operation with smaller date range.",
                )
            elif status == ShopifyBulkStatus.ACCESS_DENIED.value:
                self.log_job_status(bulk_job_id, status)
                raise ShopifyBulkExceptions.BulkJobAccessDenied(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please check your PERMISSION to fetch the data for this stream.",
                )
            else:
                raise Exception(f"Could not validate the status of the BULK Job `{bulk_job_id}`.")

    def job_check(self, url: str, created_job_response: requests.Response) -> Optional[str]:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """
        bulk_job_id: str = self.job_get_id(created_job_response)
        if bulk_job_id:
            job_started = time()
            try:
                return self.job_check_status(url, bulk_job_id)
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
            return None

    def job_retrieve_result(self, job_result_url: str) -> str:
        # save to local file using chunks to avoid OOM
        filename = self.tools.filename_from_url(job_result_url)
        with self.session.get(job_result_url, stream=True) as response:
            response.raise_for_status()
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=self.retrieve_chunk_size):
                    file.write(chunk)
        return filename

    def job_record_producer(
        self,
        job_result_url: str,
        substream: bool = False,
        custom_transform: Callable = None,
        record_identifier: str = None,
        remove_file: bool = True,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """
        @ custom_transform:
            Example method:
            Adds the new field to the record during the processing.

            ```python
            @staticmethod
            def custom_transform(record: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
                record["MY_CUSTTOM_FIELD"] = "MY_VALUE"
                yield record
            ```
        """

        try:
            # save the content to the local file
            filename = self.job_retrieve_result(job_result_url)
            # produce records from saved result
            yield from self.record_producer.produce_records(filename, substream, record_identifier, custom_transform)
        except Exception as e:
            raise ShopifyBulkExceptions.BulkRecordProduceError(
                f"An error occured while producing records from BULK Job result. Trace: {repr(e)}.",
            )
        finally:
            # removing the tmp file, if requested
            if remove_file:
                try:
                    remove(filename)
                except Exception as e:
                    self.logger.info(f"Failed to remove the `tmp job result` file, the file doen't exist. Details: {repr(e)}.")
                    # we should pass here, if the file wasn't removed , it's either:
                    # - doesn't exist
                    # - will be dropped with the container shut down.
                    pass
