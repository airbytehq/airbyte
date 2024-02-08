#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import typing
from typing import Any, Mapping

PARAMETERS_STR = "$parameters"


DEFAULT_MODEL_TYPES: Mapping[str, str] = {
    # CompositeErrorHandler
    "CompositeErrorHandler.error_handlers": "DefaultErrorHandler",
    # CursorPagination
    "CursorPagination.decoder": "JsonDecoder",
    # DatetimeBasedCursor
    "DatetimeBasedCursor.end_datetime": "MinMaxDatetime",
    "DatetimeBasedCursor.end_time_option": "RequestOption",
    "DatetimeBasedCursor.start_datetime": "MinMaxDatetime",
    "DatetimeBasedCursor.start_time_option": "RequestOption",
    # CustomIncrementalSync
    "CustomIncrementalSync.end_datetime": "MinMaxDatetime",
    "CustomIncrementalSync.end_time_option": "RequestOption",
    "CustomIncrementalSync.start_datetime": "MinMaxDatetime",
    "CustomIncrementalSync.start_time_option": "RequestOption",
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
    # DpathExtractor
    "DpathExtractor.decoder": "JsonDecoder",
    # HttpRequester
    "HttpRequester.error_handler": "DefaultErrorHandler",
    # ListPartitionRouter
    "ListPartitionRouter.request_option": "RequestOption",
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
    # SubstreamPartitionRouter
    "SubstreamPartitionRouter.parent_stream_configs": "ParentStreamConfig",
    # AddFields
    "AddFields.fields": "AddedFieldDefinition",
    # CustomPartitionRouter
    "CustomPartitionRouter.parent_stream_configs": "ParentStreamConfig",
}

# We retain a separate registry for custom components to automatically insert the type if it is missing. This is intended to
# be a short term fix because once we have migrated, then type and class_name should be requirements for all custom components.
CUSTOM_COMPONENTS_MAPPING: Mapping[str, str] = {
    "CompositeErrorHandler.backoff_strategies": "CustomBackoffStrategy",
    "DeclarativeStream.retriever": "CustomRetriever",
    "DeclarativeStream.transformations": "CustomTransformation",
    "DefaultErrorHandler.backoff_strategies": "CustomBackoffStrategy",
    "DefaultPaginator.pagination_strategy": "CustomPaginationStrategy",
    "HttpRequester.authenticator": "CustomAuthenticator",
    "HttpRequester.error_handler": "CustomErrorHandler",
    "RecordSelector.extractor": "CustomRecordExtractor",
    "SimpleRetriever.partition_router": "CustomPartitionRouter",
}


class ManifestComponentTransformer:
    def propagate_types_and_parameters(
        self, parent_field_identifier: str, declarative_component: Mapping[str, Any], parent_parameters: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Recursively transforms the specified declarative component and subcomponents to propagate parameters and insert the
        default component type if it was not already present. The resulting transformed components are a deep copy of the input
        components, not an in-place transformation.

        :param declarative_component: The current component that is having type and parameters added
        :param parent_field_identifier: The name of the field of the current component coming from the parent component
        :param parent_parameters: The parameters set on parent components defined before the current component
        :return: A deep copy of the transformed component with types and parameters persisted to it
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

        # When there is no resolved type, we're not processing a component (likely a regular object) and don't need to propagate parameters
        # When the type refers to a json schema, we're not processing a component as well. This check is currently imperfect as there could
        # be json_schema are not objects but we believe this is not likely in our case because:
        # * records are Mapping so objects hence SchemaLoader root should be an object
        # * connection_specification is a Mapping
        if "type" not in propagated_component or self._is_json_schema_object(propagated_component):
            return propagated_component

        # Combines parameters defined at the current level with parameters from parent components. Parameters at the current
        # level take precedence
        current_parameters = dict(copy.deepcopy(parent_parameters))
        component_parameters = propagated_component.pop(PARAMETERS_STR, {})
        current_parameters = {**current_parameters, **component_parameters}

        # Parameters should be applied to the current component fields with the existing field taking precedence over parameters if
        # both exist
        for parameter_key, parameter_value in current_parameters.items():
            propagated_component[parameter_key] = propagated_component.get(parameter_key) or parameter_value

        for field_name, field_value in propagated_component.items():
            if isinstance(field_value, dict):
                # We exclude propagating a parameter that matches the current field name because that would result in an infinite cycle
                excluded_parameter = current_parameters.pop(field_name, None)
                parent_type_field_identifier = f"{propagated_component.get('type')}.{field_name}"
                propagated_component[field_name] = self.propagate_types_and_parameters(
                    parent_type_field_identifier, field_value, current_parameters
                )
                if excluded_parameter:
                    current_parameters[field_name] = excluded_parameter
            elif isinstance(field_value, typing.List):
                # We exclude propagating a parameter that matches the current field name because that would result in an infinite cycle
                excluded_parameter = current_parameters.pop(field_name, None)
                for i, element in enumerate(field_value):
                    if isinstance(element, dict):
                        parent_type_field_identifier = f"{propagated_component.get('type')}.{field_name}"
                        field_value[i] = self.propagate_types_and_parameters(parent_type_field_identifier, element, current_parameters)
                if excluded_parameter:
                    current_parameters[field_name] = excluded_parameter

        if current_parameters:
            propagated_component[PARAMETERS_STR] = current_parameters
        return propagated_component

    @staticmethod
    def _is_json_schema_object(propagated_component: Mapping[str, Any]) -> bool:
        return propagated_component.get("type") == "object"
