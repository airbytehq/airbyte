#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_nested_mapping import NestedMapping
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RequestBodyGraphQL,
    RequestBodyJsonObject,
    RequestBodyPlainText,
    RequestBodyUrlEncodedForm,
)
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_nested_request_input_provider import (
    InterpolatedNestedRequestInputProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_input_provider import (
    InterpolatedRequestInputProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import (
    RequestOptionsProvider,
)
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState

RequestInput = Union[str, Mapping[str, str]]
ValidRequestTypes = (str, list)


@dataclass
class InterpolatedRequestOptionsProvider(RequestOptionsProvider):
    """
    Defines the request options to set on an outgoing HTTP request by evaluating `InterpolatedMapping`s

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
        request_parameters (Union[str, Mapping[str, str]]): The request parameters to set on an outgoing HTTP request
        request_headers (Union[str, Mapping[str, str]]): The request headers to set on an outgoing HTTP request
        request_body_data (Union[str, Mapping[str, str]]): The body data to set on an outgoing HTTP request
        request_body_json (Union[str, Mapping[str, str]]): The json content to set on an outgoing HTTP request
    """

    parameters: InitVar[Mapping[str, Any]]
    config: Config = field(default_factory=dict)
    request_parameters: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_body: Optional[
        Union[
            RequestBodyGraphQL,
            RequestBodyJsonObject,
            RequestBodyPlainText,
            RequestBodyUrlEncodedForm,
        ]
    ] = None
    request_body_data: Optional[RequestInput] = None
    request_body_json: Optional[NestedMapping] = None
    query_properties_key: Optional[str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if self.request_parameters is None:
            self.request_parameters = {}
        if self.request_headers is None:
            self.request_headers = {}
        # resolve the request body to either data or json
        self._resolve_request_body()
        # If request_body is not provided, set request_body_data and request_body_json to empty dicts
        if self.request_body_data is None:
            self.request_body_data = {}
        if self.request_body_json is None:
            self.request_body_json = {}
        # If both request_body_data and request_body_json are provided, raise an error
        if self.request_body_json and self.request_body_data:
            raise ValueError(
                "RequestOptionsProvider should only contain either 'request_body_data' or 'request_body_json' not both"
            )
        # set interpolators
        self._parameter_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_parameters, parameters=parameters
        )
        self._headers_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_headers, parameters=parameters
        )
        self._body_data_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_body_data, parameters=parameters
        )
        self._body_json_interpolator = InterpolatedNestedRequestInputProvider(
            config=self.config, request_inputs=self.request_body_json, parameters=parameters
        )

    def _resolve_request_body(self) -> None:
        """
        Resolves the request body configuration by setting either `request_body_data` or `request_body_json`
        based on the type specified in `self.request_body`. If neither is provided, both are initialized as empty
        dictionaries. Raises a ValueError if both `request_body_data` and `request_body_json` are set simultaneously.
        Raises:
            ValueError: if an unsupported request body type is provided.
        """
        # Resolve the request body to either data or json
        if self.request_body is not None and self.request_body.type is not None:
            if self.request_body.type == "RequestBodyUrlEncodedForm":
                self.request_body_data = self.request_body.value
            elif self.request_body.type == "RequestBodyGraphQL":
                self.request_body_json = self.request_body.value.dict(exclude_none=True)
            elif self.request_body.type in ("RequestBodyJsonObject", "RequestBodyPlainText"):
                self.request_body_json = self.request_body.value
            else:
                raise ValueError(f"Unsupported request body type: {self.request_body.type}")

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        interpolated_value = self._parameter_interpolator.eval_request_inputs(
            stream_slice,
            next_page_token,
            valid_key_types=(str,),
            valid_value_types=ValidRequestTypes,
        )
        if isinstance(interpolated_value, dict):
            if self.query_properties_key:
                if not stream_slice:
                    raise ValueError(
                        "stream_slice should not be None if query properties in requests is enabled. Please contact Airbyte Support"
                    )
                elif (
                    "query_properties" not in stream_slice.extra_fields
                    or stream_slice.extra_fields.get("query_properties") is None
                ):
                    raise ValueError(
                        "QueryProperties component is defined but stream_partition does not contain query_properties. Please contact Airbyte Support"
                    )
                elif not isinstance(stream_slice.extra_fields.get("query_properties"), List):
                    raise ValueError(
                        "QueryProperties component is defined but stream_slice.extra_fields.query_properties is not a List. Please contact Airbyte Support"
                    )
                interpolated_value = {
                    **interpolated_value,
                    self.query_properties_key: ",".join(
                        stream_slice.extra_fields.get("query_properties")  # type: ignore  # Earlier type checks validate query_properties type
                    ),
                }
            return interpolated_value
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._headers_interpolator.eval_request_inputs(stream_slice, next_page_token)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return self._body_data_interpolator.eval_request_inputs(
            stream_slice,
            next_page_token,
            valid_key_types=(str,),
            valid_value_types=ValidRequestTypes,
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._body_json_interpolator.eval_request_inputs(stream_slice, next_page_token)
