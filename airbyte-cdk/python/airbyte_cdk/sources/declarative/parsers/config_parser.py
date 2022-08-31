#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod

from airbyte_cdk.sources.declarative.types import ConnectionDefinition


class ConnectionDefinitionParser(ABC):
    """
    Parses a string to a ConnectionDefinition
    """

    @abstractmethod
    def parse(self, config_str: str) -> ConnectionDefinition:
        """Parses the config_str to a ConnectionDefinition"""
