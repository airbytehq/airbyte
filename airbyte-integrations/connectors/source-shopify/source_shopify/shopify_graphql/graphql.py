#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from abc import abstractmethod
from enum import Enum
from inspect import isgeneratorfunction
from json import loads
from os import remove
from string import Template
from time import sleep, time
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import requests
import sgqlc.operation
from requests.exceptions import JSONDecodeError
from source_shopify.utils import ApiTypeEnum
from source_shopify.utils import ShopifyRateLimiter as limiter

from . import schema

_schema = schema
_schema_root = _schema.shopify_schema


# the graphql api requires the query filter to be snake case even though the column returned is camel case
def _camel_to_snake(camel_case: str):
    snake_case = []
    for char in camel_case:
        if char.isupper():
            snake_case.append("_" + char.lower())
        else:
            snake_case.append(char)
    return "".join(snake_case).lstrip("_")


class ShopifyBulkGraphQl:

    # define default logger
    logger = logging.getLogger("airbyte")

    # 5Mb chunk size to save the file
    retrieve_chunk_size = 1024 * 1024 * 5
    parent_key = "__parentId"

    class Status(Enum):
        CREATED = "CREATED"
        COMPLETED = "COMPLETED"
        RUNNING = "RUNNING"
        CANCELED = "CANCELED"
        FAILED = "FAILED"
        TIMEOUT = "TIMEOUT"
        ACCESS_DENIED = "ACCESS_DENIED"

    class Query:
        def bulk_query_status(bulk_job_id: str) -> str:
            return Template(
                """query {
                        node(id: "$job_id") {
                            ... on BulkOperation {
                                id
                                status
                                errorCode
                                objectCount
                                fileSize
                                url
                                partialDataUrl
                            }
                        }
                    }"""
            ).substitute(job_id=bulk_job_id)

        def bulk_query_prepare(query: str) -> str:
            bulk_template = Template(
                '''mutation {
                    bulkOperationRunQuery(
                        query: """
                        $query
                        """
                    ) {
                        bulkOperation {
                            id
                            status
                        }
                        userErrors {
                            field
                            message
                        }
                    }
                }'''
            )
            # format for BULK ops
            query = str("{\n" + query + "\n}")
            return bulk_template.substitute(query=query)

        class BaseIncrementalQuery:
            @property
            @abstractmethod
            def record_identifier() -> str:
                """
                Defines the record identifier to fetch only records related to the choosen stream.
                """

            @abstractmethod
            def resolve_query(query_path: Union[List[str], str], query: sgqlc.operation.Selection) -> sgqlc.operation.Selection:
                """
                Defines how query object should be resolved based on the base query selection.
                In this method any additional fields should be defined.
                """

            def build_query(query_path: Union[List[str], str], query: str = None, sort_key: str = None) -> sgqlc.operation.Selection:
                # define query root
                op = sgqlc.operation.Operation(_schema_root.query_type)

                if isinstance(query_path, list):
                    # define the query operation builder using string eval to pass the query_path from args.
                    query_builder = eval(f"op.{query_path[0]}(query=query, sort_key=sort_key)")
                    # at least 1 field should be requested for the query root object
                    query_builder.edges.node.id()
                    # if composite `query_path` contains 2 elements
                    if len(query_path) == 2:
                        # at least 1 field should be requested for the 1st-lvl of nested query
                        eval(f"query_builder.edges.node.{query_path[1]}().edges.node.id()")
                    elif len(query_path) == 3:
                        # at least 1 field should be requested for the 1st-lvl of nested query
                        eval(f"query_builder.edges.node.{query_path[1]}().edges.node.id()")
                        # at least 1 field should be requested for the 2nd-lvl of nested query
                        eval(f"query_builder.edges.node.{query_path[1]}.edges.node.{query_path[2]}().edges.node.id()")
                else:
                    # define the query operation builder using string eval to pass the query_path from args.
                    query_builder = eval(f"op.{query_path}(query=query, sort_key=sort_key)")
                    # at least 1 field should be requested for the query root object
                    query_builder.edges.node.id()

                return query_builder

            def __new__(
                self,
                query_path: Union[List[str], str],
                filter_field: str = None,
                start: str = None,
                end: str = None,
                sort_key: str = None,
            ) -> sgqlc.operation.Selection:
                # define query string
                filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'"
                # define the query structure
                query = self.build_query(query_path, filter_query, sort_key)
                # get final query as a string
                return str(self.resolve_query(query_path, query))

        class Metafields(BaseIncrementalQuery):

            record_identifier = "Metafield"

            def resolve_query(query_path: Union[List[str], str], query: sgqlc.operation.Selection) -> sgqlc.operation.Selection:
                # adding `metafields` fields to the query nodes
                if isinstance(query_path, list):
                    if len(query_path) == 2:
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.id()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.namespace()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.value()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.key()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.description()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.created_at()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.updated_at()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.metafields.edges.node.type()")
                    elif len(query_path) == 3:
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.id()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.namespace()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.value()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.key()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.description()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.created_at()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.updated_at()")
                        eval(f"query.edges.node.{query_path[1]}.edges.node.{query_path[2]}.edges.node.metafields.edges.node.type()")
                else:
                    query.edges.node.metafields()
                    query.edges.node.metafields.edges.node.id()
                    query.edges.node.metafields.edges.node.namespace()
                    query.edges.node.metafields.edges.node.value()
                    query.edges.node.metafields.edges.node.key()
                    query.edges.node.metafields.edges.node.description()
                    query.edges.node.metafields.edges.node.created_at()
                    query.edges.node.metafields.edges.node.updated_at()
                    query.edges.node.metafields.edges.node.type()

                return query

    class Tools:
        def filename_from_url(job_result_url: str) -> str:
            # Regular expression pattern to extract the filename
            filename_pattern = r'filename\*?=(?:UTF-8\'\')?"([^"]+)"'
            parsed_url = dict(parse_qsl(urlparse(job_result_url).query))
            return re.search(filename_pattern, parsed_url.get("response-content-disposition")).group(1)

        def record_fields_to_snake_case(record: Mapping[str, Any]) -> Mapping[str, Any]:
            # transforming record field names from camel to snake case,
            # leaving the `__parent_id` relation in place.
            return {_camel_to_snake(k) if k != ShopifyBulkGraphQl.parent_key else k: v for k, v in record.items()}

        def record_resolve_id(record: Mapping[str, Any]) -> Mapping[str, Any]:
            """
            The ids are fetched in the format of: " gid://shopify/Order/<Id> "
            Input:
                { "Id": "gid://shopify/Order/19435458986123"}
            We need to extract the actual id from the string instead.
            Output:
                { "id": 19435458986123, "admin_graphql_api_id": "gid://shopify/Order/19435458986123"}
            """
            # save the actual api id to the `admin_graphql_api_id`
            record["admin_graphql_api_id"] = record["id"]
            # extracting the int(id) and reassign
            record["id"] = int(re.search(r"\d+", record.get("id")).group())
            return record

        def resolve_substream(record: Mapping[str, Any], record_identifier: str = None) -> Mapping[str, Any]:
            # return records based on `record_identifier` filter.
            if record_identifier:
                return record if record_identifier in record.get("admin_graphql_api_id") else None
            else:
                # return records related to substream, by checking for the `__parentId` field
                # more info: https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
                return record if ShopifyBulkGraphQl.parent_key in record.keys() else None

        def resolve_with_custom_transformer(record: Mapping[str, Any], custom_transform: Callable) -> Iterable[Mapping[str, Any]]:
            if isgeneratorfunction(custom_transform):
                yield from custom_transform(record)
            else:
                yield custom_transform(record)

        def record_resolver(
            record: Mapping[str, Any],
            substream: bool = False,
            record_identifier: str = None,
            custom_transform: Callable = None,
        ) -> Iterable[Mapping[str, Any]]:
            # resolve the id to int
            record = ShopifyBulkGraphQl.Tools.record_resolve_id(record)
            # the substream_record is `None`, when parent record takes place
            substream_record = ShopifyBulkGraphQl.Tools.resolve_substream(record, record_identifier)

            # resolution
            if custom_transform and substream:
                # process substream with external function, if passed
                if substream_record:
                    yield from ShopifyBulkGraphQl.Tools.resolve_with_custom_transformer(substream_record, custom_transform)
            elif custom_transform and not substream:
                # process record with external function, if passed
                yield from ShopifyBulkGraphQl.Tools.resolve_with_custom_transformer(record, custom_transform)
            elif not custom_transform and substream:
                # yield substream record as is
                if substream_record:
                    yield substream_record
            else:
                # yield as is otherwise
                yield record

        def record_producer(
            filename: str,
            substream: bool = False,
            record_identifier: str = None,
            custom_transform: Callable = None,
        ) -> Union[Iterable[Mapping[str, Any]], Mapping[str, Any]]:
            # reading from local file line-by-line to avoid OOM
            with open(filename, "r") as jsonl_file:
                for line in jsonl_file:
                    # transforming record field names from camel to snake case
                    record = ShopifyBulkGraphQl.Tools.record_fields_to_snake_case(loads(line))
                    # resolve record
                    yield from ShopifyBulkGraphQl.Tools.record_resolver(record, substream, record_identifier, custom_transform)

    class Exceptions:
        class BaseBulkException(Exception):
            def __init__(self, message: str):
                super().__init__(message)

        class BulkJobError(BaseBulkException):
            """Raised when there are BULK Job Errors in response"""

        class BulkJobUnknownError(BaseBulkException):
            """Raised when BULK Job has FAILED with Unknown status"""

        class BulkJobBadResponse(BaseBulkException):
            """Raised when the requests.Response object could not be parsed"""

        class BulkRecordProduceError(BaseBulkException):
            """Raised when there are error producing records from BULK Job result"""

        class BulkJobFailed(BaseBulkException):
            """Raised when BULK Job has FAILED status"""

        class BulkJobTimout(BaseBulkException):
            """Raised when BULK Job has TIMEOUT status"""

        class BulkJobAccessDenied(BaseBulkException):
            """Raised when BULK Job has ACCESS_DENIED status"""

    def bulk_job_create(self, session: requests.Session, request: requests.Request) -> str:
        # create the server-side job
        response = session.send(request)
        # process created job response
        if not self.bulk_job_check_for_errors(response):
            response_data = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("bulkOperation", {})
            if response_data.get("status") == self.Status.CREATED.value:
                job_id = response_data.get("id")
                self.logger.info(f"The BULK Job: `{job_id}` is {self.Status.CREATED.value}")
                return job_id

    @limiter.balance_rate_limit(api_type=ApiTypeEnum.graphql.value)
    def bulk_job_check_for_errors(self, response: requests.Response) -> Optional[bool]:
        try:
            errors_in_response = response.json().get("data", {}).get("bulkOperationRunQuery", {}).get("userErrors", [])
            if errors_in_response:
                raise self.Exceptions.BulkJobError(f"Something wong with the BULK job, errors: {errors_in_response}")
        except JSONDecodeError as e:
            raise self.Exceptions.BulkJobBadResponse(
                f"The BULK Job result contains errors or could not be parsed. Details: {response.text}. Trace: {e}"
            )

    def bulk_job_emit_status(self, bulk_job_id: str, status: str) -> None:
        self.logger.info(f"The BULK Job: `{bulk_job_id}` is {status}.")

    def bulk_job_check_status(self, session: requests.Session, url: str, bulk_job_id: str, check_interval_sec: int = 5) -> Optional[str]:
        # re-use of `self._session(*, **)` to make BULK Job status checks
        response = session.request(
            method="POST",
            url=url,
            data=self.Query.bulk_query_status(bulk_job_id),
            headers={"Content-Type": "application/graphql"},
        )
        # check for errors and status, return when COMPLETED.
        if not self.bulk_job_check_for_errors(response):
            status = response.json().get("data", {}).get("node", {}).get("status")
            if status == self.Status.COMPLETED.value:
                self.bulk_job_emit_status(bulk_job_id, status)
                return response.json().get("data", {}).get("node", {}).get("url")
            elif status == self.Status.FAILED.value:
                self.bulk_job_emit_status(bulk_job_id, status)
                raise self.Exceptions.BulkJobFailed(
                    f"The BULK Job: `bulk_job_id` failed to execute, details: {self.bulk_job_check_for_errors(response)}",
                )
            elif status == self.Status.TIMEOUT.value:
                raise self.Exceptions.BulkJobTimout(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please retry the operation with smaller date range.",
                )
            elif status == self.Status.ACCESS_DENIED.value:
                raise self.Exceptions.BulkJobAccessDenied(
                    f"The BULK Job: `{bulk_job_id}` exited with {status}, please check your PERMISSION to fetch the data for the `{self.name}` stream.",
                )
            else:
                self.bulk_job_emit_status(bulk_job_id, status)
                # wait for the `check_interval_sec` value in sec before check again.
                sleep(check_interval_sec)
                return self.bulk_job_check_status(session, url, bulk_job_id)

    def bulk_job_check(self, session: requests.Session, url: str, bulk_job_id: str) -> str:
        """
        This method checks the status for the BULK Job created, using it's `ID`.
        The time spent for the Job execution is tracked to understand the effort.
        """
        if bulk_job_id:
            job_started = time()
            try:
                return self.bulk_job_check_status(session, url, bulk_job_id)
            except Exception as e:
                raise self.Exceptions.BulkJobUnknownError(f"The BULK Job: `{bulk_job_id}` has unknown status. Trace: {repr(e)}.")
            finally:
                time_elapsed = round((time() - job_started), 3)
                self.logger.info(f"The BULK Job: `{bulk_job_id}` time elapsed: {time_elapsed} sec.")

    def bulk_job_retrieve_result(self, job_result_url: str) -> str:
        # save to local file using chunks to avoid OOM
        filename = self.Tools.filename_from_url(job_result_url)
        with requests.get(job_result_url, stream=True) as response:
            response.raise_for_status()
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=ShopifyBulkGraphQl.retrieve_chunk_size):
                    file.write(chunk)
        return filename

    def bulk_job_records_producer(
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
            filename = self.bulk_job_retrieve_result(job_result_url)
            # produce records from saved result
            yield from self.Tools.record_producer(filename, substream, record_identifier, custom_transform)
        except Exception as e:
            raise self.Exceptions.BulkRecordProduceError(
                f"An error occured while producing records from BULK Job result. Trace: {repr(e)}.",
            )
        finally:
            if remove_file:
                # removing the tmp file
                remove(filename)


def get_query_products(first: int, filter_field: str, filter_value: str, next_page_token: Optional[str]):
    op = sgqlc.operation.Operation(_schema_root.query_type)
    snake_case_filter_field = _camel_to_snake(filter_field)
    if next_page_token:
        products = op.products(first=first, query=f"{snake_case_filter_field}:>'{filter_value}'", after=next_page_token)
    else:
        products = op.products(first=first, query=f"{snake_case_filter_field}:>'{filter_value}'")
    products.nodes.id()
    products.nodes.title()
    products.nodes.updated_at()
    products.nodes.created_at()
    products.nodes.published_at()
    products.nodes.status()
    products.nodes.vendor()
    products.nodes.product_type()
    products.nodes.tags()
    products.nodes.options()
    products.nodes.options().id()
    products.nodes.options().name()
    products.nodes.options().position()
    products.nodes.options().values()
    products.nodes.handle()
    products.nodes.description()
    products.nodes.tracks_inventory()
    products.nodes.total_inventory()
    products.nodes.total_variants()
    products.nodes.online_store_url()
    products.nodes.online_store_preview_url()
    products.nodes.description_html()
    products.nodes.is_gift_card()
    products.nodes.legacy_resource_id()
    products.nodes.media_count()
    products.page_info()
    products.page_info.has_next_page()
    products.page_info.end_cursor()
    return str(op)
