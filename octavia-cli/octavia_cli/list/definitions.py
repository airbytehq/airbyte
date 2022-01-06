#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_api_client.api import destination_definition_api, source_definition_api


class DefinitionType:
    SOURCE = "source"
    DESTINATION = "destination"


class Definitions:
    def __init__(self, definition_type, api_client):
        self.definition_type = definition_type
        self.api_instance = self.API(api_client)

    @property
    def fields_to_display(self):
        return ["name", "docker_repository", "docker_image_tag", f"{self.definition_type.value}_definition_id"]

    @property
    def response_definition_list_field(self):
        return f"{self.definition_type.value}_definitions"

    def _retrieve(self):
        api_response = self.LIST_LATEST_DEFINITION(self.api_instance)
        definitions = [
            [definition[field] for field in self.fields_to_display] for definition in api_response[self.response_definition_list_field]
        ]
        return definitions

    def __repr__(self):
        definitions = self._retrieve()
        col_width = max(len(col) for row in definitions for col in row) + 2  # padding
        return "\n".join(["".join(col.ljust(col_width) for col in row) for row in definitions])


class SourceDefinitions(Definitions):
    def __init__(self, api_client):
        super().__init__(DefinitionType.SOURCE, api_client)

    API = source_definition_api.SourceDefinitionApi
    LIST_LATEST_DEFINITION = source_definition_api.SourceDefinitionApi.list_latest_source_definitions


class DestinationDefinitions(Definitions):
    def __init__(self, api_client):
        super().__init__(DefinitionType.DESTINATION, api_client)

    API = destination_definition_api.DestinationDefinitionApi
    LIST_LATEST_DEFINITION = destination_definition_api.DestinationDefinitionApi.list_latest_destination_definitions
