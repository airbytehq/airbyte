#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import typing
from typing import Any, Mapping

OPTIONS_STR = "$options"


DEFAULT_MODEL_TYPES: Mapping[str, str] = {
    # CompositeErrorHandler
    "CompositeErrorHandler.error_handlers": "DefaultErrorHandler",
    # CursorPagination
    "CursorPagination.decoder": "JsonDecoder",
    # DatetimeStreamSlicer
    "DatetimeStreamSlicer.end_datetime": "MinMaxDatetime",
    "DatetimeStreamSlicer.end_time_option": "RequestOption",
    "DatetimeStreamSlicer.start_datetime": "MinMaxDatetime",
    "DatetimeStreamSlicer.start_time_option": "RequestOption",
    # DeclarativeSource
    "DeclarativeSource.check": "CheckStream",
    "DeclarativeSource.spec": "Spec",
    "DeclarativeSource.streams": "DeclarativeStream",
    # DeclarativeStream
    "DeclarativeStream.retriever": "SimpleRetriever",
    "DeclarativeStream.schema_loader": "JsonFileSchemaLoader",
    # DefaultErrorHandler
    "DefaultErrorHandler.response_filters": "HttpResponseFilter",
    # DefaultPaginator
    "DefaultPaginator.decoder": "JsonDecoder",
    "DefaultPaginator.page_size_option": "RequestOption",
    "DefaultPaginator.page_token_option": "RequestOption",
    # DpathExtractor
    "DpathExtractor.decoder": "JsonDecoder",
    # HttpRequester
    "HttpRequester.error_handler": "DefaultErrorHandler",
    "HttpRequester.request_options_provider": "InterpolatedRequestOptionsProvider",
    # ListStreamSlicer
    "ListStreamSlicer.request_option": "RequestOption",
    # ParentStreamConfig
    "ParentStreamConfig.request_option": "RequestOption",
    "ParentStreamConfig.stream": "DeclarativeStream",
    # RecordSelector
    "RecordSelector.extractor": "DpathExtractor",
    "RecordSelector.record_filter": "RecordFilter",
    # SimpleRetriever
    "SimpleRetriever.paginator": "NoPagination",
    "SimpleRetriever.record_selector": "RecordSelector",
    "SimpleRetriever.requester": "HttpRequester",
    "SimpleRetriever.stream_slicer": "SingleSlice",
    # SubstreamSlicer
    "SubstreamSlicer.parent_stream_configs": "ParentStreamConfig",
    # AddFields
    "AddFields.fields": "AddedFieldDefinition",
    # CustomStreamSlicer
    "CustomStreamSlicer.end_datetime": "MinMaxDatetime",
    "CustomStreamSlicer.end_time_option": "RequestOption",
    "CustomStreamSlicer.parent_stream_configs": "ParentStreamConfig",
    "CustomStreamSlicer.start_datetime": "MinMaxDatetime",
    "CustomStreamSlicer.start_time_option": "RequestOption",
}

# We retain a separate registry for custom components to automatically insert the type if it is missing. This is intended to
# be a short term fix because once we have migrated, then type and class_name should be requirements for all custom components.
CUSTOM_COMPONENTS_MAPPING: Mapping[str, str] = {
    "CartesianProductStreamSlicer.stream_slicers": "CustomStreamSlicer",
    "CompositeErrorHandler.backoff_strategies": "CustomBackoffStrategy",
    "DeclarativeStream.retriever": "CustomRetriever",
    "DeclarativeStream.transformations": "CustomTransformation",
    "DefaultErrorHandler.backoff_strategies": "CustomBackoffStrategy",
    "DefaultPaginator.pagination_strategy": "CustomPaginationStrategy",
    "HttpRequester.authenticator": "CustomAuthenticator",
    "HttpRequester.error_handler": "CustomErrorHandler",
    "RecordSelector.extractor": "CustomRecordExtractor",
    "SimpleRetriever.stream_slicer": "CustomStreamSlicer",
}


class ManifestComponentTransformer:
    def propagate_types_and_options(
        self, parent_field_identifier: str, declarative_component: Mapping[str, Any], parent_options: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Recursively transforms the specified declarative component and subcomponents to propagate options and insert the
        default component type if it was not already present. The resulting transformed components are a deep copy of the input
        components, not an in-place transformation.

        :param declarative_component: The current component that is having type and options added
        :param parent_field_identifier: The name of the field of the current component coming from the parent component
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
                found_type = CUSTOM_COMPONENTS_MAPPING.get(parent_field_identifier)
            else:
                found_type = DEFAULT_MODEL_TYPES.get(parent_field_identifier)
            if found_type:
                propagated_component["type"] = found_type

        # When there is no resolved type, we're not processing a component (likely a regular object) and don't need to propagate options
        if "type" not in propagated_component:
            return propagated_component

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
                parent_type_field_identifier = f"{propagated_component.get('type')}.{field_name}"
                propagated_component[field_name] = self.propagate_types_and_options(
                    parent_type_field_identifier, field_value, current_options
                )
                if excluded_option:
                    current_options[field_name] = excluded_option
            elif isinstance(field_value, typing.List):
                # We exclude propagating an option that matches the current field name because that would result in an infinite cycle
                excluded_option = current_options.pop(field_name, None)
                for i, element in enumerate(field_value):
                    if isinstance(element, dict):
                        parent_type_field_identifier = f"{propagated_component.get('type')}.{field_name}"
                        field_value[i] = self.propagate_types_and_options(parent_type_field_identifier, element, current_options)
                if excluded_option:
                    current_options[field_name] = excluded_option

        if current_options:
            propagated_component[OPTIONS_STR] = current_options
        return propagated_component
