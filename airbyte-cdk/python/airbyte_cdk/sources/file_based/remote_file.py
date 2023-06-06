from abc import ABC
from datetime import datetime
from enum import Enum


class FileType(Enum):
    Avro = "avro"
    Csv = "csv"
    Jsonl = "jsonl"
    Parquet = "parquet"


class RemoteFile(ABC):
    """
    A file in a file-based stream.
    """

    def __init__(self, uri: str, last_modified: datetime):
        self.uri = uri
        self.last_modified = last_modified
