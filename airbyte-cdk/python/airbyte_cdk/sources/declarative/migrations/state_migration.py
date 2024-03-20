from abc import abstractmethod
from typing import Any, Mapping


class StateMigration:
    @abstractmethod
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        """
        Return true if the state is of the expected format and should be migrated
        Return false otherwise
        :param stream_state:
        :return:
        """

    @abstractmethod
    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        :param stream_state:
        :return:
        """
