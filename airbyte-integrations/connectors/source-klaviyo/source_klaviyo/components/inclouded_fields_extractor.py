#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import dpath
import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor


@dataclass
class KlaviyoIncludedFieldExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        # Evaluate and retrieve the extraction paths
        evaluated_field_paths = [field_path.eval(self.config) for field_path in self._field_path]
        target_records = self.extract_records_by_path(response, evaluated_field_paths)
        included_records = self.extract_records_by_path(response, ["included"])

        # Update target records with included records
        updated_records = self.update_target_records_with_included(target_records, included_records)
        yield from updated_records

    @staticmethod
    def update_target_records_with_included(
        target_records: Iterable[Mapping[str, Any]], included_records: Iterable[Mapping[str, Any]]
    ) -> Iterable[Mapping[str, Any]]:
        for included_record in included_records:
            included_attributes = included_record.get("attributes", {})
            for target_record in target_records:
                target_relationships = target_record.get("relationships", {})
                included_record_type = included_record["type"]
                if included_record_type in target_relationships:
                    target_relationships[included_record_type]["data"].update(included_attributes)
                yield target_record

    def extract_records_by_path(self, response: requests.Response, field_paths: list = None) -> Iterable[Mapping[str, Any]]:
        response_body = self.decoder.decode(response)

        # Extract data from the response body based on the provided field paths
        if not field_paths:
            extracted_data = response_body
        else:
            field_path_str = "/".join(field_paths)  # Convert list of field paths to a single string path for dpath
            if "*" in field_path_str:
                extracted_data = dpath.util.values(response_body, field_path_str)
            else:
                extracted_data = dpath.util.get(response_body, field_path_str, default=[])

        # Yield extracted data as individual records
        if isinstance(extracted_data, list):
            yield from extracted_data
        elif extracted_data:
            yield extracted_data
        else:
            yield from []
