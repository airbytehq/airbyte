#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import urlencode

import pendulum
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

from .utils import transform_data


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
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
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
