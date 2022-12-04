#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
import json
from typing import Optional, Union

import airbyte_api_client
import click
from airbyte_api_client.api import destination_api, source_api, web_backend_api
from airbyte_api_client.model.destination_id_request_body import DestinationIdRequestBody
from airbyte_api_client.model.destination_read import DestinationRead
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.source_read import SourceRead
from airbyte_api_client.model.web_backend_connection_read import WebBackendConnectionRead
from airbyte_api_client.model.web_backend_connection_request_body import WebBackendConnectionRequestBody
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody


class DuplicateResourceError(click.ClickException):
    pass


class ResourceNotFoundError(click.ClickException):
    pass


class BaseResource(abc.ABC):
    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def name(
        self,
    ) -> str:  # pragma: no cover
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
    @abc.abstractmethod
    def get_payload(
        self,
    ):  # pragma: no cover
        pass

    @property
    @abc.abstractmethod
    def list_for_workspace_function_name(
        self,
    ) -> str:  # pragma: no cover
        pass

    @property
    def _list_for_workspace_fn(self):
        return getattr(self.api, self.list_for_workspace_function_name)

    @property
    def list_for_workspace_payload(
        self,
    ):
        return WorkspaceIdRequestBody(workspace_id=self.workspace_id)

    def __init__(
        self,
        api_client: airbyte_api_client.ApiClient,
        workspace_id: str,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
    ):
        if resource_id is None and resource_name is None:
            raise ValueError("resource_id and resource_name keyword arguments can't be both None.")
        if resource_id is not None and resource_name is not None:
            raise ValueError("resource_id and resource_name keyword arguments can't be both set.")
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.api_instance = self.api(api_client)
        self.workspace_id = workspace_id

    def _find_by_resource_name(
        self,
    ) -> Union[WebBackendConnectionRead, SourceRead, DestinationRead]:
        """Retrieve a remote resource from its name by listing the available resources on the Airbyte instance.

        Raises:
            ResourceNotFoundError: Raised if no resource was found with the current resource_name.
            DuplicateResourceError:  Raised if multiple resources were found with the current resource_name.

        Returns:
            Union[WebBackendConnectionRead, SourceRead, DestinationRead]: The remote resource model instance.
        """

        api_response = self._list_for_workspace_fn(self.api_instance, self.list_for_workspace_payload)
        matching_resources = []
        for resource in getattr(api_response, f"{self.name}s"):
            if resource.name == self.resource_name:
                matching_resources.append(resource)
        if not matching_resources:
            raise ResourceNotFoundError(f"The {self.name} {self.resource_name} was not found in your current Airbyte workspace.")
        if len(matching_resources) > 1:
            raise DuplicateResourceError(
                f"{len(matching_resources)} {self.name}s with the name {self.resource_name} were found in your current Airbyte workspace."
            )
        return matching_resources[0]

    def _find_by_resource_id(
        self,
    ) -> Union[WebBackendConnectionRead, SourceRead, DestinationRead]:
        """Retrieve a remote resource from its id by calling the get endpoint of the resource type.

        Returns:
            Union[WebBackendConnectionRead, SourceRead, DestinationRead]: The remote resource model instance.
        """
        return self._get_fn(self.api_instance, self.get_payload)

    def get_remote_resource(self) -> Union[WebBackendConnectionRead, SourceRead, DestinationRead]:
        """Retrieve a remote resource with a resource_name or a resource_id

        Returns:
            Union[WebBackendConnectionRead, SourceRead, DestinationRead]: The remote resource model instance.
        """
        if self.resource_id is not None:
            return self._find_by_resource_id()
        else:
            return self._find_by_resource_name()

    def to_json(self) -> str:
        """Get the JSON representation of the remote resource model instance.

        Returns:
            str: The JSON representation of the remote resource model instance.
        """
        return json.dumps(self.get_remote_resource().to_dict())


class Source(BaseResource):
    name = "source"
    api = source_api.SourceApi
    get_function_name = "get_source"
    list_for_workspace_function_name = "list_sources_for_workspace"

    @property
    def get_payload(self) -> Optional[SourceIdRequestBody]:
        """Defines the payload to retrieve the remote source according to its resource_id.
        Returns:
            SourceIdRequestBody: The SourceIdRequestBody payload.
        """
        return SourceIdRequestBody(self.resource_id)


class Destination(BaseResource):
    name = "destination"
    api = destination_api.DestinationApi
    get_function_name = "get_destination"
    list_for_workspace_function_name = "list_destinations_for_workspace"

    @property
    def get_payload(self) -> Optional[DestinationIdRequestBody]:
        """Defines the payload to retrieve the remote destination according to its resource_id.
        Returns:
            DestinationIdRequestBody: The DestinationIdRequestBody payload.
        """
        return DestinationIdRequestBody(self.resource_id)


class Connection(BaseResource):
    name = "connection"
    api = web_backend_api.WebBackendApi
    get_function_name = "web_backend_get_connection"
    list_for_workspace_function_name = "web_backend_list_connections_for_workspace"

    @property
    def get_payload(self) -> Optional[WebBackendConnectionRequestBody]:
        """Defines the payload to retrieve the remote connection according to its resource_id.
        Returns:
            WebBackendConnectionRequestBody: The WebBackendConnectionRequestBody payload.
        """
        return WebBackendConnectionRequestBody(with_refreshed_catalog=False, connection_id=self.resource_id)
