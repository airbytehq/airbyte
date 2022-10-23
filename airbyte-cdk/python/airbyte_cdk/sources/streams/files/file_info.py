#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering


@total_ordering
@dataclass
class FileInfo:
    """Class for sharing of metadata"""

    key: str
    size: int
    last_modified: datetime

    @property
    def size_in_megabytes(self) -> float:
        """technically size in 'mebibytes'"""
        return self.size / 1024**2

    def __str__(self) -> str:
        return "Key: %s, LastModified: %s, Size: %.4fMb" % (self.key, self.last_modified.isoformat(), self.size_in_megabytes)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FileInfo):
            return self.key == other.key and self.last_modified == other.last_modified and self.size == other.size
        return False

    def __lt__(self, other: object) -> bool:
        # comparison of less than / greater than for FileInfos is based on last modified
        if isinstance(other, FileInfo):
            return self.last_modified < other.last_modified
        else:
            raise TypeError(f"Can't compare {self.__class__} with {other.__class__}")

    def __hash__(self) -> int:
        return self.key.__hash__()
