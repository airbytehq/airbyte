#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import importlib
import inspect
import re
from typing import Any, Callable, List, Literal, Mapping, Optional, Type, Union, get_args, get_origin, get_type_hints

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import (
    ApiKeyAuthenticator,
    BasicHttpAuthenticator,
    BearerAuthenticator,
    SessionTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.incremental import Cursor, CursorFactory, DatetimeBasedCursor, PerPartitionCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddedFieldDefinition as AddedFieldDefinitionModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddFields as AddFieldsModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ApiKeyAuthenticator as ApiKeyAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BasicHttpAuthenticator as BasicHttpAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BearerAuthenticator as BearerAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CompositeErrorHandler as CompositeErrorHandlerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConstantBackoffStrategy as ConstantBackoffStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CursorPagination as CursorPaginationModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomAuthenticator as CustomAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomBackoffStrategy as CustomBackoffStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomErrorHandler as CustomErrorHandlerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomIncrementalSync as CustomIncrementalSyncModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomPaginationStrategy as CustomPaginationStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomPartitionRouter as CustomPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRecordExtractor as CustomRecordExtractorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRequester as CustomRequesterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRetriever as CustomRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomTransformation as CustomTransformationModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DatetimeBasedCursor as DatetimeBasedCursorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultPaginator as DefaultPaginatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DpathExtractor as DpathExtractorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ExponentialBackoffStrategy as ExponentialBackoffStrategyModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpResponseFilter as HttpResponseFilterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import InlineSchemaLoader as InlineSchemaLoaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonDecoder as JsonDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonFileSchemaLoader as JsonFileSchemaLoaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ListPartitionRouter as ListPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import MinMaxDatetime as MinMaxDatetimeModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import NoAuth as NoAuthModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import NoPagination as NoPaginationModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import OAuthAuthenticator as OAuthAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import OffsetIncrement as OffsetIncrementModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import PageIncrement as PageIncrementModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ParentStreamConfig as ParentStreamConfigModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RecordFilter as RecordFilterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RecordSelector as RecordSelectorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RemoveFields as RemoveFieldsModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RequestOption as RequestOptionModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RequestPath as RequestPathModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SessionTokenAuthenticator as SessionTokenAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SimpleRetriever as SimpleRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SubstreamPartitionRouter as SubstreamPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import WaitTimeFromHeader as WaitTimeFromHeaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import WaitUntilTimeFromHeader as WaitUntilTimeFromHeaderModel
from airbyte_cdk.sources.declarative.partition_routers import ListPartitionRouter, SinglePartitionRouter, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import CompositeErrorHandler, DefaultErrorHandler, HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import (
    ConstantBackoffStrategy,
    ExponentialBackoffStrategy,
    WaitTimeFromHeaderBackoffStrategy,
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator, NoPagination, PaginatorTestReadDecorator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy, OffsetIncrement, PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever, SimpleRetrieverTestReadDecorator
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader, InlineSchemaLoader, JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer, StreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.message import InMemoryMessageRepository
from pydantic import BaseModel

ComponentDefinition: Union[Literal, Mapping, List]


DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy


class ModelToComponentFactory:
    def __init__(
        self,
        limit_pages_fetched_per_slice: int = None,
        limit_slices_fetched: int = None,
        emit_connector_builder_messages: bool = False,
        disable_retries=False,
    ):
        self._init_mappings()
        self._limit_pages_fetched_per_slice = limit_pages_fetched_per_slice
        self._limit_slices_fetched = limit_slices_fetched
        self._emit_connector_builder_messages = emit_connector_builder_messages
        self._disable_retries = disable_retries
        self._message_repository = InMemoryMessageRepository()

    def _init_mappings(self):
        self.PYDANTIC_MODEL_TO_CONSTRUCTOR: [Type[BaseModel], Callable] = {
            AddedFieldDefinitionModel: self.create_added_field_definition,
            AddFieldsModel: self.create_add_fields,
            ApiKeyAuthenticatorModel: self.create_api_key_authenticator,
            BasicHttpAuthenticatorModel: self.create_basic_http_authenticator,
            BearerAuthenticatorModel: self.create_bearer_authenticator,
            CheckStreamModel: self.create_check_stream,
            CompositeErrorHandlerModel: self.create_composite_error_handler,
            ConstantBackoffStrategyModel: self.create_constant_backoff_strategy,
            CursorPaginationModel: self.create_cursor_pagination,
            CustomAuthenticatorModel: self.create_custom_component,
            CustomBackoffStrategyModel: self.create_custom_component,
            CustomErrorHandlerModel: self.create_custom_component,
            CustomIncrementalSyncModel: self.create_custom_component,
            CustomRecordExtractorModel: self.create_custom_component,
            CustomRequesterModel: self.create_custom_component,
            CustomRetrieverModel: self.create_custom_component,
            CustomPaginationStrategyModel: self.create_custom_component,
            CustomPartitionRouterModel: self.create_custom_component,
            CustomTransformationModel: self.create_custom_component,
            DatetimeBasedCursorModel: self.create_datetime_based_cursor,
            DeclarativeStreamModel: self.create_declarative_stream,
            DefaultErrorHandlerModel: self.create_default_error_handler,
            DefaultPaginatorModel: self.create_default_paginator,
            DpathExtractorModel: self.create_dpath_extractor,
            ExponentialBackoffStrategyModel: self.create_exponential_backoff_strategy,
            HttpRequesterModel: self.create_http_requester,
            HttpResponseFilterModel: self.create_http_response_filter,
            InlineSchemaLoaderModel: self.create_inline_schema_loader,
            JsonDecoderModel: self.create_json_decoder,
            JsonFileSchemaLoaderModel: self.create_json_file_schema_loader,
            ListPartitionRouterModel: self.create_list_partition_router,
            MinMaxDatetimeModel: self.create_min_max_datetime,
            NoAuthModel: self.create_no_auth,
            NoPaginationModel: self.create_no_pagination,
            OAuthAuthenticatorModel: self.create_oauth_authenticator,
            OffsetIncrementModel: self.create_offset_increment,
            PageIncrementModel: self.create_page_increment,
            ParentStreamConfigModel: self.create_parent_stream_config,
            RecordFilterModel: self.create_record_filter,
            RecordSelectorModel: self.create_record_selector,
            RemoveFieldsModel: self.create_remove_fields,
            RequestPathModel: self.create_request_path,
            RequestOptionModel: self.create_request_option,
            SessionTokenAuthenticatorModel: self.create_session_token_authenticator,
            SimpleRetrieverModel: self.create_simple_retriever,
            SpecModel: self.create_spec,
            SubstreamPartitionRouterModel: self.create_substream_partition_router,
            WaitTimeFromHeaderModel: self.create_wait_time_from_header,
            WaitUntilTimeFromHeaderModel: self.create_wait_until_time_from_header,
        }

        # Needed for the case where we need to perform a second parse on the fields of a custom component
        self.TYPE_NAME_TO_MODEL = {cls.__name__: cls for cls in self.PYDANTIC_MODEL_TO_CONSTRUCTOR}

    def create_component(self, model_type: Type[BaseModel], component_definition: ComponentDefinition, config: Config, **kwargs) -> type:
        """
        Takes a given Pydantic model type and Mapping representing a component definition and creates a declarative component and
        subcomponents which will be used at runtime. This is done by first parsing the mapping into a Pydantic model and then creating
        creating declarative components from that model.

        :param model_type: The type of declarative component that is being initialized
        :param component_definition: The mapping that represents a declarative component
        :param config: The connector config that is provided by the customer
        :return: The declarative component to be used at runtime
        """

        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(f"Expected manifest component of type {model_type.__name__}, but received {component_type} instead")

        declarative_component_model = model_type.parse_obj(component_definition)

        if not isinstance(declarative_component_model, model_type):
            raise ValueError(f"Expected {model_type.__name__} component, but received {declarative_component_model.__class__.__name__}")

        return self._create_component_from_model(model=declarative_component_model, config=config, **kwargs)

    def _create_component_from_model(self, model: BaseModel, config: Config, **kwargs) -> Any:
        if model.__class__ not in self.PYDANTIC_MODEL_TO_CONSTRUCTOR:
            raise ValueError(f"{model.__class__} with attributes {model} is not a valid component type")
        component_constructor = self.PYDANTIC_MODEL_TO_CONSTRUCTOR.get(model.__class__)
        return component_constructor(model=model, config=config, **kwargs)

    @staticmethod
    def create_added_field_definition(model: AddedFieldDefinitionModel, config: Config, **kwargs) -> AddedFieldDefinition:
        interpolated_value = InterpolatedString.create(model.value, parameters=model.parameters)
        return AddedFieldDefinition(path=model.path, value=interpolated_value, parameters=model.parameters)

    def create_add_fields(self, model: AddFieldsModel, config: Config, **kwargs) -> AddFields:
        added_field_definitions = [
            self._create_component_from_model(model=added_field_definition_model, config=config)
            for added_field_definition_model in model.fields
        ]
        return AddFields(fields=added_field_definitions, parameters=model.parameters)

    @staticmethod
    def create_api_key_authenticator(model: ApiKeyAuthenticatorModel, config: Config, **kwargs) -> ApiKeyAuthenticator:
        if model.inject_into is None and model.header is None:
            raise ValueError("Expected either inject_into or header to be set for ApiKeyAuthenticator")

        if model.inject_into is not None and model.header is not None:
            raise ValueError("inject_into and header cannot be set both for ApiKeyAuthenticator - remove the deprecated header option")

        request_option = (
            RequestOption(
                inject_into=RequestOptionType(model.inject_into.inject_into.value),
                field_name=model.inject_into.field_name,
                parameters=model.parameters,
            )
            if model.inject_into
            else RequestOption(
                inject_into=RequestOptionType.header,
                field_name=model.header,
                parameters=model.parameters,
            )
        )
        return ApiKeyAuthenticator(api_token=model.api_token, request_option=request_option, config=config, parameters=model.parameters)

    @staticmethod
    def create_basic_http_authenticator(model: BasicHttpAuthenticatorModel, config: Config, **kwargs) -> BasicHttpAuthenticator:
        return BasicHttpAuthenticator(password=model.password, username=model.username, config=config, parameters=model.parameters)

    @staticmethod
    def create_bearer_authenticator(model: BearerAuthenticatorModel, config: Config, **kwargs) -> BearerAuthenticator:
        return BearerAuthenticator(
            api_token=model.api_token,
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_check_stream(model: CheckStreamModel, config: Config, **kwargs):
        return CheckStream(stream_names=model.stream_names, parameters={})

    def create_composite_error_handler(self, model: CompositeErrorHandlerModel, config: Config, **kwargs) -> CompositeErrorHandler:
        error_handlers = [
            self._create_component_from_model(model=error_handler_model, config=config) for error_handler_model in model.error_handlers
        ]
        return CompositeErrorHandler(error_handlers=error_handlers, parameters=model.parameters)

    @staticmethod
    def create_constant_backoff_strategy(model: ConstantBackoffStrategyModel, config: Config, **kwargs) -> ConstantBackoffStrategy:
        return ConstantBackoffStrategy(
            backoff_time_in_seconds=model.backoff_time_in_seconds,
            config=config,
            parameters=model.parameters,
        )

    def create_cursor_pagination(self, model: CursorPaginationModel, config: Config, **kwargs) -> CursorPaginationStrategy:
        if model.decoder:
            decoder = self._create_component_from_model(model=model.decoder, config=config)
        else:
            decoder = JsonDecoder(parameters=model.parameters)

        return CursorPaginationStrategy(
            cursor_value=model.cursor_value,
            decoder=decoder,
            page_size=model.page_size,
            stop_condition=model.stop_condition,
            config=config,
            parameters=model.parameters,
        )

    def create_custom_component(self, model, config: Config, **kwargs) -> type:
        """
        Generically creates a custom component based on the model type and a class_name reference to the custom Python class being
        instantiated. Only the model's additional properties that match the custom class definition are passed to the constructor
        :param model: The Pydantic model of the custom component being created
        :param config: The custom defined connector config
        :return: The declarative component built from the Pydantic model to be used at runtime
        """

        custom_component_class = self._get_class_from_fully_qualified_class_name(model.class_name)
        component_fields = get_type_hints(custom_component_class)
        model_args = model.dict()
        model_args["config"] = config

        # There are cases where a parent component will pass arguments to a child component via kwargs. When there are field collisions
        # we defer to these arguments over the component's definition
        for key, arg in kwargs.items():
            model_args[key] = arg

        # Pydantic is unable to parse a custom component's fields that are subcomponents into models because their fields and types are not
        # defined in the schema. The fields and types are defined within the Python class implementation. Pydantic can only parse down to
        # the custom component and this code performs a second parse to convert the sub-fields first into models, then declarative components
        for model_field, model_value in model_args.items():
            # If a custom component field doesn't have a type set, we try to use the type hints to infer the type
            if isinstance(model_value, dict) and "type" not in model_value and model_field in component_fields:
                derived_type = self._derive_component_type_from_type_hints(component_fields.get(model_field))
                if derived_type:
                    model_value["type"] = derived_type

            if self._is_component(model_value):
                model_args[model_field] = self._create_nested_component(model, model_field, model_value, config)
            elif isinstance(model_value, list):
                vals = []
                for v in model_value:
                    if isinstance(v, dict) and "type" not in v and model_field in component_fields:
                        derived_type = self._derive_component_type_from_type_hints(component_fields.get(model_field))
                        if derived_type:
                            v["type"] = derived_type
                    if self._is_component(v):
                        vals.append(self._create_nested_component(model, model_field, v, config))
                    else:
                        vals.append(v)
                model_args[model_field] = vals

        kwargs = {class_field: model_args[class_field] for class_field in component_fields.keys() if class_field in model_args}
        return custom_component_class(**kwargs)

    @staticmethod
    def _get_class_from_fully_qualified_class_name(class_name: str) -> type:
        split = class_name.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]
        return getattr(importlib.import_module(module), class_name)

    @staticmethod
    def _derive_component_type_from_type_hints(field_type: str) -> Optional[str]:
        interface = field_type
        while True:
            origin = get_origin(interface)
            if origin:
                # Unnest types until we reach the raw type
                # List[T] -> T
                # Optional[List[T]] -> T
                args = get_args(interface)
                interface = args[0]
            else:
                break
        if isinstance(interface, type) and not ModelToComponentFactory.is_builtin_type(interface):
            return interface.__name__
        return None

    @staticmethod
    def is_builtin_type(cls) -> bool:
        if not cls:
            return False
        return cls.__module__ == "builtins"

    @staticmethod
    def _extract_missing_parameters(error: TypeError) -> List[str]:
        parameter_search = re.search(r"keyword-only.*:\s(.*)", str(error))
        if parameter_search:
            return re.findall(r"\'(.+?)\'", parameter_search.group(1))
        else:
            return []

    def _create_nested_component(self, model, model_field: str, model_value: Any, config: Config) -> Any:
        type_name = model_value.get("type", None)
        if not type_name:
            # If no type is specified, we can assume this is a dictionary object which can be returned instead of a subcomponent
            return model_value

        model_type = self.TYPE_NAME_TO_MODEL.get(type_name, None)
        if model_type:
            parsed_model = model_type.parse_obj(model_value)
            try:
                # To improve usability of the language, certain fields are shared between components. This can come in the form of
                # a parent component passing some of its fields to a child component or the parent extracting fields from other child
                # components and passing it to others. One example is the DefaultPaginator referencing the HttpRequester url_base
                # while constructing a SimpleRetriever. However, custom components don't support this behavior because they are created
                # generically in create_custom_component(). This block allows developers to specify extra arguments in $parameters that
                # are needed by a component and could not be shared.
                model_constructor = self.PYDANTIC_MODEL_TO_CONSTRUCTOR.get(parsed_model.__class__)
                constructor_kwargs = inspect.getfullargspec(model_constructor).kwonlyargs
                model_parameters = model_value.get("$parameters", {})
                matching_parameters = {kwarg: model_parameters[kwarg] for kwarg in constructor_kwargs if kwarg in model_parameters}
                return self._create_component_from_model(model=parsed_model, config=config, **matching_parameters)
            except TypeError as error:
                missing_parameters = self._extract_missing_parameters(error)
                if missing_parameters:
                    raise ValueError(
                        f"Error creating component '{type_name}' with parent custom component {model.class_name}: Please provide "
                        + ", ".join((f"{type_name}.$parameters.{parameter}" for parameter in missing_parameters))
                    )
                raise TypeError(f"Error creating component '{type_name}' with parent custom component {model.class_name}: {error}")
        else:
            raise ValueError(
                f"Error creating custom component {model.class_name}. Subcomponent creation has not been implemented for '{type_name}'"
            )

    @staticmethod
    def _is_component(model_value: Any) -> bool:
        return isinstance(model_value, dict) and model_value.get("type")

    def create_datetime_based_cursor(self, model: DatetimeBasedCursorModel, config: Config, **kwargs) -> DatetimeBasedCursor:
        start_datetime = (
            model.start_datetime if isinstance(model.start_datetime, str) else self.create_min_max_datetime(model.start_datetime, config)
        )
        end_datetime = None
        if model.end_datetime:
            end_datetime = (
                model.end_datetime if isinstance(model.end_datetime, str) else self.create_min_max_datetime(model.end_datetime, config)
            )

        end_time_option = (
            RequestOption(
                inject_into=RequestOptionType(model.end_time_option.inject_into.value),
                field_name=model.end_time_option.field_name,
                parameters=model.parameters,
            )
            if model.end_time_option
            else None
        )
        start_time_option = (
            RequestOption(
                inject_into=RequestOptionType(model.start_time_option.inject_into.value),
                field_name=model.start_time_option.field_name,
                parameters=model.parameters,
            )
            if model.start_time_option
            else None
        )

        return DatetimeBasedCursor(
            cursor_field=model.cursor_field,
            cursor_granularity=model.cursor_granularity,
            datetime_format=model.datetime_format,
            end_datetime=end_datetime,
            start_datetime=start_datetime,
            step=model.step,
            end_time_option=end_time_option,
            lookback_window=model.lookback_window,
            start_time_option=start_time_option,
            partition_field_end=model.partition_field_end,
            partition_field_start=model.partition_field_start,
            config=config,
            parameters=model.parameters,
        )

    def create_declarative_stream(self, model: DeclarativeStreamModel, config: Config, **kwargs) -> DeclarativeStream:
        # When constructing a declarative stream, we assemble the incremental_sync component and retriever's partition_router field
        # components if they exist into a single CartesianProductStreamSlicer. This is then passed back as an argument when constructing the
        # Retriever. This is done in the declarative stream not the retriever to support custom retrievers. The custom create methods in
        # the factory only support passing arguments to the component constructors, whereas this performs a merge of all slicers into one.
        combined_slicers = self._merge_stream_slicers(model=model, config=config)

        primary_key = model.primary_key.__root__ if model.primary_key else None
        retriever = self._create_component_from_model(
            model=model.retriever, config=config, name=model.name, primary_key=primary_key, stream_slicer=combined_slicers
        )

        cursor_field = model.incremental_sync.cursor_field if model.incremental_sync else None

        if model.schema_loader:
            schema_loader = self._create_component_from_model(model=model.schema_loader, config=config)
        else:
            options = model.parameters or {}
            if "name" not in options:
                options["name"] = model.name
            schema_loader = DefaultSchemaLoader(config=config, parameters=options)

        transformations = []
        if model.transformations:
            for transformation_model in model.transformations:
                transformations.append(self._create_component_from_model(model=transformation_model, config=config))
        return DeclarativeStream(
            name=model.name,
            primary_key=primary_key,
            retriever=retriever,
            schema_loader=schema_loader,
            stream_cursor_field=cursor_field or "",
            transformations=transformations,
            config=config,
            parameters=model.parameters,
        )

    def _merge_stream_slicers(self, model: DeclarativeStreamModel, config: Config) -> Optional[StreamSlicer]:
        stream_slicer = None
        if hasattr(model.retriever, "partition_router") and model.retriever.partition_router:
            stream_slicer_model = model.retriever.partition_router
            stream_slicer = (
                CartesianProductStreamSlicer(
                    [self._create_component_from_model(model=slicer, config=config) for slicer in stream_slicer_model], parameters={}
                )
                if type(stream_slicer_model) == list
                else self._create_component_from_model(model=stream_slicer_model, config=config)
            )

        if model.incremental_sync and stream_slicer:
            return PerPartitionCursor(
                cursor_factory=CursorFactory(
                    lambda: self._create_component_from_model(model=model.incremental_sync, config=config),
                ),
                partition_router=stream_slicer,
            )
        elif model.incremental_sync:
            return self._create_component_from_model(model=model.incremental_sync, config=config) if model.incremental_sync else None
        elif stream_slicer:
            return stream_slicer
        else:
            return None

    def create_default_error_handler(self, model: DefaultErrorHandlerModel, config: Config, **kwargs) -> DefaultErrorHandler:
        backoff_strategies = []
        if model.backoff_strategies:
            for backoff_strategy_model in model.backoff_strategies:
                backoff_strategies.append(self._create_component_from_model(model=backoff_strategy_model, config=config))
        else:
            backoff_strategies.append(DEFAULT_BACKOFF_STRATEGY(config=config, parameters=model.parameters))

        response_filters = []
        if model.response_filters:
            for response_filter_model in model.response_filters:
                response_filters.append(self._create_component_from_model(model=response_filter_model, config=config))
        else:
            response_filters.append(
                HttpResponseFilter(
                    ResponseAction.RETRY, http_codes=HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS, config=config, parameters=model.parameters
                )
            )
            response_filters.append(HttpResponseFilter(ResponseAction.IGNORE, config=config, parameters=model.parameters))

        return DefaultErrorHandler(
            backoff_strategies=backoff_strategies,
            max_retries=model.max_retries,
            response_filters=response_filters,
            config=config,
            parameters=model.parameters,
        )

    def create_default_paginator(self, model: DefaultPaginatorModel, config: Config, *, url_base: str) -> DefaultPaginator:
        decoder = self._create_component_from_model(model=model.decoder, config=config) if model.decoder else JsonDecoder(parameters={})
        page_size_option = (
            self._create_component_from_model(model=model.page_size_option, config=config) if model.page_size_option else None
        )
        page_token_option = (
            self._create_component_from_model(model=model.page_token_option, config=config) if model.page_token_option else None
        )
        pagination_strategy = self._create_component_from_model(model=model.pagination_strategy, config=config)

        paginator = DefaultPaginator(
            decoder=decoder,
            page_size_option=page_size_option,
            page_token_option=page_token_option,
            pagination_strategy=pagination_strategy,
            url_base=url_base,
            config=config,
            parameters=model.parameters,
        )
        if self._limit_pages_fetched_per_slice:
            return PaginatorTestReadDecorator(paginator, self._limit_pages_fetched_per_slice)
        return paginator

    def create_dpath_extractor(self, model: DpathExtractorModel, config: Config, **kwargs) -> DpathExtractor:
        decoder = self._create_component_from_model(model.decoder, config=config) if model.decoder else JsonDecoder(parameters={})
        return DpathExtractor(decoder=decoder, field_path=model.field_path, config=config, parameters=model.parameters)

    @staticmethod
    def create_exponential_backoff_strategy(model: ExponentialBackoffStrategyModel, config: Config) -> ExponentialBackoffStrategy:
        return ExponentialBackoffStrategy(factor=model.factor, parameters=model.parameters, config=config)

    def create_http_requester(self, model: HttpRequesterModel, config: Config, *, name: str) -> HttpRequester:
        authenticator = (
            self._create_component_from_model(model=model.authenticator, config=config, url_base=model.url_base)
            if model.authenticator
            else None
        )
        error_handler = (
            self._create_component_from_model(model=model.error_handler, config=config)
            if model.error_handler
            else DefaultErrorHandler(backoff_strategies=[], response_filters=[], config=config, parameters=model.parameters)
        )

        request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=model.request_body_data,
            request_body_json=model.request_body_json,
            request_headers=model.request_headers,
            request_parameters=model.request_parameters,
            config=config,
            parameters=model.parameters,
        )

        return HttpRequester(
            name=name,
            url_base=model.url_base,
            path=model.path,
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=model.http_method,
            request_options_provider=request_options_provider,
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_http_response_filter(model: HttpResponseFilterModel, config: Config, **kwargs) -> HttpResponseFilter:
        action = ResponseAction(model.action.value)
        http_codes = (
            set(model.http_codes) if model.http_codes else set()
        )  # JSON schema notation has no set data type. The schema enforces an array of unique elements

        return HttpResponseFilter(
            action=action,
            error_message=model.error_message or "",
            error_message_contains=model.error_message_contains,
            http_codes=http_codes,
            predicate=model.predicate or "",
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_inline_schema_loader(model: InlineSchemaLoaderModel, config: Config, **kwargs) -> InlineSchemaLoader:
        return InlineSchemaLoader(schema=model.schema_, parameters={})

    @staticmethod
    def create_json_decoder(model: JsonDecoderModel, config: Config, **kwargs) -> JsonDecoder:
        return JsonDecoder(parameters={})

    @staticmethod
    def create_json_file_schema_loader(model: JsonFileSchemaLoaderModel, config: Config, **kwargs) -> JsonFileSchemaLoader:
        return JsonFileSchemaLoader(file_path=model.file_path, config=config, parameters=model.parameters)

    @staticmethod
    def create_list_partition_router(model: ListPartitionRouterModel, config: Config, **kwargs) -> ListPartitionRouter:
        request_option = (
            RequestOption(
                inject_into=RequestOptionType(model.request_option.inject_into.value),
                field_name=model.request_option.field_name,
                parameters=model.parameters,
            )
            if model.request_option
            else None
        )
        return ListPartitionRouter(
            cursor_field=model.cursor_field,
            request_option=request_option,
            values=model.values,
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_min_max_datetime(model: MinMaxDatetimeModel, config: Config, **kwargs) -> MinMaxDatetime:
        return MinMaxDatetime(
            datetime=model.datetime,
            datetime_format=model.datetime_format,
            max_datetime=model.max_datetime,
            min_datetime=model.min_datetime,
            parameters=model.parameters,
        )

    @staticmethod
    def create_no_auth(model: NoAuthModel, config: Config, **kwargs) -> NoAuth:
        return NoAuth(parameters=model.parameters)

    @staticmethod
    def create_no_pagination(model: NoPaginationModel, config: Config, **kwargs) -> NoPagination:
        return NoPagination(parameters={})

    def create_oauth_authenticator(self, model: OAuthAuthenticatorModel, config: Config, **kwargs) -> DeclarativeOauth2Authenticator:
        if model.refresh_token_updater:
            return DeclarativeSingleUseRefreshTokenOauth2Authenticator(
                config,
                InterpolatedString.create(model.token_refresh_endpoint, parameters=model.parameters).eval(config),
                access_token_name=InterpolatedString.create(model.access_token_name, parameters=model.parameters).eval(config),
                refresh_token_name=model.refresh_token_updater.refresh_token_name,
                expires_in_name=InterpolatedString.create(model.expires_in_name, parameters=model.parameters).eval(config),
                client_id=InterpolatedString.create(model.client_id, parameters=model.parameters).eval(config),
                client_secret=InterpolatedString.create(model.client_secret, parameters=model.parameters).eval(config),
                access_token_config_path=model.refresh_token_updater.access_token_config_path,
                refresh_token_config_path=model.refresh_token_updater.refresh_token_config_path,
                token_expiry_date_config_path=model.refresh_token_updater.token_expiry_date_config_path,
                grant_type=InterpolatedString.create(model.grant_type, parameters=model.parameters).eval(config),
                refresh_request_body=InterpolatedMapping(model.refresh_request_body or {}, parameters=model.parameters).eval(config),
                scopes=model.scopes,
                token_expiry_date_format=model.token_expiry_date_format,
                message_repository=self._message_repository,
            )
        return DeclarativeOauth2Authenticator(
            access_token_name=model.access_token_name,
            client_id=model.client_id,
            client_secret=model.client_secret,
            expires_in_name=model.expires_in_name,
            grant_type=model.grant_type,
            refresh_request_body=model.refresh_request_body,
            refresh_token=model.refresh_token,
            scopes=model.scopes,
            token_expiry_date=model.token_expiry_date,
            token_expiry_date_format=model.token_expiry_date_format,
            token_refresh_endpoint=model.token_refresh_endpoint,
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_offset_increment(model: OffsetIncrementModel, config: Config, **kwargs) -> OffsetIncrement:
        return OffsetIncrement(page_size=model.page_size, config=config, parameters=model.parameters)

    @staticmethod
    def create_page_increment(model: PageIncrementModel, config: Config, **kwargs) -> PageIncrement:
        return PageIncrement(page_size=model.page_size, start_from_page=model.start_from_page, parameters=model.parameters)

    def create_parent_stream_config(self, model: ParentStreamConfigModel, config: Config, **kwargs) -> ParentStreamConfig:
        declarative_stream = self._create_component_from_model(model.stream, config=config)
        request_option = self._create_component_from_model(model.request_option, config=config) if model.request_option else None
        return ParentStreamConfig(
            parent_key=model.parent_key,
            request_option=request_option,
            stream=declarative_stream,
            partition_field=model.partition_field,
            config=config,
            parameters=model.parameters,
        )

    @staticmethod
    def create_record_filter(model: RecordFilterModel, config: Config, **kwargs) -> RecordFilter:
        return RecordFilter(condition=model.condition, config=config, parameters=model.parameters)

    @staticmethod
    def create_request_path(model: RequestPathModel, config: Config, **kwargs) -> RequestPath:
        return RequestPath(parameters={})

    @staticmethod
    def create_request_option(model: RequestOptionModel, config: Config, **kwargs) -> RequestOption:
        inject_into = RequestOptionType(model.inject_into.value)
        return RequestOption(field_name=model.field_name, inject_into=inject_into, parameters={})

    def create_record_selector(self, model: RecordSelectorModel, config: Config, **kwargs) -> RecordSelector:
        extractor = self._create_component_from_model(model=model.extractor, config=config)
        record_filter = self._create_component_from_model(model.record_filter, config=config) if model.record_filter else None

        return RecordSelector(extractor=extractor, record_filter=record_filter, parameters=model.parameters)

    @staticmethod
    def create_remove_fields(model: RemoveFieldsModel, config: Config, **kwargs) -> RemoveFields:
        return RemoveFields(field_pointers=model.field_pointers, parameters={})

    @staticmethod
    def create_session_token_authenticator(
        model: SessionTokenAuthenticatorModel, config: Config, *, url_base: str, **kwargs
    ) -> SessionTokenAuthenticator:
        return SessionTokenAuthenticator(
            api_url=url_base,
            header=model.header,
            login_url=model.login_url,
            password=model.password,
            session_token=model.session_token,
            session_token_response_key=model.session_token_response_key,
            username=model.username,
            validate_session_url=model.validate_session_url,
            config=config,
            parameters=model.parameters,
        )

    def create_simple_retriever(
        self,
        model: SimpleRetrieverModel,
        config: Config,
        *,
        name: str,
        primary_key: Optional[Union[str, List[str], List[List[str]]]],
        stream_slicer: Optional[StreamSlicer],
    ) -> SimpleRetriever:
        requester = self._create_component_from_model(model=model.requester, config=config, name=name)
        record_selector = self._create_component_from_model(model=model.record_selector, config=config)
        url_base = model.requester.url_base if hasattr(model.requester, "url_base") else requester.get_url_base()
        paginator = (
            self._create_component_from_model(model=model.paginator, config=config, url_base=url_base)
            if model.paginator
            else NoPagination(parameters={})
        )

        stream_slicer = stream_slicer or SinglePartitionRouter(parameters={})
        cursor = stream_slicer if isinstance(stream_slicer, Cursor) else None
        if self._limit_slices_fetched or self._emit_connector_builder_messages:
            return SimpleRetrieverTestReadDecorator(
                name=name,
                paginator=paginator,
                primary_key=primary_key,
                requester=requester,
                record_selector=record_selector,
                stream_slicer=stream_slicer,
                cursor=cursor,
                config=config,
                maximum_number_of_slices=self._limit_slices_fetched,
                parameters=model.parameters,
                disable_retries=self._disable_retries,
            )
        return SimpleRetriever(
            name=name,
            paginator=paginator,
            primary_key=primary_key,
            requester=requester,
            record_selector=record_selector,
            stream_slicer=stream_slicer,
            cursor=cursor,
            config=config,
            parameters=model.parameters,
            disable_retries=self._disable_retries,
        )

    @staticmethod
    def create_spec(model: SpecModel, config: Config, **kwargs) -> Spec:
        return Spec(
            connection_specification=model.connection_specification,
            documentation_url=model.documentation_url,
            advanced_auth=model.advanced_auth,
            parameters={},
        )

    def create_substream_partition_router(self, model: SubstreamPartitionRouterModel, config: Config, **kwargs) -> SubstreamPartitionRouter:
        parent_stream_configs = []
        if model.parent_stream_configs:
            parent_stream_configs.extend(
                [
                    self._create_component_from_model(model=parent_stream_config, config=config)
                    for parent_stream_config in model.parent_stream_configs
                ]
            )

        return SubstreamPartitionRouter(parent_stream_configs=parent_stream_configs, parameters=model.parameters, config=config)

    @staticmethod
    def create_wait_time_from_header(model: WaitTimeFromHeaderModel, config: Config, **kwargs) -> WaitTimeFromHeaderBackoffStrategy:
        return WaitTimeFromHeaderBackoffStrategy(header=model.header, parameters=model.parameters, config=config, regex=model.regex)

    @staticmethod
    def create_wait_until_time_from_header(
        model: WaitUntilTimeFromHeaderModel, config: Config, **kwargs
    ) -> WaitUntilTimeFromHeaderBackoffStrategy:
        return WaitUntilTimeFromHeaderBackoffStrategy(
            header=model.header, parameters=model.parameters, config=config, min_wait=model.min_wait, regex=model.regex
        )

    def get_message_repository(self):
        return self._message_repository
