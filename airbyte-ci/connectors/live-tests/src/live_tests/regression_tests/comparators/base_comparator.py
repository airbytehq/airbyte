# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod

from dagger import Container

from live_tests.commons.models import ConnectorUnderTest


class BaseComparator(ABC):
    """
    Interface to be shared between the file comparator and the database comparator(s)
    """

    @abstractmethod
    async def compare(self, control_connector: ConnectorUnderTest, target_connector: ConnectorUnderTest) -> Container:
        ...
