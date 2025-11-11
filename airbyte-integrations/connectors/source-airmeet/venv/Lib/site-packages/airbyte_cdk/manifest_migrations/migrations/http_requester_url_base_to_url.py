#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.manifest_migrations.manifest_migration import (
    TYPE_TAG,
    ManifestMigration,
    ManifestType,
)


class HttpRequesterUrlBaseToUrl(ManifestMigration):
    """
    This migration is responsible for migrating the `url_base` key to `url` in the HttpRequester component.
    The `url_base` key is expected to be a base URL, and the `url` key is expected to be a full URL.
    The migration will copy the value of `url_base` to `url`.
    """

    component_type = "HttpRequester"
    original_key = "url_base"
    replacement_key = "url"

    def should_migrate(self, manifest: ManifestType) -> bool:
        return manifest[TYPE_TAG] == self.component_type and self.original_key in list(
            manifest.keys()
        )

    def migrate(self, manifest: ManifestType) -> None:
        manifest[self.replacement_key] = manifest[self.original_key]
        manifest.pop(self.original_key, None)

    def validate(self, manifest: ManifestType) -> bool:
        """
        Validate the migration by checking if the `url` key is present and the `url_base` key is not.
        """
        return (
            self.replacement_key in manifest
            and self.original_key not in manifest
            and manifest[self.replacement_key] is not None
        )
