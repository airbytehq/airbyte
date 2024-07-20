from abc import ABC, abstractmethod
from typing import Dict


class Writer(ABC):
    """
    Register a message stream if one doesn't exist. Returns a boolean indicating whether or not a new resource was created.
    """
    @abstractmethod
    def ensure_registered(self, namespace: str, stream_name):
        pass

    """
    Add a row to the writer output
    """
    @abstractmethod
    def add_row(self, namespace: str, stream_name: str, row: Dict):
        pass

    """
    Ensure that all records for the stream have been written to Foundry.
    """
    @abstractmethod
    def ensure_flushed(self, namespace: str, stream_name: str):
        pass
