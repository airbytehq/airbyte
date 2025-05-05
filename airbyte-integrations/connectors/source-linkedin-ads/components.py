#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import urlencode

import requests
from requests.exceptions import InvalidURL

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_parse


# replace `pivot` with `_pivot`, to allow redshift normalization,
# since `pivot` is a reserved keyword for Destination Redshift,
# on behalf of https://github.com/airbytehq/airbyte/issues/13018,
# expand this list, if required.
DESTINATION_RESERVED_KEYWORDS: list = ["pivot"]


class SafeHttpClient(HttpClient):
    """
    A custom HTTP client that safely validates query parameters, ensuring that the symbols ():,% are preserved
    during UTF-8 encoding.
    """

    def _create_prepared_request(
        self,
        http_method: str,
        url: str,
        dedupe_query_params: bool = False,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ) -> requests.PreparedRequest:
        """
        Prepares an HTTP request with optional deduplication of query parameters and safe encoding.
        """
        if dedupe_query_params:
            query_params = self._dedupe_query_params(url, params)
        else:
            query_params = params or {}
        query_params = urlencode(query_params, safe="():,%")
        args = {"method": http_method, "url": url, "headers": headers, "params": query_params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data
        prepared_request: requests.PreparedRequest = self._session.prepare_request(requests.Request(**args))

        return prepared_request


@dataclass
class SafeEncodeHttpRequester(HttpRequester):
    """
    A custom HTTP requester that ensures safe encoding of query parameters, preserving the symbols ():,% during UTF-8 encoding.
    """

    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None
    query_properties_key: Optional[str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """
        Initializes the request options provider with the provided parameters and any
        configured request components like headers, parameters, or bodies.
        """
        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
            request_headers=self.request_headers,
            request_parameters=self.request_parameters,
            query_properties_key=self.query_properties_key,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies
        else:
            backoff_strategies = None

        self._http_client = SafeHttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )


@dataclass
class LinkedInAdsRecordExtractor(RecordExtractor):
    """
    Extracts and transforms LinkedIn Ads records, ensuring that 'lastModified' and 'created'
    date-time fields are formatted to RFC3339.
    """

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Converts 'lastModified' and 'created' fields in the record to RFC3339 format.
        """
        for item in ["lastModified", "created"]:
            if record.get(item) is not None:
                record[item] = ab_datetime_parse(record[item]).to_datetime().isoformat()
        return record

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """
        Extracts and transforms records from an HTTP response.
        """
        for record in transform_data(response.json().get("elements")):
            yield self._date_time_to_rfc3339(record)


@dataclass
class LinkedInAdsErrorHandler(DefaultErrorHandler):
    """
    An error handler for LinkedIn Ads that interprets responses, providing custom error resolutions
    for specific exceptions like `InvalidURL`.
    This is a temporary workaround untill we update this in the CDK. https://github.com/airbytehq/airbyte-internal-issues/issues/11320
    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        """
        Interprets responses and exceptions, providing custom error resolutions for specific exceptions.
        """
        if isinstance(response_or_exception, InvalidURL):
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="source-linkedin-ads has faced a temporary DNS resolution issue. Retrying...",
            )
        return super().interpret_response(response_or_exception)


def transform_change_audit_stamps(
    record: Dict, dict_key: str = "changeAuditStamps", props: List = ["created", "lastModified"], fields: List = ["time"]
) -> Mapping[str, Any]:
    """
    :: EXAMPLE `changeAuditStamps` input structure:
        {
            "changeAuditStamps": {
                "created": {"time": 1629581275000},
                "lastModified": {"time": 1629664544760}
            }
        }
    :: EXAMPLE output:
        {
            "created": "2021-08-21 21:27:55",
            "lastModified": "2021-08-22 20:35:44"
        }
    """

    target_dict: Dict = record.get(dict_key)
    for prop in props:
        # Update dict with flatten key:value
        for field in fields:
            record[prop] = ab_datetime_parse(target_dict.get(prop).get(field) // 1000).to_datetime().strftime("%Y-%m-%d %H:%M:%S")
    record.pop(dict_key)

    return record


def date_str_from_date_range(record: Dict, prefix: str) -> str:
    """
    Makes the ISO8601 format date string from the input <prefix>.<part of the date>
    EXAMPLE:
        Input: record
        {
            "start.year": 2021, "start.month": 8, "start.day": 1,
            "end.year": 2021, "end.month": 9, "end.day": 31
        }
    EXAMPLE output:
        With `prefix` = "start"
            str:  "2021-08-13",
        With `prefix` = "end"
            str: "2021-09-31",
    """

    year = record.get(f"{prefix}.year")
    month = record.get(f"{prefix}.month")
    day = record.get(f"{prefix}.day")
    return AirbyteDateTime(year, month, day).to_datetime().strftime("%Y-%m-%d")


def transform_date_range(
    record: Dict,
    dict_key: str = "dateRange",
    props: List = ["start", "end"],
    fields: List = ["year", "month", "day"],
) -> Mapping[str, Any]:
    """
    :: EXAMPLE `dateRange` input structure in Analytics streams:
        {
            "dateRange": {
                "start": {"month": 8, "day": 13, "year": 2021},
                "end": {"month": 8, "day": 13, "year": 2021}
            }
        }
    :: EXAMPLE output:
        {
            "start_date": "2021-08-13",
            "end_date": "2021-08-13"
        }
    """
    # define list of tmp keys for cleanup.
    keys_to_remove = [dict_key, "start.day", "start.month", "start.year", "end.day", "end.month", "end.year", "start", "end"]

    target_dict: Dict = record.get(dict_key)
    for prop in props:
        # Update dict with flatten key:value
        for field in fields:
            record.update(**{f"{prop}.{field}": target_dict.get(prop).get(field)})
    # We build `start_date` & `end_date` fields from nested structure.
    record.update(**{"start_date": date_str_from_date_range(record, "start"), "end_date": date_str_from_date_range(record, "end")})
    # Cleanup tmp fields & nested used parts
    for key in keys_to_remove:
        if key in record:
            record.pop(key)
    return record


def transform_targeting_criteria(record: Dict, dict_key: str = "targetingCriteria") -> Mapping[str, Any]:
    """
        :: EXAMPLE `targetingCriteria` input structure:
            {
                "targetingCriteria": {
                    "include": {
                        "and": [
                            {
                                "or": {
                                    "urn:li:adTargetingFacet:titles": [
                                        "urn:li:title:100",
                                        "urn:li:title:10326",
                                        "urn:li:title:10457",
                                        "urn:li:title:10738",
                                        "urn:li:title:10966",
                                        "urn:li:title:11349",
                                        "urn:li:title:1159",
    ]
                                }
                            },
                            {"or": {"urn:li:adTargetingFacet:locations": ["urn:li:geo:103644278"]}},
                            {"or": {"urn:li:adTargetingFacet:interfaceLocales": ["urn:li:locale:en_US"]}},
                        ]
                    },
                    "exclude": {
                        "or": {
                            "urn:li:adTargetingFacet:facet_Key1": [
                                "facet_test1",
                                "facet_test2",
                            ],
                            "urn:li:adTargetingFacet:facet_Key2": [
                                "facet_test3",
                                "facet_test4",
                            ],
                    }
                }
            }
        :: EXAMPLE output:
            {
                "targetingCriteria": {
                    "include": {
                        "and": [
                            {
                                "type": "urn:li:adTargetingFacet:titles",
                                "values": [
                                    "urn:li:title:100",
                                    "urn:li:title:10326",
                                    "urn:li:title:10457",
                                    "urn:li:title:10738",
                                    "urn:li:title:10966",
                                    "urn:li:title:11349",
                                    "urn:li:title:1159",
                                ],
                            },
                            {
                                "type": "urn:li:adTargetingFacet:locations",
                                "values": ["urn:li:geo:103644278"],
                            },
                            {
                                "type": "urn:li:adTargetingFacet:interfaceLocales",
                                "values": ["urn:li:locale:en_US"],
                            },
                        ]
                    },
                    "exclude": {
                        "or": [
                            {
                                "type": "urn:li:adTargetingFacet:facet_Key1",
                                "values": ["facet_test1", "facet_test2"],
                            },
                            {
                                "type": "urn:li:adTargetingFacet:facet_Key2",
                                "values": ["facet_test3", "facet_test4"],
                            },
                        ]
                    },
                }
    """

    def unnest_dict(nested_dict: Dict) -> Iterable[Dict]:
        """
        Unnest the nested dict to simplify the normalization
        EXAMPLE OUTPUT:
            [
                {"type": "some_key", "values": "some_values"},
                ...,
                {"type": "some_other_key", "values": "some_other_values"}
            ]
        """

        for key, value in nested_dict.items():
            values = []
            if isinstance(value, List):
                if len(value) > 0:
                    if isinstance(value[0], str):
                        values = value
                    elif isinstance(value[0], Dict):
                        for v in value:
                            values.append(v)
            elif isinstance(value, Dict):
                values.append(value)
            yield {"type": key, "values": values}

    # get the target dict from record
    targeting_criteria = record.get(dict_key)

    # transform `include`
    if "include" in targeting_criteria:
        and_list = targeting_criteria.get("include").get("and")
        updated_include = {"and": []}
        for k in and_list:
            or_dict = k.get("or")
            for j in unnest_dict(or_dict):
                updated_include["and"].append(j)
        # Replace the original 'and' with updated_include
        record["targetingCriteria"]["include"] = updated_include

    # transform `exclude` if present
    if "exclude" in targeting_criteria:
        or_dict = targeting_criteria.get("exclude").get("or")
        updated_exclude = {"or": []}
        for k in unnest_dict(or_dict):
            updated_exclude["or"].append(k)
        # Replace the original 'or' with updated_exclude
        record["targetingCriteria"]["exclude"] = updated_exclude

    return record


def transform_variables(record: Dict, dict_key: str = "variables") -> Mapping[str, Any]:
    """
    :: EXAMPLE `variables` input:
    {
        "variables": {
            "data": {
                "com.linkedin.ads.SponsoredUpdateCreativeVariables": {
                    "activity": "urn:li:activity:1234",
                    "directSponsoredContent": 0,
                    "share": "urn:li:share:1234",
                }
            }
        }
    }
    :: EXAMPLE output:
    {
        "variables": {
            "type": "com.linkedin.ads.SponsoredUpdateCreativeVariables",
            "values": [
                {"key": "activity", "value": "urn:li:activity:1234"},
                {"key": "directSponsoredContent", "value": 0},
                {"key": "share", "value": "urn:li:share:1234"},
            ],
        }
    }
    """

    variables = record.get(dict_key).get("data")
    for key, params in variables.items():
        record["variables"]["type"] = key
        record["variables"]["values"] = []
        for key, value in params.items():
            # convert various datatypes of values into the string
            record["variables"]["values"].append({"key": key, "value": json.dumps(value, ensure_ascii=True)})
        # Clean the nested structure
        record["variables"].pop("data")
    return record


def transform_col_names(record: Dict, dict_keys: list = []) -> Mapping[str, Any]:
    """
    Rename records keys (columns) indicated in `dict_keys` to avoid normalization issues for certain destinations.
    Example:
        The `pivot` or `PIVOT` is the reserved keyword for DESTINATION REDSHIFT, we should avoid using it in this case.
        https://github.com/airbytehq/airbyte/issues/13018
    """
    for key in dict_keys:
        if key in record:
            record[f"_{key}"] = record[key]  # create new key from original
            record.pop(key)  # remove the original key
    return record


def transform_pivot_values(record: Dict) -> Mapping[str, Any]:
    pivot_values = record.get("pivotValues", [])
    record["string_of_pivot_values"] = ",".join(pivot_values)
    return record


def transform_data(records: List) -> Iterable[Mapping]:
    """
    We need to transform the nested complex data structures into simple key:value pair,
    to be properly normalised in the destination.
    """
    for record in records:
        if "changeAuditStamps" in record:
            record = transform_change_audit_stamps(record)

        if "dateRange" in record:
            record = transform_date_range(record)

        if "targetingCriteria" in record:
            record = transform_targeting_criteria(record)

        if "variables" in record:
            record = transform_variables(record)

        if "pivotValues" in record:
            record = transform_pivot_values(record)

        record = transform_col_names(record, DESTINATION_RESERVED_KEYWORDS)

        yield record
