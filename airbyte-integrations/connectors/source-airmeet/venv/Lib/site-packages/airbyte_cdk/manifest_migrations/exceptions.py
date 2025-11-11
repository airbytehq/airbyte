#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


class ManifestMigrationException(Exception):
    """
    Raised when a migration error occurs in the manifest.
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"Failed to migrate the manifest: {message}")
