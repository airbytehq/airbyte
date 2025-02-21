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
        included_relations = list(self.extract_records_by_path(response, ["included"]))

        # Update target records with included records
        updated_records = self.update_target_records_with_included(target_records, included_relations)
        yield from updated_records

    @staticmethod
    def update_target_records_with_included(
        target_records: Iterable[Mapping[str, Any]], included_relations: Iterable[Mapping[str, Any]]
    ) -> Iterable[Mapping[str, Any]]:
        for target_record in target_records:
            target_relationships = target_record.get("relationships", {})

            for included_relation in included_relations:
                included_relation_attributes = included_relation.get("attributes", {})
                included_relation_type = included_relation["type"]
                included_relation_id = included_relation["id"]

                target_relationship_id = target_relationships.get(included_relation_type, {}).get("data", {}).get("id")

                if included_relation_id == target_relationship_id:
                    target_relationships[included_relation_type]["data"].update(included_relation_attributes)

            yield target_record

    def extract_records_by_path(self, response: requests.Response, field_paths: list = None) -> Iterable[Mapping[str, Any]]:
        try:
            response_body = response.json()
        except Exception as e:
            raise Exception(f"Failed to parse response body as JSON: {e}")

        # Extract data from the response body based on the provided field paths
        if not field_paths:
            extracted_data = response_body
        else:
            field_path_str = "/".join(field_paths)  # Convert list of field paths to a single string path for dpath
            if "*" in field_path_str:
                extracted_data = dpath.values(response_body, field_path_str)
            else:
                extracted_data = dpath.get(response_body, field_path_str, default=[])

        # Yield extracted data as individual records
        if isinstance(extracted_data, list):
            yield from extracted_data
        elif extracted_data:
            yield extracted_data
        else:
            yield from []
