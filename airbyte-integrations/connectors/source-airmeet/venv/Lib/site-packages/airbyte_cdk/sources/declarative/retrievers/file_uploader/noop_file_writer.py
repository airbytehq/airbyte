#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

from .file_writer import FileWriter


class NoopFileWriter(FileWriter):
    NOOP_FILE_SIZE = -1

    def write(self, file_path: Path, content: bytes) -> int:
        """
        Noop file writer
        """
        return self.NOOP_FILE_SIZE
