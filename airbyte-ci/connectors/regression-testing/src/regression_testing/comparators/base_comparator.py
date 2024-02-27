from abc import ABC, abstractmethod

from dagger import Container
from ..utils import ConnectorUnderTest


class BaseComparator(ABC):
    """
    Interface to be shared between the file comparator and the database comparator(s)
    """

    @abstractmethod
    async def compare(self, control_connector: ConnectorUnderTest, target_connector: ConnectorUnderTest) -> Container:
        ...
