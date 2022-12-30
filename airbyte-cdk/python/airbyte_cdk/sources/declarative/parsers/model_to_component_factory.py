#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import importlib
from typing import Any, Callable, Dict, List, Literal, Mapping, Type, Union, get_type_hints

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddedFieldDefinition as AddedFieldDefinitionModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddFields as AddFieldsModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ApiKeyAuthenticator as ApiKeyAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BasicHttpAuthenticator as BasicHttpAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import BearerAuthenticator as BearerAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CartesianProductStreamSlicer as CartesianProductStreamSlicerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CompositeErrorHandler as CompositeErrorHandlerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConstantBackoffStrategy as ConstantBackoffStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CursorPagination as CursorPaginationModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomBackoffStrategy as CustomBackoffStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomPaginationStrategy as CustomPaginationStrategyModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRecordExtractor as CustomRecordExtractorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRetriever as CustomRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomStreamSlicer as CustomStreamSlicerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DatetimeStreamSlicer as DatetimeStreamSlicerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultPaginator as DefaultPaginatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DpathExtractor as DpathExtractorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpResponseFilter as HttpResponseFilterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import InlineSchemaLoader as InlineSchemaLoaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    InterpolatedRequestOptionsProvider as InterpolatedRequestOptionsProviderModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonDecoder as JsonDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonFileSchemaLoader as JsonFileSchemaLoaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ListStreamSlicer as ListStreamSlicerModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import MinMaxDatetime as MinMaxDatetimeModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import NoAuth as NoAuthModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import NoPagination as NoPaginationModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import OffsetIncrement as OffsetIncrementModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import PageIncrement as PageIncrementModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ParentStreamConfig as ParentStreamConfigModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RecordFilter as RecordFilterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RecordSelector as RecordSelectorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RemoveFields as RemoveFieldsModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RequestOption as RequestOptionModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SimpleRetriever as SimpleRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SingleSlice as SingleSliceModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SubstreamSlicer as SubstreamSlicerModel
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import CompositeErrorHandler, DefaultErrorHandler, HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ConstantBackoffStrategy, ExponentialBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator, NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy, OffsetIncrement, PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader, InlineSchemaLoader, JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.stream_slicers import (
    CartesianProductStreamSlicer,
    DatetimeStreamSlicer,
    ListStreamSlicer,
    SingleSlice,
    SubstreamSlicer,
)
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import Config
from pydantic import BaseModel

ComponentDefinition: Union[Literal, Mapping, List]


DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy


def create_component_from_model(model: BaseModel, config: Config, **kwargs) -> Any:
    if model.__class__ not in PYDANTIC_MODEL_TO_CONSTRUCTOR:
        raise ValueError(f"{model.__class__} with attributes {model} is not a valid component type")
    component_constructor = PYDANTIC_MODEL_TO_CONSTRUCTOR.get(model.__class__)
    return component_constructor(model=model, config=config, **kwargs)  # todo tbd check this


def create_added_field_definition(model: AddedFieldDefinitionModel, config: Config) -> AddedFieldDefinition:
    return AddedFieldDefinition(path=model.path, value=model.value)


def create_add_fields(model: AddFieldsModel, config: Config) -> AddFields:
    added_field_definitions = [
        create_component_from_model(model=added_field_definition_model, config=config) for added_field_definition_model in model.fields
    ]
    return AddFields(fields=added_field_definitions, options=model.options)


def create_api_key_authenticator(model: ApiKeyAuthenticatorModel, config: Config) -> ApiKeyAuthenticator:
    return ApiKeyAuthenticator(api_token=model.api_token, header=model.header, config=config, options=model.options)


def create_basic_http_authenticator(model: BasicHttpAuthenticatorModel, config: Config) -> BasicHttpAuthenticator:
    return BasicHttpAuthenticator(password=model.password, username=model.username, config=config, options=model.options)


def create_bearer_authenticator(model: BearerAuthenticatorModel, config: Config) -> BearerAuthenticator:
    return BearerAuthenticator(
        api_token=model.api_token,
        config=config,
        options=model.options,
    )


def create_cartesian_product_slicer(model: CartesianProductStreamSlicerModel, config: Config) -> CartesianProductStreamSlicer:
    stream_slicers = [create_component_from_model(model=stream_slicer_model, config=config) for stream_slicer_model in model.stream_slicers]
    return CartesianProductStreamSlicer(stream_slicers=stream_slicers, options=model.options)


def create_check_stream(model: CheckStreamModel, config: Config):
    return CheckStream(model.stream_names, options={})


def create_composite_error_handler(model: CompositeErrorHandlerModel, config: Config) -> CompositeErrorHandler:
    error_handlers = []
    if model.error_handlers:
        for error_handler_model in model.error_handlers:
            error_handlers.append(create_component_from_model(model=error_handler_model, config=config))
    return CompositeErrorHandler(error_handlers=error_handlers)


def create_constant_backoff_strategy(model: ConstantBackoffStrategyModel, config: Config) -> ConstantBackoffStrategy:
    return ConstantBackoffStrategy(
        backoff_time_in_seconds=model.backoff_time_in_seconds,
        config=config,
        options=model.options,
    )


def create_cursor_pagination(model: CursorPaginationModel, config: Config) -> CursorPaginationStrategy:
    if model.decoder:
        decoder = create_component_from_model(model=model.decoder, config=config)
    else:
        decoder = JsonDecoder()

    return CursorPaginationStrategy(
        cursor_value=model.cursor_value,
        decoder=decoder,
        page_size=model.page_size,
        stop_condition=model.stop_condition,
        config=config,
        options=model.options,
    )


def create_custom_component(model, config: Config) -> type:
    """
    Generically creates a custom component based on the model type and a class_name reference to the custom Python class being
    instantiated. Only the model's additional properties that match the custom class definition are passed to the constructor
    :param model: The Pydantic model of the custom component being created
    :param config: The custom defined connector config
    :return: The declarative component built from the Pydantic model to be used at runtime
    """

    custom_component_class = _get_class_from_fully_qualified_class_name(model.class_name)
    component_fields = get_type_hints(custom_component_class)
    model_args = model.dict()
    model_args["config"] = config
    model_args["options"] = model_args.pop("$options", {})

    # todo: we may need to investigate if we can pull type hints to figure out field types, otherwise type will always need to be defined

    # Pydantic is unable to parse a custom component's fields that are subcomponents into models because their fields and types are not
    # defined in the schema. The fields and types are defined within the Python class implementation. Pydantic can only parse down to
    # the custom component and this code performs a second parse to convert the sub-fields first into models, then declarative components
    for model_field, model_value in model_args.items():
        if _is_component(model_field, model_value):
            model_args[model_field] = _create_nested_component(model, model_field, model_value, config)
        elif isinstance(model_value, list):
            vals = []
            for v in model_value:
                if _is_component(model_field, v):
                    vals.append(_create_nested_component(model, model_field, v, config))
            model_args[model_field] = vals

    kwargs = _get_defaults(model)
    kwargs.update({class_field: model_args[class_field] for class_field in component_fields.keys() if class_field in model_args})
    return custom_component_class(**kwargs)


def _get_defaults(model) -> Dict:
    return {
        "CustomRecordExtractor": {
            "decoder": JsonDecoder(),
        }
    }.get(model.type, {})


def _create_nested_component(model, model_field: str, model_value: Any, config: Config) -> Any:
    type_name = model_value.get("type", None)
    if not type_name:
        raise ValueError(
            f"Error while parsing custom component {model.class_name}. Subcomponent field '{model_field}' should have a 'type' specified"
        )
    model_type = TYPE_NAME_TO_MODEL.get(type_name, None)
    if model_type:
        parsed_model = model_type.parse_obj(model_value)
        return create_component_from_model(model=parsed_model, config=config)
    else:
        raise ValueError(
            f"Error creating custom component {model.class_name}. Subcomponent creation has not been implemented for '{type_name}'"
        )


def _is_component(model_field: str, model_value: Any) -> bool:
    return isinstance(model_value, dict) and model_field != "options" and model_field != "config"


def create_datetime_stream_slicer(model: DatetimeStreamSlicerModel, config: Config) -> DatetimeStreamSlicer:
    start_datetime = (
        model.start_datetime if isinstance(model.start_datetime, str) else create_min_max_datetime(model.start_datetime, config)
    )
    end_datetime = model.end_datetime if isinstance(model.end_datetime, str) else create_min_max_datetime(model.end_datetime, config)
    return DatetimeStreamSlicer(
        cursor_field=model.cursor_field,
        datetime_format=model.datetime_format,
        end_datetime=end_datetime,
        start_datetime=start_datetime,
        step=model.step,
        end_time_option=model.end_time_option,
        lookback_window=model.lookback_window,
        start_time_option=model.start_time_option,
        stream_state_field_end=model.stream_state_field_end,
        stream_state_field_start=model.stream_state_field_start,
        config=config,
        options=model.options,
    )


def create_declarative_stream(model: DeclarativeStreamModel, config: Config) -> DeclarativeStream:
    retriever = create_component_from_model(model=model.retriever, config=config)

    if model.schema_loader:
        schema_loader = create_component_from_model(model=model.schema_loader, config=config)
    else:
        schema_loader = DefaultSchemaLoader(config=config, options=model.options)

    transformations = []
    if model.transformations:
        for transformation_model in model.transformations:
            transformations.append(create_component_from_model(model=transformation_model, config=config))
    return DeclarativeStream(
        checkpoint_interval=model.checkpoint_interval,
        name=model.name,
        primary_key=model.primary_key,
        retriever=retriever,
        schema_loader=schema_loader,
        stream_cursor_field=model.stream_cursor_field or [],
        transformations=transformations,
        config=config,
        options={},
    )


def create_default_error_handler(model: DefaultErrorHandlerModel, config: Config) -> DefaultErrorHandler:
    backoff_strategies = []
    if model.backoff_strategies:
        for backoff_strategy_model in model.backoff_strategies:
            backoff_strategies.append(create_component_from_model(model=backoff_strategy_model, config=config))
    else:
        backoff_strategies.append(DEFAULT_BACKOFF_STRATEGY(config=config, options=model.options))

    response_filters = []
    if model.response_filters:
        for response_filter_model in model.response_filters:
            response_filters.append(create_component_from_model(model=response_filter_model, config=config))
    else:
        response_filters.append(
            HttpResponseFilter(
                ResponseAction.RETRY, http_codes=HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS, config=config, options=model.options
            )
        )
        response_filters.append(HttpResponseFilter(ResponseAction.IGNORE, config=config, options=model.options))

    return DefaultErrorHandler(
        backoff_strategies=backoff_strategies,
        max_retries=model.max_retries,
        response_filters=response_filters,
        config=config,
        options=model.options,
    )


def create_default_paginator(model: DefaultPaginatorModel, config: Config, **kwargs) -> DefaultPaginator:
    decoder = create_component_from_model(model=model.decoder, config=config) if model.decoder else JsonDecoder()
    page_size_option = create_component_from_model(model=model.page_size_option, config=config) if model.page_size_option else None
    page_token_option = create_component_from_model(model=model.page_token_option, config=config) if model.page_token_option else None
    pagination_strategy = create_component_from_model(model=model.pagination_strategy, config=config)

    url_base = (
        kwargs["url_base"] if "url_base" in kwargs else model.url_base
    )  # todo remove this later, just want to spike an example of passing args from another components fields

    return DefaultPaginator(
        decoder=decoder,
        page_size_option=page_size_option,
        page_token_option=page_token_option,
        pagination_strategy=pagination_strategy,
        url_base=url_base,
        config=config,
        options=model.options,
    )


def create_dpath_extractor(model: DpathExtractorModel, config: Config) -> DpathExtractor:
    decoder = create_component_from_model(model.decoder, config=config) if model.decoder else JsonDecoder()
    return DpathExtractor(decoder=decoder, field_pointer=model.field_pointer, config=config, options=model.options)


def create_http_requester(model: HttpRequesterModel, config: Config) -> HttpRequester:
    authenticator = create_component_from_model(model=model.authenticator, config=config) if model.authenticator else None
    error_handler = (
        create_component_from_model(model=model.error_handler, config=config)
        if model.error_handler
        else DefaultErrorHandler(backoff_strategies=[], response_filters=[], config=config, options=model.options)
    )
    request_options_provider = (
        create_component_from_model(model=model.request_options_provider, config=config) if model.request_options_provider else None
    )

    return HttpRequester(
        name=model.name,
        url_base=model.url_base,
        path=model.path,
        authenticator=authenticator or None,
        error_handler=error_handler,
        http_method=model.http_method,
        request_options_provider=request_options_provider,
        config=config,
        options=model.options,
    )


def create_http_response_filter(model: HttpResponseFilterModel, config: Config) -> HttpResponseFilter:
    action = ResponseAction(model.action.value)
    http_codes = set(model.http_codes)  # JSON schema notation has no set data type. The schema enforces an array of unique elements
    return HttpResponseFilter(
        action=action,
        error_message=model.error_message or "",
        error_message_contains=model.error_message_contains,
        http_codes=http_codes,
        predicate=model.predicate or "",
        config=config,
        options=model.options,
    )


def create_inline_schema_loader(model: InlineSchemaLoaderModel, config: Config) -> InlineSchemaLoader:
    return InlineSchemaLoader(schema=model.schema_, options={})


def create_interpolated_request_options_provider(
    model: InterpolatedRequestOptionsProviderModel, config: Config
) -> InterpolatedRequestOptionsProvider:
    return InterpolatedRequestOptionsProvider(
        request_body_data=model.request_body_data,
        request_body_json=model.request_body_json,
        request_headers=model.request_headers,
        request_parameters=model.request_parameters,
        config=config,
        options=model.options,
    )


def create_json_decoder(model: JsonDecoderModel, config: Config) -> JsonDecoder:
    return JsonDecoder()


def create_json_file_schema_loader(model: JsonFileSchemaLoaderModel, config: Config) -> JsonFileSchemaLoader:
    return JsonFileSchemaLoader(file_path=model.file_path, config=config, options=model.options)


def create_list_stream_slicer(model: ListStreamSlicerModel, config: Config) -> ListStreamSlicer:
    return ListStreamSlicer(
        cursor_field=model.cursor_field,
        request_option=model.request_option,
        slice_values=model.slice_values,
        config=config,
        options=model.options,
    )


def create_min_max_datetime(model: MinMaxDatetimeModel, config: Config) -> MinMaxDatetime:
    return MinMaxDatetime(
        datetime=model.datetime,
        datetime_format=model.datetime_format,
        max_datetime=model.max_datetime,
        min_datetime=model.min_datetime,
        options=model.options,
    )


def create_no_auth(model: NoAuthModel, config: Config) -> NoAuth:
    return NoAuth(options=model.options)


def create_no_pagination(model: NoPaginationModel, config: Config, **kwargs) -> NoPagination:
    return NoPagination()


def create_offset_increment(model: OffsetIncrementModel, config: Config) -> OffsetIncrement:
    return OffsetIncrement(page_size=model.page_size, config=config, options=model.options)


def create_page_increment(model: PageIncrementModel, config: Config) -> PageIncrement:
    return PageIncrement(page_size=model.page_size, start_from_page=model.start_from_page, options=model.options)


def create_parent_stream_config(model: ParentStreamConfigModel, config: Config) -> ParentStreamConfig:
    declarative_stream = create_component_from_model(model.stream, config=config)
    request_option = create_component_from_model(model.request_option, config=config) if model.request_option else None
    return ParentStreamConfig(
        parent_key=model.parent_key, request_option=request_option, stream=declarative_stream, stream_slice_field=model.stream_slice_field
    )


def create_record_filter(model: RecordFilterModel, config: Config) -> RecordFilter:
    return RecordFilter(condition=model.condition, config=config, options=model.options)


def create_request_option(model: RequestOptionModel, config: Config) -> RequestOption:
    inject_into = RequestOptionType(model.inject_into.value)  # todo does this work?
    return RequestOption(field_name=model.field_name, inject_into=inject_into)


def create_record_selector(model: RecordSelectorModel, config: Config) -> RecordSelector:
    extractor = create_component_from_model(model=model.extractor, config=config)
    record_filter = create_component_from_model(model.record_filter, config=config) if model.record_filter else None

    return RecordSelector(extractor=extractor, record_filter=record_filter, options=model.options)


def create_remove_fields(model: RemoveFieldsModel, config: Config) -> RemoveFields:
    return RemoveFields(field_pointers=model.field_pointers)


def create_simple_retriever(model: SimpleRetrieverModel, config: Config) -> SimpleRetriever:
    requester = create_component_from_model(model=model.requester, config=config)
    record_selector = create_component_from_model(model=model.record_selector, config=config)
    paginator = (
        create_component_from_model(model=model.paginator, config=config, url_base=model.requester.url_base)
        if model.paginator
        else NoPagination()
    )
    stream_slicer = create_component_from_model(model=model.stream_slicer, config=config) if model.stream_slicer else SingleSlice()

    return SimpleRetriever(
        name=model.name,
        paginator=paginator,
        primary_key=model.primary_key,
        requester=requester,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        config=config,
        options=model.options,
    )


def create_single_slice(model: SingleSliceModel, config: Config) -> SingleSlice:
    return SingleSlice()


def create_spec(model: SpecModel, config: Config) -> Spec:
    return Spec(connection_specification=model.connection_specification, documentation_url=model.documentation_url, options={})


def create_substream_slicer(model: SubstreamSlicerModel, config: Config) -> SubstreamSlicer:
    parent_stream_configs = []
    if model.parent_stream_configs:
        parent_stream_configs.extend(
            [create_component_from_model(model=parent_stream_config, config=config) for parent_stream_config in model.parent_stream_configs]
        )

    return SubstreamSlicer(parent_stream_configs=parent_stream_configs, options=model.options)


class ModelToComponentFactory:
    @staticmethod
    def create_component(model_type: Type[BaseModel], component_definition: ComponentDefinition, config: Config) -> type:
        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(f"Expected manifest component of type {model_type}, but received {component_type} instead")

        declarative_component_model = model_type.parse_obj(component_definition)

        if not isinstance(declarative_component_model, model_type):
            raise ValueError(f"Expected DeclarativeStream component, but received {declarative_component_model.__class__.__name__}")

        return create_component_from_model(model=declarative_component_model, config=config)


# todo this is better up top but need to make it a forward reference
PYDANTIC_MODEL_TO_CONSTRUCTOR: [Type[BaseModel], Callable] = {
    AddedFieldDefinitionModel: create_added_field_definition,
    AddFieldsModel: create_add_fields,
    ApiKeyAuthenticatorModel: create_api_key_authenticator,
    BasicHttpAuthenticatorModel: create_basic_http_authenticator,
    BearerAuthenticatorModel: create_bearer_authenticator,
    CheckStreamModel: create_check_stream,
    CartesianProductStreamSlicerModel: create_cartesian_product_slicer,
    CompositeErrorHandlerModel: create_composite_error_handler,
    ConstantBackoffStrategyModel: create_constant_backoff_strategy,
    CursorPaginationModel: create_cursor_pagination,
    CustomBackoffStrategyModel: create_custom_component,
    CustomRecordExtractorModel: create_custom_component,
    CustomRetrieverModel: create_custom_component,
    CustomPaginationStrategyModel: create_custom_component,
    CustomStreamSlicerModel: create_custom_component,
    DatetimeStreamSlicerModel: create_datetime_stream_slicer,
    DeclarativeStreamModel: create_declarative_stream,
    DefaultErrorHandlerModel: create_default_error_handler,
    DefaultPaginatorModel: create_default_paginator,
    DpathExtractorModel: create_dpath_extractor,
    HttpRequesterModel: create_http_requester,
    HttpResponseFilterModel: create_http_response_filter,
    InlineSchemaLoaderModel: create_inline_schema_loader,
    InterpolatedRequestOptionsProviderModel: create_interpolated_request_options_provider,
    JsonDecoderModel: create_json_decoder,
    JsonFileSchemaLoaderModel: create_json_file_schema_loader,
    ListStreamSlicerModel: create_list_stream_slicer,
    MinMaxDatetimeModel: create_min_max_datetime,
    NoAuthModel: create_no_auth,
    NoPaginationModel: create_no_pagination,
    OffsetIncrementModel: create_offset_increment,
    PageIncrementModel: create_page_increment,
    ParentStreamConfigModel: create_parent_stream_config,
    RecordFilterModel: create_record_filter,
    RecordSelectorModel: create_record_selector,
    RemoveFieldsModel: create_remove_fields,
    RequestOptionModel: create_request_option,
    SimpleRetrieverModel: create_simple_retriever,
    SingleSliceModel: create_single_slice,
    SpecModel: create_spec,
    SubstreamSlicerModel: create_substream_slicer,
}


# Needed for the case where we need to perform a second parse on the fields of a custom component
TYPE_NAME_TO_MODEL = {cls.__name__.partition("Model")[0]: cls for cls in PYDANTIC_MODEL_TO_CONSTRUCTOR}


def _get_class_from_fully_qualified_class_name(class_name: str):
    split = class_name.split(".")
    module = ".".join(split[:-1])
    class_name = split[-1]
    return getattr(importlib.import_module(module), class_name)
