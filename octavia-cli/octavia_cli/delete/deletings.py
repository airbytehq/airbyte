#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import abc

import airbyte_api_client
from airbyte_api_client.api import connection_api, destination_api, destination_definition_api, source_api, source_definition_api
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from click import ClickException


class FailedToDeleteError(ClickException):
    pass


class BaseDeleting(abc.ABC):
    COMMON_DELETE_FUNCTION_KWARGS = {"_check_return_type": False}
    id = None

    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def delete_function_name(
        self,
    ) -> str:  # pragma: no cover
        pass

    @property
    def _delete_fn(self):
        return getattr(self.api, self.delete_function_name)

    @property
    def delete_function_kwargs(self) -> dict:
        return {}

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        self.api_instance = self.api(api_client)

    def deleting(self) -> str:
        try:
            self._delete_fn(self.api_instance, **self.delete_function_kwargs, **self.COMMON_DELETE_FUNCTION_KWARGS)
            return "Successfully deleted Airbyte resource with ID: " + self.id
        except airbyte_api_client.ApiException as api_error:
            raise FailedToDeleteError(api_error.body)

    def __repr__(self):
        res = self.deleting()
        return res


class SourceConnectorsDefinitions(BaseDeleting):
    api = source_definition_api.SourceDefinitionApi
    delete_function_name = "delete_source_definition"

    def __init__(self, api_client: airbyte_api_client.ApiClient, source_definition_id: str):
        self.id = source_definition_id
        super().__init__(api_client)

    @property
    def delete_function_kwargs(self) -> dict:
        return {"source_definition_id_request_body": SourceDefinitionIdRequestBody(source_definition_id=self.id)}


class DestinationConnectorsDefinitions(BaseDeleting):
    api = destination_definition_api.DestinationDefinitionApi
    delete_function_name = "delete_destination_definition"

    def __init__(self, api_client: airbyte_api_client.ApiClient, destination_definition_id: str):
        self.id = destination_definition_id
        super().__init__(api_client)

    @property
    def delete_function_kwargs(self) -> dict:
        return {"destination_definition_id_request_body": DestinationDefinitionIdRequestBody(destination_definition_id=self.id)}


class Sources(BaseDeleting):
    api = source_api.SourceApi
    delete_function_name = "delete_source"

    def __init__(self, api_client: airbyte_api_client.ApiClient, source_id: str):
        self.id = source_id
        super().__init__(api_client)

    @property
    def delete_function_kwargs(self) -> dict:
        return {"source_id_request_body": SourceIdRequestBody(source_id=self.id)}


class Destinations(BaseDeleting):
    api = destination_api.DestinationApi
    delete_function_name = "delete_destination"

    def __init__(self, api_client: airbyte_api_client.ApiClient, destination_id: str):
        self.id = destination_id
        super().__init__(api_client)

    @property
    def delete_function_kwargs(self) -> dict:
        return {"destination_id_request_body": DestinationIdRequestBody(destination_id=self.id)}


class Connections(BaseDeleting):
    api = connection_api.ConnectionApi
    delete_function_name = "delete_connection"

    def __init__(self, api_client: airbyte_api_client.ApiClient, connection_id: str):
        self.id = connection_id
        super().__init__(api_client)

    @property
    def delete_function_kwargs(self) -> dict:
        return {"connection_id_request_body": ConnectionIdRequestBody(connection_id=self.id)}
