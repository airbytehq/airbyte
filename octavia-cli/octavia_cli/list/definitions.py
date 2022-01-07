#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import abc
from enum import Enum
from typing import Union

import airbyte_api_client
from airbyte_api_client.api import destination_definition_api, source_definition_api


class DefinitionType(Enum):
    SOURCE = "source"
    DESTINATION = "destination"


class Definitions(abc.ABC):
    @property
    def api(self) -> Union[source_definition_api.SourceDefinitionApi, destination_definition_api.DestinationDefinitionApi]:
        raise NotImplementedError

    def __init__(self, definition_type: DefinitionType, api_client: airbyte_api_client.ApiClient):
        self.definition_type = definition_type
        self.api_instance = self.api(api_client)

    @property
    def fields_to_display(self):
        return ["name", "docker_repository", "docker_image_tag", f"{self.definition_type.value}_definition_id"]

    @property
    def response_definition_list_field(self):
        return f"{self.definition_type.value}_definitions"

    @abc.abstractmethod
    def list_latest_definitions(api_instance):
        pass

    @property
    def latest_definitions(self):
        return self.list_latest_definitions(self.api_instance)

    def _parse_response(self, api_response):
        definitions = [
            [definition[field] for field in self.fields_to_display] for definition in api_response[self.response_definition_list_field]
        ]
        return definitions

    def __repr__(self):
        definitions = [[f.upper() for f in self.fields_to_display]] + self.latest_definitions
        col_width = max(len(col) for row in definitions for col in row) + 2  # padding
        return "\n".join(["".join(col.ljust(col_width) for col in row) for row in definitions])


class SourceDefinitions(Definitions):
    api = source_definition_api.SourceDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.SOURCE, api_client)

    def list_latest_definitions(self, api_instance):
        api_response = source_definition_api.SourceDefinitionApi.list_latest_source_definitions(api_instance)
        return self._parse_response(api_response)


class DestinationDefinitions(Definitions):
    api = destination_definition_api.DestinationDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.DESTINATION, api_client)

    def list_latest_definitions(self, api_instance):
        api_response = destination_definition_api.DestinationDefinitionApi.list_latest_destination_definitions(api_instance)
        return self._parse_response(api_response)
