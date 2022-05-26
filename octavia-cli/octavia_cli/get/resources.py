#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import abc
from typing import Dict

import airbyte_api_client
from airbyte_api_client.api import source_api, destination_api, connection_api
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody


class BaseResource(abc.ABC):
    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def get_function_name(
        self,
    ) -> str:  # pragma: no cover
        pass

    @property
    def _get_fn(self):
        return getattr(self.api, self.get_function_name)

    @property
    def get_function_kwargs(self) -> dict:
        return {}

    def __init__(self, api_client: airbyte_api_client.ApiClient, workspace_id: str, resource_id: str):
        self.api_instance = self.api(api_client)
        self.workspace_id = workspace_id
        self.resource_id = resource_id

    def get_resource(self) -> Dict:
        api_response = self._get_fn(
            self.api_instance, **self.get_function_kwargs)
        return api_response

    def __repr__(self):
        return str(self.get_resource())


class Source(BaseResource):
    api = source_api.SourceApi
    get_function_name = "get_source"

    @ property
    def get_function_kwargs(self) -> dict:
        return {"source_id_request_body": SourceIdRequestBody(source_id=self.resource_id)}


class Destination(BaseResource):
    api = destination_api.DestinationApi
    get_function_name = "get_destination"

    @ property
    def get_function_kwargs(self) -> dict:
        return {"destination_id_request_body": DestinationIdRequestBody(destination_id=self.resource_id)}


class Connection(BaseResource):
    api = connection_api.ConnectionApi
    get_function_name = "get_connection"

    @ property
    def get_function_kwargs(self) -> dict:
        return {"connection_id_request_body": ConnectionIdRequestBody(connection_id=self.resource_id)}
