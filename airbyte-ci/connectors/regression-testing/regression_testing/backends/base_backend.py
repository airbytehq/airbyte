from abc import ABC, abstractmethod


class BaseBackend(ABC):  # TODO
    """
    Interface to be shared between the file backend and the database backend(s)
    """

    @abstractmethod
    def write(self):
        ...

    @abstractmethod
    def read(self):
        ...

    @abstractmethod
    def compare(self):
        ...
