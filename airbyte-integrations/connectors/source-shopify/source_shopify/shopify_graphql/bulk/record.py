#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re
from inspect import isgeneratorfunction
from io import TextIOWrapper
from json import loads
from typing import Any, Callable, Iterable, List, Mapping, Optional

from .query import BULK_PARENT_KEY
from .tools import BulkTools


class ShopifyBulkRecord:
    def __init__(self, custom_reader: Callable = None) -> None:
        self.tools: BulkTools = BulkTools()
        # set custom reader, if initialized
        self.record_reader: Callable = custom_reader if custom_reader else self.default_reader

    def default_reader(self, jsonl_file: TextIOWrapper) -> Iterable[Mapping[str, Any]]:
        # default record reader generator
        yield from [loads(line) for line in jsonl_file]

    @staticmethod
    def check_type(record: Optional[Mapping[str, Any]] = None, type: Optional[str] = None) -> bool:
        if record:
            return True if record["__typename"] == type else False
        else:
            return False

    @staticmethod
    def emit_collected(buffer: Optional[List[Mapping[str, Any]]] = []) -> Iterable[Mapping[str, Any]]:
        if len(buffer) > 0:
            for record in buffer:
                yield record

    # @staticmethod
    def record_resolve_id(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        The ids are fetched in the format of: " gid://shopify/Order/<Id> "
        Input:
            { "Id": "gid://shopify/Order/19435458986123"}
        We need to extract the actual id from the string instead.
        Output:
            { "id": 19435458986123, "admin_graphql_api_id": "gid://shopify/Order/19435458986123"}
        """
        # save the actual api id to the `admin_graphql_api_id`
        # while resolving the `id` in `record_resolve_id`,
        # we re-assign the original id like `"gid://shopify/Order/19435458986123"`,
        # into `admin_graphql_api_id` have the ability to identify the record oigin correctly in subsequent actions.
        record["admin_graphql_api_id"] = record["id"]
        # extracting the int(id) and reassign
        record["id"] = self.tools.resolve_str_id(record.get("id"))
        return record

    @staticmethod
    def resolve_substream(record: Mapping[str, Any], record_identifier: Optional[str] = None) -> Optional[Mapping[str, Any]]:
        # return records based on `record_identifier` filter.
        if record_identifier:
            # resolving record by it's identifier, saved in `record_reesolve_id` method.
            return record if record_identifier in record.get("admin_graphql_api_id", "") else None
        else:
            # return records related to substream, by checking for the `__parentId` field
            # more info: https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
            return record if BULK_PARENT_KEY in record.keys() else None

    @staticmethod
    def resolve_with_custom_transformer(record: Mapping[str, Any], custom_transform: Callable) -> Iterable[Mapping[str, Any]]:
        if isgeneratorfunction(custom_transform):
            yield from custom_transform(record)
        else:
            yield custom_transform(record)

    def record_resolver(
        self,
        record: Mapping[str, Any],
        substream: Optional[bool] = False,
        record_identifier: Optional[str] = None,
        custom_transform: Optional[Callable] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # transforming record field names from camel to snake case
        # resolve the id to int
        record = self.record_resolve_id(self.tools.fields_names_to_snake_case(record))
        # the substream_record is `None`, when parent record takes place
        substream_record = self.resolve_substream(record, record_identifier)

        # resolution
        if custom_transform and substream:
            # process substream with external function, if passed
            if substream_record:
                yield from self.resolve_with_custom_transformer(substream_record, custom_transform)
        elif custom_transform and not substream:
            # process record with external function, if passed
            yield from self.resolve_with_custom_transformer(record, custom_transform)
        elif not custom_transform and substream:
            # yield substream record as is
            if substream_record:
                yield substream_record
        else:
            # yield as is otherwise
            yield record

    def produce_records(
        self,
        filename: str,
        substream: Optional[bool] = False,
        record_identifier: Optional[str] = None,
        custom_transform: Optional[Callable] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Read the JSONL content saved from `job.job_retrieve_result()` line-by-line to avoid OOM.
        The filename example: `bulk-4039263649981.jsonl`,
            where `4039263649981` is the `id` of the COMPLETED BULK Jobw with `result_url`.
            Note: typically the `filename` is taken from the `result_url` string provided in the response.
        """

        with open(filename, "r") as jsonl_file:
            for record in self.record_reader(jsonl_file):
                yield from self.record_resolver(record, substream, record_identifier, custom_transform)
