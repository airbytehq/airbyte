from abc import ABC, abstractmethod
from typing import Mapping, Any, TypeVar

StateType = TypeVar('StateType', bound='State')


class State(ABC):
    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        """ Returns a dictionary representation of this state object"""

    @staticmethod
    @abstractmethod
    def from_dict(d: Mapping[str, Any]) -> StateType:
        """ Parses the dictionary into a state object """
