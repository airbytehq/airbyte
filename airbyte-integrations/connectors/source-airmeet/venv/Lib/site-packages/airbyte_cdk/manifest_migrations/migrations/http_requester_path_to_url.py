#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from urllib.parse import urljoin

from airbyte_cdk.manifest_migrations.manifest_migration import (
    TYPE_TAG,
    ManifestMigration,
    ManifestType,
)
from airbyte_cdk.sources.types import EmptyString


class HttpRequesterPathToUrl(ManifestMigration):
    """
    This migration is responsible for migrating the `path` key to `url` in the HttpRequester component.
    The `path` key is expected to be a relative path, and the `url` key is expected to be a full URL.
    The migration will concatenate the `url_base` and `path` to form a full URL.
    """

    component_type = "HttpRequester"
    original_key = "path"
    replacement_key = "url"

    def should_migrate(self, manifest: ManifestType) -> bool:
        return manifest[TYPE_TAG] == self.component_type and self.original_key in list(
            manifest.keys()
        )

    def migrate(self, manifest: ManifestType) -> None:
        original_key_value = manifest.get(self.original_key, EmptyString).lstrip("/")
        replacement_key_value = manifest[self.replacement_key]

        # return a full-url if provided directly from interpolation context
        if original_key_value == EmptyString or original_key_value is None:
            manifest[self.replacement_key] = replacement_key_value
            manifest.pop(self.original_key, None)
        else:
            # since we didn't provide a full-url, the url_base might not have a trailing slash
            # so we join the url_base and path correctly
            if not replacement_key_value.endswith("/"):
                replacement_key_value += "/"

            manifest[self.replacement_key] = urljoin(replacement_key_value, original_key_value)
            manifest.pop(self.original_key, None)

    def validate(self, manifest: ManifestType) -> bool:
        """
        Validate the migration by checking if the `url` key is present and the `path` key is not.
        """
        return (
            self.replacement_key in manifest
            and self.original_key not in manifest
            and manifest[self.replacement_key] is not None
        )
