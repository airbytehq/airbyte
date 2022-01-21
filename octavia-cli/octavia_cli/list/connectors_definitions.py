#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import abc
from enum import Enum
from typing import Callable, List, Union

import airbyte_api_client
from airbyte_api_client.api import destination_definition_api, source_definition_api


class DefinitionType(Enum):
    SOURCE = "source"
    DESTINATION = "destination"


class ConnectorsDefinitions(abc.ABC):
    LIST_LATEST_DEFINITIONS_KWARGS = {"_check_return_type": False}

    @property
    @abc.abstractmethod
    def api(
        self,
    ) -> Union[source_definition_api.SourceDefinitionApi, destination_definition_api.DestinationDefinitionApi]:  # pragma: no cover
        pass

    def __init__(self, definition_type: DefinitionType, api_client: airbyte_api_client.ApiClient, list_latest_definitions: Callable):
        self.definition_type = definition_type
        self.api_instance = self.api(api_client)
        self.list_latest_definitions = list_latest_definitions

    @property
    def fields_to_display(self) -> List[str]:
        return ["name", "dockerRepository", "dockerImageTag", f"{self.definition_type.value}DefinitionId"]

    @property
    def response_definition_list_field(self) -> str:
        return f"{self.definition_type.value}_definitions"

    def _parse_response(self, api_response) -> List[List[str]]:
        definitions = [
            [definition[field] for field in self.fields_to_display] for definition in api_response[self.response_definition_list_field]
        ]
        return definitions

    @property
    def latest_definitions(self) -> List[List[str]]:
        api_response = self.list_latest_definitions(self.api_instance, **self.LIST_LATEST_DEFINITIONS_KWARGS)
        return self._parse_response(api_response)

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
    def _camelcased_to_uppercased_spaced(camelcased: str) -> str:
        """Util function to transform a camelCase string to a UPPERCASED SPACED string
        e.g: dockerImageName -> DOCKER IMAGE NAME
        Args:
            camelcased (str): The camel cased string to convert.

        Returns:
            (str): The converted UPPERCASED SPACED string
        """
        return "".join(map(lambda x: x if x.islower() else " " + x, camelcased)).upper()

    # TODO alafanechere: declare in a specific formatting module because it will probably be reused
    @staticmethod
    def _display_as_table(data: List[List[str]]) -> str:
        """Formats tabular input data into a displayable table with columns.
        Args:
            data (List[List[str]]): Tabular data containing rows and columns.
        Returns:
            table (str): String representation of input tabular data.
        """
        col_width = ConnectorsDefinitions._compute_col_width(data)
        table = "\n".join(["".join(col.ljust(col_width) for col in row) for row in data])
        return table

    # TODO alafanechere: declare in a specific formatting module because it will probably be reused
    @staticmethod
    def _format_column_names(camelcased_column_names: List[str]) -> List[str]:
        """Format camel cased column names to uppercased spaced column names

        Args:
            camelcased_column_names (List[str]): Column names in camel case.

        Returns:
            (List[str]): Column names in uppercase with spaces.
        """
        return [ConnectorsDefinitions._camelcased_to_uppercased_spaced(column_name) for column_name in camelcased_column_names]

    def __repr__(self):
        definitions = [self._format_column_names(self.fields_to_display)] + self.latest_definitions
        return self._display_as_table(definitions)


class SourceConnectorsDefinitions(ConnectorsDefinitions):
    api = source_definition_api.SourceDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.SOURCE, api_client, self.api.list_latest_source_definitions)


class DestinationConnectorsDefinitions(ConnectorsDefinitions):
    api = destination_definition_api.DestinationDefinitionApi

    def __init__(self, api_client: airbyte_api_client.ApiClient):
        super().__init__(DefinitionType.DESTINATION, api_client, self.api.list_latest_destination_definitions)
