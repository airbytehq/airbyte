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

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def job_check_for_errors(self, response: requests.Response) -> Optional[bool]:
        try:
            errors_in_response = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get(
                "userErrors", []
            ) or response.json().get("errors")
            if errors_in_response:
                raise ShopifyBulkExceptions.BulkJobError(f"Something wong with the BULK job, errors: {errors_in_response}")
        except JSONDecodeError as e:
            raise ShopifyBulkExceptions.BulkJobBadResponse(
                f"The BULK Job result contains errors or could not be parsed. Details: {response.text}. Trace: {e}"
            )

    def job_create(self, request: requests.Request) -> str:
        # create the server-side job
        response = self.session.send(request)
        # process created job response
        if not self.job_check_for_errors(response):
            response_data = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
            if response_data.get("status") == ShopifyBulkStatus.CREATED.value:
                job_id = response_data.get("id")
                self.logger.info(f"The BULK Job: `{job_id}` is {ShopifyBulkStatus.CREATED.value}")
                return job_id

    def job_emit_status(self, bulk_job_id: str, status: str) -> None:
        self.logger.info(f"The BULK Job: `{bulk_job_id}` is {status}.")

    def job_check_status(self, url: str, bulk_job_id: str, check_interval_sec: int = 5) -> Optional[str]:
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
                self.job_emit_status(bulk_job_id, status)
                return response.json().get("data", {}).get("node", {}).get("url")
            elif status == ShopifyBulkStatus.FAILED.value:
                self.job_emit_status(bulk_job_id, status)
                raise ShopifyBulkExceptions.BulkJobFailed(
                    f"The BULK Job: `{bulk_job_id}` failed to execute, details: {self.job_check_for_errors(response)}",
                )
            elif status == ShopifyBulkStatus.TIMEOUT.value:
                raise ShopifyBulkExceptions.BulkJobTimout(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please retry the operation with smaller date range.",
                )
            elif status == ShopifyBulkStatus.ACCESS_DENIED.value:
                raise ShopifyBulkExceptions.BulkJobAccessDenied(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please check your PERMISSION to fetch the data for the `{self.name}` stream.",
                )
            else:
                self.job_emit_status(bulk_job_id, status)
                # wait for the `check_interval_sec` value in sec before check again.
                sleep(check_interval_sec)
                return self.job_check_status(url, bulk_job_id)

    def job_check(self, url: str, bulk_job_id: str) -> str:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """
        if bulk_job_id:
            job_started = time()
            try:
                return self.job_check_status(url, bulk_job_id)
            except Exception as e:
                raise ShopifyBulkExceptions.BulkJobUnknownError(f"The BULK Job: `{bulk_job_id}` has unknown status. Trace: {repr(e)}.")
            finally:
                time_elapsed = round((time() - job_started), 3)
                self.logger.info(f"The BULK Job: `{bulk_job_id}` time elapsed: {time_elapsed} sec.")

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
                remove(filename)
