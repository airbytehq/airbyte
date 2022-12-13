#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import typing
from typing import Any, Mapping

OPTIONS_STR = "$options"


# todo: For better granularity, we may want this to be keyed on the object + field
DEFAULT_MODEL_TYPES: Mapping[str, str] = {
    # DatetimeStreamSlicer
    "end_datetime": "MinMaxDatetime",
    "start_datetime": "MinMaxDatetime",
    # DeclarativeSource
    "streams": "DeclarativeStream",
    # DeclarativeStream
    "retriever": "SimpleRetriever",
    "schema_loader": "DefaultSchemaLoader",
    # CursorPagination, DefaultPaginator, DpathExtractor
    "decoder": "JsonDecoder",
    # DefaultErrorHandler
    "response_filters": "HttpResponseFilter",
    # DefaultPaginator
    "page_size_option": "RequestOption",
    "page_token_option": "RequestOption",
    # HttpRequester
    "error_handler": "DefaultErrorHandler",
    "request_options_provider": "InterpolatedRequestOptionsProvider",
    # ListStreamSlicer, ParentStreamConfig
    "request_option": "RequestOption",
    # ParentStreamConfig
    "stream": "DeclarativeStream",
    # RecordSelector
    "extractor": "DpathExtractor",
    # SimpleRetriever
    "paginator": "NoPagination",
    "record_selector": "RecordSelector",
    "requester": "HttpRequester",
    "stream_slicer": "SingleSlice",
    # SubstreamSlicer
    "parent_stream_configs": "ParentStreamConfig",
    # Transformers
    "fields": "AddedFieldDefinition",
}

# I don't love this separate map, but we may need to separate the behavior when we see class_name
CUSTOM_COMPONENTS_MAPPING: Mapping[str, str] = {
    "authenticator": "CustomAuthenticator",
    "backoff_strategies": "CustomBackoffStrategy",
    "extractor": "CustomRecordExtractor",
    "pagination_strategy": "CustomPaginationStrategy",
    "stream_slicer": "CustomStreamSlicer",
}


class ManifestComponentTransformer:
    def propagate_types_and_options(
        self, parent_field: str, declarative_component: Mapping[str, Any], parent_options: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Recursively transforms the specified declarative component and subcomponents to propagate options and insert the
        default component type if it was not already present. The resulting transformed components are a deep copy of the input
        components, not an in-place transformation.

        :param declarative_component: The current component that is having type and options added
        :param parent_field: The name of the field of the current component coming from the parent component
        :param parent_options: The options set on parent components defined before the current component
        :return: A deep copy of the transformed component with types and options persisted to it
        """
        propagated_component = dict(copy.deepcopy(declarative_component))
        if "type" not in propagated_component:
            # If the component has class_name we assume that this is a reference to a custom component. This is a slight change to
            # existing behavior because we originally allowed for either class or type to be specified. After the pydantic migration,
            # class_name will only be a valid field on custom components and this change reflects that. I checked, and we currently
            # have no low-code connectors that use class_name except for custom components.
            if "class_name" in propagated_component:
                found_type = CUSTOM_COMPONENTS_MAPPING.get(parent_field)
            else:
                found_type = DEFAULT_MODEL_TYPES.get(parent_field)
            if found_type:
                propagated_component["type"] = found_type

        # Combines options defined at the current level with options from parent components. Options at the current level take precedence
        current_options = dict(copy.deepcopy(parent_options))
        component_options = propagated_component.pop(OPTIONS_STR, {})
        current_options = {**current_options, **component_options}

        # Options should be applied to the current component fields with the existing field taking precedence over options if both exist
        for option_key, option_value in current_options.items():
            propagated_component[option_key] = propagated_component.get(option_key) or option_value

        for field_name, field_value in propagated_component.items():
            if isinstance(field_value, dict):
                # We exclude propagating an option that matches the current field name because that would result in an infinite cycle
                excluded_option = current_options.pop(field_name, None)
                propagated_component[field_name] = self.propagate_types_and_options(field_name, field_value, current_options)
                if excluded_option:
                    current_options[field_name] = excluded_option
            elif isinstance(field_value, typing.List):
                for i, element in enumerate(field_value):
                    if isinstance(element, dict):
                        field_value[i] = self.propagate_types_and_options(field_name, element, current_options)

        if current_options:
            propagated_component[OPTIONS_STR] = current_options
        return propagated_component
