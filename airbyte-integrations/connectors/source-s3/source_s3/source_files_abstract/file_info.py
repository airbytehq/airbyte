#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering


@total_ordering
@dataclass
class FileInfo:
    """Class for sharing of metadate"""

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

    @classmethod
    def create_by_local_file(cls, filepath: str) -> "FileInfo":
        "Generates a FileInfo instance. This function can be used for tests"
        if not os.path.exists(filepath):
            return cls(key=filepath, size=0, last_modified=datetime.now())
        return cls(key=filepath, size=os.stat(filepath).st_size, last_modified=datetime.fromtimestamp(os.path.getmtime(filepath)))

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
