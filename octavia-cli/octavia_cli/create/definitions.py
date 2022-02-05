#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import abc

import click
from airbyte_api_client.api import (
    destination_definition_api,
    destination_definition_specification_api,
    source_definition_api,
    source_definition_specification_api,
)
from airbyte_api_client.exceptions import ApiException
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody


class DefinitionNotFoundError(click.ClickException):
    pass


class BaseDefinition(abc.ABC):
    COMMON_GET_FUNCTION_KWARGS = {"_check_return_type": False}

    specification = None

    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def type(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def get_function_name(
        self,
    ):  # pragma: no cover
        pass

    @property
    def _get_fn(self):
        return getattr(self.api, self.get_function_name)

    @property
    def _get_fn_kwargs(self) -> dict:
        return {}

    def __init__(self, api_client, id: str) -> None:
        self.id = id
        self.api_instance = self.api(api_client)
        self._api_data = self._read()

    def _read(self):
        try:
            return self._get_fn(self.api_instance, **self._get_fn_kwargs, **self.COMMON_GET_FUNCTION_KWARGS)
        except ApiException as e:
            if e.status == 422:
                raise DefinitionNotFoundError(f"Definition {self.id} does not exists on your Airbyte instance.")
            raise e

    def __getattr__(self, name):
        if name in self._api_data:
            return self._api_data.get(name)
        raise AttributeError(f"{self.__class__.__name__}.{name} is invalid.")


class SourceDefinition(BaseDefinition):
    api = source_definition_api.SourceDefinitionApi
    type = "source"
    get_function_name = "get_source_definition"

    @property
    def _get_fn_kwargs(self):
        return {"source_definition_id_request_body": SourceDefinitionIdRequestBody(self.id)}


class SourceDefinitionSpecification(SourceDefinition):
    api = source_definition_specification_api.SourceDefinitionSpecificationApi
    get_function_name = "get_source_definition_specification"


class DestinationDefinition(BaseDefinition):
    api = destination_definition_api.DestinationDefinitionApi
    type = "destination"
    get_function_name = "get_destination_definition"

    @property
    def _get_fn_kwargs(self):
        return {"destination_definition_id_request_body": DestinationDefinitionIdRequestBody(self.id)}


class DestinationDefinitionSpecification(DestinationDefinition):
    api = destination_definition_specification_api.DestinationDefinitionSpecificationApi
    get_function_name = "get_destination_definition_specification"


def factory(definition_type, api_client, definition_id):
    if definition_type == "source":
        definition = SourceDefinition(api_client, definition_id)
        specification = SourceDefinitionSpecification(api_client, definition_id)
    elif definition_type == "destination":
        definition = DestinationDefinition(api_client, definition_id)
        specification = DestinationDefinitionSpecification(api_client, definition_id)
    else:
        raise ValueError(f"{definition_type} does not exist")
    definition.specification = specification
    return definition
