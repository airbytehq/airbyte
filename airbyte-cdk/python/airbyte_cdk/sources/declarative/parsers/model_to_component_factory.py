#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import importlib
import inspect
import re
from typing import Any, Callable, Dict, List, Mapping, Optional, Type, TypeVar, Union, get_args, get_origin, get_type_hints

from airbyte_cdk.models import Level
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator, JwtAuthenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.selective_authenticator import SelectiveAuthenticator
from airbyte_cdk.sources.declarative.auth.token import (
    ApiKeyAuthenticator,
    BasicHttpAuthenticator,
    BearerAuthenticator,
    LegacySessionTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider, SessionTokenProvider, TokenProvider
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import Decoder, IterableDecoder, JsonDecoder, JsonlDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.incremental import CursorFactory, DatetimeBasedCursor, PerPartitionCursor, ResumableFullRefreshCursor
from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration
from airbyte_cdk.sources.declarative.models import CustomStateMigration
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
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRecordFilter as CustomRecordFilterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRequester as CustomRequesterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRetriever as CustomRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomSchemaLoader as CustomSchemaLoader
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
from airbyte_cdk.sources.declarative.models.declarative_component_schema import IterableDecoder as IterableDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonDecoder as JsonDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonFileSchemaLoader as JsonFileSchemaLoaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonlDecoder as JsonlDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JwtAuthenticator as JwtAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    LegacySessionTokenAuthenticator as LegacySessionTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    LegacyToPerPartitionStateMigration as LegacyToPerPartitionStateMigrationModel,
)
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
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SelectiveAuthenticator as SelectiveAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SessionTokenAuthenticator as SessionTokenAuthenticatorModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SimpleRetriever as SimpleRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SubstreamPartitionRouter as SubstreamPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import WaitTimeFromHeader as WaitTimeFromHeaderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import WaitUntilTimeFromHeader as WaitUntilTimeFromHeaderModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.declarative.partition_routers import CartesianProductStreamSlicer, ListPartitionRouter, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import CompositeErrorHandler, DefaultErrorHandler, HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import (
    ConstantBackoffStrategy,
    ExponentialBackoffStrategy,
    WaitTimeFromHeaderBackoffStrategy,
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator, NoPagination
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy, OffsetIncrement, PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader, InlineSchemaLoader, JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.message import InMemoryMessageRepository, LogAppenderMessageRepositoryDecorator, MessageRepository
from airbyte_cdk.sources.types import Config
from isodate import parse_duration
from pydantic.v1 import BaseModel

ComponentDefinition = Mapping[str, Any]

M = TypeVar("M", bound=BaseModel)
D = TypeVar("D", bound=BaseModel)


class ModelToComponentFactory:
    """
    The default Model > Component Factory implementation.
    The Custom components are built separetely from the default implementations,
    to provide the reasonable decoupling from the standard and Custom implementation build technique.
    """

    def __init__(
        self,
        limit_pages_fetched_per_slice: Optional[int] = None,
        limit_slices_fetched: Optional[int] = None,
        emit_connector_builder_messages: bool = False,
        disable_retries: bool = False,
        message_repository: Optional[MessageRepository] = None,
    ):
        self._init_mappings()
        self._limit_pages_fetched_per_slice = limit_pages_fetched_per_slice
        self._limit_slices_fetched = limit_slices_fetched
        self._emit_connector_builder_messages = emit_connector_builder_messages
        self._disable_retries = disable_retries
        self._message_repository = message_repository or InMemoryMessageRepository(  # type: ignore
            self._evaluate_log_level(emit_connector_builder_messages)
        )
        # support the dependencies constructors with the re-usable parts from this Factory
        self._flags = {
            "_limit_pages_fetched_per_slice": self._limit_pages_fetched_per_slice,
            "_limit_slices_fetched": self._limit_slices_fetched,
            "_emit_connector_builder_messages": self._emit_connector_builder_messages,
            "_disable_retries": self._disable_retries,
            "_message_repository": self._message_repository,
        }

    def _init_mappings(self) -> None:
        self.MODEL_TO_COMPONENT: Dict[Type[BaseModel], Union[Type[ComponentConstructor], Callable[[BaseModel, Mapping[str, Any]], Any]]] = {
            AddedFieldDefinitionModel: AddedFieldDefinition,
            AddFieldsModel: AddFields,
            ApiKeyAuthenticatorModel: ApiKeyAuthenticator,
            BasicHttpAuthenticatorModel: BasicHttpAuthenticator,
            BearerAuthenticatorModel: BearerAuthenticator,
            CheckStreamModel: CheckStream,
            CompositeErrorHandlerModel: CompositeErrorHandler,
            ConstantBackoffStrategyModel: ConstantBackoffStrategy,
            CursorPaginationModel: CursorPaginationStrategy,
            CustomAuthenticatorModel: self.create_custom_component,
            CustomBackoffStrategyModel: self.create_custom_component,
            CustomErrorHandlerModel: self.create_custom_component,
            CustomIncrementalSyncModel: self.create_custom_component,
            CustomRecordExtractorModel: self.create_custom_component,
            CustomRecordFilterModel: self.create_custom_component,
            CustomRequesterModel: self.create_custom_component,
            CustomRetrieverModel: self.create_custom_component,
            CustomSchemaLoader: self.create_custom_component,
            CustomStateMigration: self.create_custom_component,
            CustomPaginationStrategyModel: self.create_custom_component,
            CustomPartitionRouterModel: self.create_custom_component,
            CustomTransformationModel: self.create_custom_component,
            DatetimeBasedCursorModel: DatetimeBasedCursor,
            # TODO: DO NOT CHANGE `DeclarativeStream`
            DeclarativeStreamModel: self.create_declarative_stream,
            DefaultErrorHandlerModel: DefaultErrorHandler,
            DefaultPaginatorModel: DefaultPaginator,
            DpathExtractorModel: DpathExtractor,
            ExponentialBackoffStrategyModel: ExponentialBackoffStrategy,
            SessionTokenAuthenticatorModel: self.create_session_token_authenticator,
            HttpRequesterModel: HttpRequester,
            HttpResponseFilterModel: HttpResponseFilter,
            InlineSchemaLoaderModel: InlineSchemaLoader,
            JsonDecoderModel: JsonDecoder,
            JsonlDecoderModel: JsonlDecoder,
            IterableDecoderModel: IterableDecoder,
            JsonFileSchemaLoaderModel: JsonFileSchemaLoader,
            JwtAuthenticatorModel: JwtAuthenticator,
            LegacyToPerPartitionStateMigrationModel: LegacyToPerPartitionStateMigration,
            # TODO:
            ListPartitionRouterModel: ListPartitionRouter,
            MinMaxDatetimeModel: MinMaxDatetime,
            NoAuthModel: NoAuth,
            NoPaginationModel: NoPagination,
            OAuthAuthenticatorModel: self.create_oauth_authenticator,
            OffsetIncrementModel: OffsetIncrement,
            PageIncrementModel: PageIncrement,
            ParentStreamConfigModel: ParentStreamConfig,
            RecordFilterModel: RecordFilter,
            RecordSelectorModel: RecordSelector,
            RemoveFieldsModel: RemoveFields,
            RequestPathModel: RequestPath,
            RequestOptionModel: RequestOption,
            LegacySessionTokenAuthenticatorModel: LegacySessionTokenAuthenticator,
            SelectiveAuthenticatorModel: self.create_selective_authenticator,
            SimpleRetrieverModel: SimpleRetriever,
            SpecModel: Spec,
            SubstreamPartitionRouterModel: self.create_substream_partition_router,
            WaitTimeFromHeaderModel: WaitTimeFromHeaderBackoffStrategy,
            WaitUntilTimeFromHeaderModel: WaitUntilTimeFromHeaderBackoffStrategy,
        }

        # Needed for the case where we need to perform a second parse on the fields of a custom component
        self.TYPE_NAME_TO_MODEL = {cls.__name__: cls for cls in self.MODEL_TO_COMPONENT}

    def create_component(
        self, model_type: Type[BaseModel], component_definition: ComponentDefinition, config: Config, **kwargs: Any
    ) -> Any:
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

    def _create_component_from_model(self, model: BaseModel, config: Config, **kwargs: Any) -> ComponentConstructor[BaseModel, BaseModel]:
        if model.__class__ not in self.MODEL_TO_COMPONENT:
            raise ValueError(f"{model.__class__} with attributes {model} is not a valid component type")

        component = self.MODEL_TO_COMPONENT.get(model.__class__)
        if not component:
            raise ValueError(f"Could not find constructor for {model.__class__}")

        if inspect.isclass(component) and issubclass(component, ComponentConstructor):
            # Default components flow
            component_instance: ComponentConstructor[BaseModel, BaseModel] = component.build(
                model=model,
                config=config,
                dependency_constructor=self._create_component_from_model,
                additional_flags=self._flags,
                **kwargs,
            )
            return component_instance
        else:
            return component(model=model, config=config, **kwargs)

    def create_legacy_to_per_partition_state_migration(
        self,
        model: LegacyToPerPartitionStateMigrationModel,
        config: Mapping[str, Any],
        declarative_stream: DeclarativeStreamModel,
    ) -> LegacyToPerPartitionStateMigration:
        retriever = declarative_stream.retriever

        # VERIFY
        if not isinstance(retriever, SimpleRetrieverModel):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a DeclarativeStream with a SimpleRetriever. Got {type(retriever)}"
            )

        partition_router = retriever.partition_router
        if not isinstance(partition_router, (SubstreamPartitionRouterModel, CustomPartitionRouterModel)):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a SimpleRetriever with a Substream partition router. Got {type(partition_router)}"
            )
        if not hasattr(partition_router, "parent_stream_configs"):
            raise ValueError("LegacyToPerPartitionStateMigrations can only be applied with a parent stream configuration.")

        return LegacyToPerPartitionStateMigration(declarative_stream.retriever.partition_router, declarative_stream.incremental_sync, config, declarative_stream.parameters)  # type: ignore # The retriever type was already checked

    # TODO: There is no COMPONENT for `SessionTokenAuthenticator`, it should be created at first.
    def create_session_token_authenticator(
        self, model: SessionTokenAuthenticatorModel, config: Config, name: str, decoder: Decoder, **kwargs: Any
    ) -> Union[ApiKeyAuthenticator, BearerAuthenticator]:
        login_requester = self._create_component_from_model(
            model=model.login_requester, config=config, name=f"{name}_login_requester", decoder=decoder
        )
        token_provider = SessionTokenProvider(
            login_requester=login_requester,
            session_token_path=model.session_token_path,
            expiration_duration=parse_duration(model.expiration_duration) if model.expiration_duration else None,
            parameters=model.parameters or {},
            message_repository=self._message_repository,
        )
        if model.request_authentication.type == "Bearer":
            return self.create_bearer_authenticator(
                BearerAuthenticatorModel(type="BearerAuthenticator", api_token=""),  # type: ignore # $parameters has a default value
                config,
                token_provider=token_provider,  # type: ignore # $parameters defaults to None
            )
        else:
            return self._create_component_from_model(
                ApiKeyAuthenticatorModel(type="ApiKeyAuthenticator", api_token="", inject_into=model.request_authentication.inject_into),  # type: ignore # $parameters and headers default to None
                config=config,
                token_provider=token_provider,
            )

    @staticmethod
    def create_bearer_authenticator(
        model: BearerAuthenticatorModel, config: Config, token_provider: Optional[TokenProvider] = None, **kwargs: Any
    ) -> BearerAuthenticator:
        if token_provider is not None and model.api_token != "":
            raise ValueError("If token_provider is set, api_token is ignored and has to be set to empty string.")
        return BearerAuthenticator(
            token_provider=token_provider
            if token_provider is not None
            else InterpolatedStringTokenProvider(api_token=model.api_token or "", config=config, parameters=model.parameters or {}),
            config=config,
            parameters=model.parameters or {},
        )

    def create_custom_component(self, model: BaseModel, config: Config, **kwargs: Any) -> Any:
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
    def _get_class_from_fully_qualified_class_name(full_qualified_class_name: str) -> Any:
        split = full_qualified_class_name.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]
        try:
            return getattr(importlib.import_module(module), class_name)
        except AttributeError:
            raise ValueError(f"Could not load class {full_qualified_class_name}.")

    @staticmethod
    def _derive_component_type_from_type_hints(field_type: Any) -> Optional[str]:
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
    def is_builtin_type(cls: Optional[Type[Any]]) -> bool:
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

    def _create_nested_component(self, model: Any, model_field: str, model_value: Any, config: Config) -> Any:
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
                model_constructor = self.MODEL_TO_COMPONENT.get(parsed_model.__class__)
                constructor_kwargs = inspect.getfullargspec(model_constructor).kwonlyargs
                model_parameters = model_value.get("$parameters", {})
                matching_parameters = {kwarg: model_parameters[kwarg] for kwarg in constructor_kwargs if kwarg in model_parameters}
                return self._create_component_from_model(model=parsed_model, config=config, **matching_parameters)
            except TypeError as error:
                raise error
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
        return isinstance(model_value, dict) and model_value.get("type") is not None

    def create_declarative_stream(self, model: DeclarativeStreamModel, config: Config, **kwargs: Any) -> DeclarativeStream:
        # When constructing a declarative stream, we assemble the incremental_sync component and retriever's partition_router field
        # components if they exist into a single CartesianProductStreamSlicer. This is then passed back as an argument when constructing the
        # Retriever. This is done in the declarative stream not the retriever to support custom retrievers. The custom create methods in
        # the factory only support passing arguments to the component constructors, whereas this performs a merge of all slicers into one.
        combined_slicers = self._merge_stream_slicers(model=model, config=config)

        primary_key = model.primary_key.__root__ if model.primary_key else None
        stop_condition_on_cursor = (
            model.incremental_sync and hasattr(model.incremental_sync, "is_data_feed") and model.incremental_sync.is_data_feed
        )
        client_side_incremental_sync = None
        if (
            model.incremental_sync
            and hasattr(model.incremental_sync, "is_client_side_incremental")
            and model.incremental_sync.is_client_side_incremental
        ):
            if combined_slicers and not isinstance(combined_slicers, (DatetimeBasedCursor, PerPartitionCursor)):
                raise ValueError("Unsupported Slicer is used. PerPartitionCursor should be used here instead")
            client_side_incremental_sync = {
                "date_time_based_cursor": self._create_component_from_model(model=model.incremental_sync, config=config),
                "per_partition_cursor": combined_slicers if isinstance(combined_slicers, PerPartitionCursor) else None,
            }
        transformations = []
        if model.transformations:
            for transformation_model in model.transformations:
                transformations.append(self._create_component_from_model(model=transformation_model, config=config))
        retriever = self._create_component_from_model(
            model=model.retriever,
            config=config,
            name=model.name,
            primary_key=primary_key,
            stream_slicer=combined_slicers,
            stop_condition_on_cursor=stop_condition_on_cursor,
            client_side_incremental_sync=client_side_incremental_sync,
            transformations=transformations,
        )
        cursor_field = model.incremental_sync.cursor_field if model.incremental_sync else None

        if model.state_migrations:
            state_transformations = [
                self._create_component_from_model(state_migration, config, declarative_stream=model)
                for state_migration in model.state_migrations
            ]
        else:
            state_transformations = []

        if model.schema_loader:
            schema_loader = self._create_component_from_model(model=model.schema_loader, config=config)
        else:
            options = model.parameters or {}
            if "name" not in options:
                options["name"] = model.name
            schema_loader = DefaultSchemaLoader(config=config, parameters=options)

        return DeclarativeStream(
            name=model.name or "",
            primary_key=primary_key,
            retriever=retriever,
            schema_loader=schema_loader,
            stream_cursor_field=cursor_field or "",
            state_migrations=state_transformations,
            config=config,
            parameters=model.parameters or {},
        )

    @staticmethod
    def model_has_partition_router(model: DeclarativeStreamModel) -> bool:
        return (
            hasattr(model.retriever, "partition_router")
            and isinstance(model.retriever, SimpleRetrieverModel)
            and model.retriever.partition_router
        )

    def _create_base_slicer(self, model: DeclarativeStreamModel, config: Config) -> Optional[StreamSlicer]:
        stream_slicer = None
        if self.model_has_partition_router(model):
            stream_slicer_model = model.retriever.partition_router
            if isinstance(stream_slicer_model, list):
                stream_slicer: CartesianProductStreamSlicer = CartesianProductStreamSlicer(
                    [self._create_component_from_model(model=slicer, config=config) for slicer in stream_slicer_model], parameters={}
                )
            else:
                stream_slicer: StreamSlicer = self._create_component_from_model(model=stream_slicer_model, config=config)

        return stream_slicer

    def _create_per_partition_cursor(
        self, model: DeclarativeStreamModel, stream_slicer: StreamSlicer, config: Config
    ) -> PerPartitionCursor:
        incremental_sync_model = model.incremental_sync
        return PerPartitionCursor(
            cursor_factory=CursorFactory(
                lambda: self._create_component_from_model(model=incremental_sync_model, config=config),
            ),
            partition_router=stream_slicer,
        )

    def _merge_stream_slicers(self, model: DeclarativeStreamModel, config: Config) -> Optional[StreamSlicer]:
        stream_slicer: Optional[StreamSlicer] = self._create_base_slicer(model, config)

        if model.incremental_sync and stream_slicer:
            return self._create_per_partition_cursor(model, stream_slicer, config)
        elif model.incremental_sync:
            return self._create_component_from_model(model=model.incremental_sync, config=config) if model.incremental_sync else None
        elif hasattr(model.retriever, "paginator") and model.retriever.paginator and not stream_slicer:
            # To incrementally deliver RFR for low-code we're first implementing this for streams that do not use
            # nested state like substreams or those using list partition routers
            return ResumableFullRefreshCursor(parameters={})

        return stream_slicer

    @staticmethod
    def create_min_max_datetime(model: MinMaxDatetimeModel, config: Config, **kwargs: Any) -> MinMaxDatetime:
        return MinMaxDatetime(
            datetime=model.datetime,
            datetime_format=model.datetime_format or "",
            max_datetime=model.max_datetime or "",
            min_datetime=model.min_datetime or "",
            parameters=model.parameters or {},
        )

    def create_oauth_authenticator(self, model: OAuthAuthenticatorModel, config: Config, **kwargs: Any) -> DeclarativeOauth2Authenticator:
        if model.refresh_token_updater:
            return DeclarativeSingleUseRefreshTokenOauth2Authenticator.build(
                model=model, config=config, dependency_constructor=self._create_component_from_model, additional_flags=self._flags
            )
            # ignore type error because fixing it would have a lot of dependencies, revisit later
            # return DeclarativeSingleUseRefreshTokenOauth2Authenticator(  # type: ignore
            #     config,
            #     InterpolatedString.create(model.token_refresh_endpoint, parameters=model.parameters or {}).eval(config),
            #     access_token_name=InterpolatedString.create(
            #         model.access_token_name or "access_token", parameters=model.parameters or {}
            #     ).eval(config),
            #     refresh_token_name=model.refresh_token_updater.refresh_token_name,
            #     expires_in_name=InterpolatedString.create(model.expires_in_name or "expires_in", parameters=model.parameters or {}).eval(
            #         config
            #     ),
            #     client_id=InterpolatedString.create(model.client_id, parameters=model.parameters or {}).eval(config),
            #     client_secret=InterpolatedString.create(model.client_secret, parameters=model.parameters or {}).eval(config),
            #     access_token_config_path=model.refresh_token_updater.access_token_config_path,
            #     refresh_token_config_path=model.refresh_token_updater.refresh_token_config_path,
            #     token_expiry_date_config_path=model.refresh_token_updater.token_expiry_date_config_path,
            #     grant_type=InterpolatedString.create(model.grant_type or "refresh_token", parameters=model.parameters or {}).eval(config),
            #     refresh_request_body=InterpolatedMapping(model.refresh_request_body or {}, parameters=model.parameters or {}).eval(config),
            #     scopes=model.scopes,
            #     token_expiry_date_format=model.token_expiry_date_format,
            #     message_repository=self._message_repository,
            #     refresh_token_error_status_codes=model.refresh_token_updater.refresh_token_error_status_codes,
            #     refresh_token_error_key=model.refresh_token_updater.refresh_token_error_key,
            #     refresh_token_error_values=model.refresh_token_updater.refresh_token_error_values,
            # )
        # ignore type error because fixing it would have a lot of dependencies, revisit later
        return DeclarativeOauth2Authenticator.build(
            model=model,
            config=config,  # type: ignore
            dependency_constructor=self._create_component_from_model,
            additional_flags=self._flags,
        )

        # return DeclarativeOauth2Authenticator(  # type: ignore
        #     access_token_name=model.access_token_name or "access_token",
        #     client_id=model.client_id,
        #     client_secret=model.client_secret,
        #     expires_in_name=model.expires_in_name or "expires_in",
        #     grant_type=model.grant_type or "refresh_token",
        #     refresh_request_body=model.refresh_request_body,
        #     refresh_token=model.refresh_token,
        #     scopes=model.scopes,
        #     token_expiry_date=model.token_expiry_date,
        #     token_expiry_date_format=model.token_expiry_date_format,  # type: ignore
        #     token_expiry_is_time_of_expiration=bool(model.token_expiry_date_format),
        #     token_refresh_endpoint=model.token_refresh_endpoint,
        #     config=config,
        #     parameters=model.parameters or {},
        #     message_repository=self._message_repository,
        # )

    def create_selective_authenticator(self, model: SelectiveAuthenticatorModel, config: Config, **kwargs: Any) -> DeclarativeAuthenticator:
        authenticators = {name: self._create_component_from_model(model=auth, config=config) for name, auth in model.authenticators.items()}
        # SelectiveAuthenticator will return instance of DeclarativeAuthenticator or raise ValueError error
        return SelectiveAuthenticator(  # type: ignore[abstract]
            config=config,
            authenticators=authenticators,
            authenticator_selection_path=model.authenticator_selection_path,
            **kwargs,
        )

    def create_substream_partition_router(
        self, model: SubstreamPartitionRouterModel, config: Config, **kwargs: Any
    ) -> SubstreamPartitionRouter:
        parent_stream_configs = []
        if model.parent_stream_configs:
            parent_stream_configs.extend(
                [
                    self._create_message_repository_substream_wrapper(model=parent_stream_config, config=config)
                    for parent_stream_config in model.parent_stream_configs
                ]
            )

        return SubstreamPartitionRouter(parent_stream_configs=parent_stream_configs, parameters=model.parameters or {}, config=config)

    def _create_message_repository_substream_wrapper(self, model: ParentStreamConfigModel, config: Config) -> Any:
        substream_factory = ModelToComponentFactory(
            limit_pages_fetched_per_slice=self._limit_pages_fetched_per_slice,
            limit_slices_fetched=self._limit_slices_fetched,
            emit_connector_builder_messages=self._emit_connector_builder_messages,
            disable_retries=self._disable_retries,
            message_repository=LogAppenderMessageRepositoryDecorator(
                {"airbyte_cdk": {"stream": {"is_substream": True}}, "http": {"is_auxiliary": True}},
                self._message_repository,
                self._evaluate_log_level(self._emit_connector_builder_messages),
            ),
        )
        return substream_factory._create_component_from_model(model=model, config=config)

    def get_message_repository(self) -> MessageRepository:
        return self._message_repository

    def _evaluate_log_level(self, emit_connector_builder_messages: bool) -> Level:
        return Level.DEBUG if emit_connector_builder_messages else Level.INFO
