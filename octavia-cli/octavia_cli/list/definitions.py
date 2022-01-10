#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import abc
from enum import Enum
from typing import List, Union

import airbyte_api_client
from airbyte_api_client.api import destination_definition_api, source_definition_api


class DefinitionType(Enum):
    SOURCE = "source"
    DESTINATION = "destination"


class Definitions(abc.ABC):
    @property
    @abc.abstractmethod
    def api(
        self,
    ) -> Union[source_definition_api.SourceDefinitionApi, destination_definition_api.DestinationDefinitionApi]:  # pragma: no cover
        pass

    def __init__(self, definition_type: DefinitionType, api_client: airbyte_api_client.ApiClient):
        self.definition_type = definition_type
        self.api_instance = self.api(api_client)

    @property
    def fields_to_display(self) -> List[str]:
        return ["name", "docker_repository", "docker_image_tag", f"{self.definition_type.value}_definition_id"]

    @property
    def response_definition_list_field(self) -> str:
        return f"{self.definition_type.value}_definitions"

    @property
    @abc.abstractmethod
    def latest_definitions(self) -> List[List[str]]:  # pragma: no cover
        pass

    def _parse_response(self, api_response) -> List[List[str]]:
        definitions = [
            [definition[field] for field in self.fields_to_display] for definition in api_response[self.response_definition_list_field]
        ]
        return definitions

    # TODO alafanechere: declare in a specific formatting module because it will probably be reused
    @staticmethod
    def _compute_col_width(data: List[List[str]], padding: int = 2) -> int:
        """Compute column width for display purposes:
        Find largest column size, add a padding of two characters.
        Returns:
            data (List[List[str]]): Tabular data containing rows and columns.
            padding (int): Number of character to adds to create space between columns.
        Returns:
            col_width (int): The computed column width according to input data.
        """
        col_width = max(len(col) for row in data for col in row) + padding
        return col_width

    # TODO alafanechere: declare in a specific formatting module because it will probably be reused
    @staticmethod
    def _display_as_table(data: List[List[str]]) -> str:
        """Formats tabular input data into a displayable table with columns.
        Args:
            data (List[List[str]]): Tabular data containing rows and columns.
        Returns:
            table (str): String representation of input tabular data.
        """
        col_width = Definitions._compute_col_width(data)
        table = "\n".join(["".join(col.ljust(col_width) for col in row) for row in data])
        return table

    def __repr__(self):
        definitions = [[f.upper() for f in self.fields_to_display]] + self.latest_definitions
        return self._display_as_table(definitions)


class SourceDefinitions(Definitions):
    api = source_definition_api.SourceDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.SOURCE, api_client)

    @property
    def latest_definitions(self) -> List[List[str]]:
        api_response = self.api.list_latest_source_definitions(self.api_instance)
        return self._parse_response(api_response)


class DestinationDefinitions(Definitions):
    api = destination_definition_api.DestinationDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.DESTINATION, api_client)

    @property
    def latest_definitions(self) -> List[List[str]]:
        api_response = self.api.list_latest_destination_definitions(self.api_instance)
        return self._parse_response(api_response)
