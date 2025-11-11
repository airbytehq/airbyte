#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

from .file_writer import FileWriter


class LocalFileSystemFileWriter(FileWriter):
    def write(self, file_path: Path, content: bytes) -> int:
        """
        Writes the file to the specified location
        """
        with open(str(file_path), "wb") as f:
            f.write(content)

        return file_path.stat().st_size
