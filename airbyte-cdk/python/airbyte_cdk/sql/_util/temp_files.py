# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Internal helper functions for working with temporary files."""

from __future__ import annotations

import json
import tempfile
import time
import warnings
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

from airbyte_cdk.sql.constants import TEMP_DIR_OVERRIDE

if TYPE_CHECKING:
    from collections.abc import Generator


@contextmanager
def as_temp_files(files_contents: list[dict[str, Any] | str]) -> Generator[list[str], Any, None]:
    """Write the given contents to temporary files and yield the file paths as strings."""
    temp_files: list[Any] = []
    try:
        for content in files_contents:
            use_json = isinstance(content, dict)
            temp_file = tempfile.NamedTemporaryFile(  # noqa: SIM115  # Avoiding context manager
                mode="w+t",
                delete=False,
                encoding="utf-8",
                dir=TEMP_DIR_OVERRIDE or None,
                suffix=".json" if use_json else ".txt",
            )
            temp_file.write(
                json.dumps(content) if isinstance(content, dict) else content,
            )
            temp_file.flush()
            # Don't close the file yet (breaks Windows)
            # temp_file.close()
            temp_files.append(temp_file)
        yield [file.name for file in temp_files]
    finally:
        for temp_file in temp_files:
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    with suppress(Exception):
                        temp_file.close()

                    Path(temp_file.name).unlink(missing_ok=True)

                    break  # File was deleted successfully. Move on.
                except Exception as ex:
                    if attempt < max_attempts - 1:
                        time.sleep(1)  # File might not be closed yet. Wait and try again.
                    else:
                        # Something went wrong and the file could not be deleted. Warn the user.
                        warnings.warn(
                            f"Failed to remove temporary file: '{temp_file.name}'. {ex}",
                            stacklevel=2,
                        )
