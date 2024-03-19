from abc import abstractmethod
from typing import Any, Mapping


class StateMigration:
    @abstractmethod
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        """
        Return false is the state is already migrated
        Raise an exception if the input_state is not of the expected format
        Return true if the state is of the expected format and should be migrated
        :param stream_state:
        :return:
        """

    @abstractmethod
    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        :param stream_state:
        :return:
        """
