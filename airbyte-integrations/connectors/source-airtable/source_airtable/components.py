# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, MutableMapping

import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from source_airtable.schema_helpers import SchemaHelpers


class FieldsExtractor(DpathExtractor):
    def extract_records(
        self,
        response: requests.Response,
    ) -> Iterable[MutableMapping[Any, Any]]:
        for record in super().extract_records(response):

            updated_record = {
                "_airtable_id": record["id"],
                "_airtable_created_time": record["createdTime"],
                # this field will be updated by transformations, only used by DynamicSchemaLoader to identify proper schema
                "_airtable_table_name": "",
                **{SchemaHelpers.clean_name(k): v for k, v in record["fields"].items()},
            }

            yield updated_record
