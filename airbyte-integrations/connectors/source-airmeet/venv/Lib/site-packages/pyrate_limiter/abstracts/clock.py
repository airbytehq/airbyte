from abc import ABC
from abc import abstractmethod
from typing import Awaitable
from typing import Union


class AbstractClock(ABC):
    """Clock that return timestamp for `now`"""

    @abstractmethod
    def now(self) -> Union[int, Awaitable[int]]:
        """Get time as of now, in miliseconds"""
