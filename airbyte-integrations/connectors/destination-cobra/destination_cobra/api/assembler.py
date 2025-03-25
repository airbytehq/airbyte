# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from copy import deepcopy
from functools import cache
from typing import Any, Dict, Optional

from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.utils.datetime_helpers import ab_datetime_format, ab_datetime_try_parse


class SalesforceRecordAssembler:
    def __init__(self, http_client: HttpClient, url_base: str) -> None:
        self._http_client = http_client
        self._url_base = url_base

    def assemble(self, sf_object: str, record: Dict[str, Any]) -> Dict[str, Any]:
        # Note that we assemble here even if the record only has the field `Id` which is the case for the delete operation.
        # The drawback seems to be minimal though i.e. that we do one API call to get the field types for the object.
        type_by_field = self._get_type_by_field(sf_object)

        sf_record = deepcopy(record)
        fields_to_normalize = {field for field in record.keys() if type_by_field.get(field) in ["date", "datetime"]}
        if fields_to_normalize:
            for field in fields_to_normalize:
                sf_record[field] = self._normalize_field(sf_record[field], type_by_field[field])
        return sf_record

    @cache
    def _get_type_by_field(self, sf_object: str) -> Dict[str, str]:
        _, response = self._http_client.send_request(
            http_method="GET",
            url=f"{self._url_base}/services/data/v62.0/sobjects/{sf_object}/describe/",
            request_kwargs={},
        )
        if response.status_code == 200:
            return {field["name"]: field["type"] for field in response.json()["fields"]}

    def _normalize_field(self, value: Optional[str], _type: str) -> str:
        if value is None:
            return None

        airbyte_datetime = ab_datetime_try_parse(value)
        if airbyte_datetime is None:
            raise ValueError(f"Value {value} could not be parsed as type {_type}")

        if _type == "date":
            return airbyte_datetime.to_datetime().strftime("%Y-%m-%d")
        elif _type == "datetime":
            return airbyte_datetime.to_datetime().isoformat(timespec="milliseconds")
        else:
            raise ValueError(f"Type {_type} is not supported")
