#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from dataclasses import dataclass, field
from io import TextIOWrapper
from json import loads
from os import remove
from typing import Any, Callable, Final, Iterable, List, Mapping, MutableMapping, Optional, Union

from .exceptions import ShopifyBulkExceptions
from .query import ShopifyBulkQuery
from .tools import END_OF_FILE, BulkTools


@dataclass
class ShopifyBulkRecord:
    query: ShopifyBulkQuery

    # default buffer
    buffer: List[MutableMapping[str, Any]] = field(init=False, default_factory=list)

    # default logger
    logger: Final[logging.Logger] = logging.getLogger("airbyte")

    def __post_init__(self) -> None:
        self.composition: Optional[Mapping[str, Any]] = self.query.record_composition
        self.record_process_components: Optional[Callable[[MutableMapping], MutableMapping]] = self.query.record_process_components
        self.components: List[str] = self.composition.get("record_components", []) if self.composition else []
        # how many records composed
        self.record_composed: int = 0

    @property
    def tools(self) -> BulkTools:
        return BulkTools()

    @staticmethod
    def check_type(record: Mapping[str, Any], types: Union[List[str], str]) -> bool:
        record_type = record.get("__typename")
        if isinstance(types, list):
            return any(record_type == t for t in types)
        else:
            return record_type == types

    def record_new(self, record: MutableMapping[str, Any]) -> None:
        record = self.component_prepare(record)
        record.pop("__typename")
        self.buffer.append(record)

    def record_new_component(self, record: MutableMapping[str, Any]) -> None:
        component = record.get("__typename")
        record.pop("__typename")
        # add component to its placeholder in the components list
        self.buffer[-1]["record_components"][component].append(record)

    def component_prepare(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if self.components:
            record["record_components"] = {}
            for component in self.components:
                record["record_components"][component] = []
        return record

    def buffer_flush(self) -> Iterable[Mapping[str, Any]]:
        if len(self.buffer) > 0:
            for record in self.buffer:
                # resolve id from `str` to `int`
                record = self.record_resolve_id(record)
                # process record components
                yield from self.record_process_components(record)
            # clean the buffer
            self.buffer.clear()

    def record_compose(self, record: Mapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Step 1: register the new record by it's `__typename`
        Step 2: check for `components` by their `__typename` and add to the placeholder
        Step 3: repeat until the `<END_OF_FILE>`.
        """
        if self.check_type(record, self.composition.get("new_record")):
            # emit from previous iteration, if present
            yield from self.buffer_flush()
            # register the record
            self.record_new(record)
        # components check
        elif self.check_type(record, self.components):
            self.record_new_component(record)

    def process_line(self, jsonl_file: TextIOWrapper) -> Iterable[MutableMapping[str, Any]]:
        # process the json lines
        for line in jsonl_file:
            # we exit from the loop when receive <end_of_file> (file ends)
            if line == END_OF_FILE:
                break
            elif line != "":
                yield from self.record_compose(loads(line))

        # emit what's left in the buffer, typically last record
        yield from self.buffer_flush()

    def record_resolve_id(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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
        # IF NOT `id` field is provided by the query results, we should return composed record `as is`.
        id = record.get("id")
        if id and isinstance(id, str):
            record["admin_graphql_api_id"] = id
            # extracting the int(id) and reassign
            record["id"] = self.tools.resolve_str_id(id)
        return record

    def produce_records(self, filename: str) -> Iterable[MutableMapping[str, Any]]:
        """
        Read the JSONL content saved from `job.job_retrieve_result()` line-by-line to avoid OOM.
        The filename example: `bulk-4039263649981.jsonl`,
            where `4039263649981` is the `id` of the COMPLETED BULK Jobw with `result_url`.
            Note: typically the `filename` is taken from the `result_url` string provided in the response.
        """

        with open(filename, "r") as jsonl_file:
            # reset the counter
            self.record_composed = 0

            for record in self.process_line(jsonl_file):
                yield self.tools.fields_names_to_snake_case(record)
                self.record_composed += 1

    def read_file(self, filename: str, remove_file: Optional[bool] = True) -> Iterable[Mapping[str, Any]]:
        try:
            # produce records from saved result
            yield from self.produce_records(filename)
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
