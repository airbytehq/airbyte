#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
    def size_in_megabytes(self):
        return self.size / 1024 ** 2

    def __str__(self):
        return "Key: %s, LastModified: %s, Size: %.4fMb" % (self.key, self.last_modified.isoformat(), self.size_in_megabytes)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, str):
            return self.key == other
        return self.key == other.key

    def __lt__(self, other):
        if isinstance(other, str):
            return self.key < other
        return self.key < other.key

    def __hash__(self):
        return self.key.__hash__()
