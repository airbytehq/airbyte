#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, MutableMapping, Union

import dpath
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from source_google_sheets.helpers_ import Helpers


def _make_interpolated_path(provided_path, parameters):
    interpolated_path = [InterpolatedString.create(path, parameters=parameters) for path in provided_path]
    for path_index in range(len(interpolated_path)):
        if isinstance(interpolated_path[path_index], str):
            interpolated_path[path_index] = InterpolatedString.create(interpolated_path[path_index], parameters=parameters)
    return interpolated_path


def create_requester_from_component_definition(component_definition, config):
    factory_constructor = ModelToComponentFactory(emit_connector_builder_messages=False, disable_cache=False)
    # sheet_headers_requester_definition = parameters.get("headers_requester")
    sheet_headers_requester_name = component_definition.get("$parameters", {}).get("name", "")
    sheet_headers_requester = factory_constructor.create_component(
        model_type=HttpRequester,
        component_definition=component_definition,
        config=config,
        name=sheet_headers_requester_name,
    )
    if not sheet_headers_requester.use_cache:
        raise Exception("Stream Schema ordered properties requester is required to use cache.")
    return sheet_headers_requester


def _extract_records_by_path(
    response: requests.Response, provided_path: List[Union[InterpolatedString, str]], config
) -> Iterable[MutableMapping[Any, Any]]:
    for body in JsonDecoder({}).decode(response):
        if len(provided_path) == 0:
            extracted = body
        else:
            path = [path.eval(config) for path in provided_path]
            if "*" in path:
                extracted = dpath.values(body, path)
            else:
                extracted = dpath.get(body, path, default=[])  # type: ignore # extracted will be a MutableMapping, given input data structure
        if isinstance(extracted, list):
            yield from extracted
        elif extracted:
            yield extracted
        else:
            yield from []


def request_schema_ordered_properties(sheet_headers_requester, parameters, config):
    sheet_data_values_path = _make_interpolated_path(provided_path=parameters["sheet_data_values_path"], parameters=parameters)
    sheet_headers = []
    response = sheet_headers_requester.send_request()
    fields_to_match_key = parameters["fields_to_match_key"]
    sheet_data_values = _extract_records_by_path(response, sheet_data_values_path, config)
    for sheet_data_value in sheet_data_values:
        schema_property_value = sheet_data_value[fields_to_match_key]
        sheet_headers.append(schema_property_value)

    return Helpers.get_sheets_to_column_index_to_name(sheet_headers)


def resolve_fields_origin(parameters, config):
    try:
        fields_to_match_origin = parameters["fields_to_match_origin"]
    except KeyError:
        raise Exception("Missing required header requester parameter")

    if fields_to_match_origin.get("type") == "HttpRequester":
        sheet_headers_requester = create_requester_from_component_definition(fields_to_match_origin, config)
        stream_schema_ordered_properties = request_schema_ordered_properties(sheet_headers_requester, parameters, config)
        return stream_schema_ordered_properties
    else:
        return fields_to_match_origin
