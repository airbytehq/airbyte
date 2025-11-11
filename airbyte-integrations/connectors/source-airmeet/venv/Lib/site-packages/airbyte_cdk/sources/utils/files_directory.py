#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import os

AIRBYTE_STAGING_DIRECTORY = os.getenv("AIRBYTE_STAGING_DIRECTORY", "/staging/files")
DEFAULT_LOCAL_DIRECTORY = "/tmp/airbyte-file-transfer"


def get_files_directory() -> str:
    return (
        AIRBYTE_STAGING_DIRECTORY
        if os.path.exists(AIRBYTE_STAGING_DIRECTORY)
        else DEFAULT_LOCAL_DIRECTORY
    )
