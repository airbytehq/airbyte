#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import copy
import logging
import re
from datetime import datetime, timezone
from typing import Tuple, Type

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from airbyte_cdk.manifest_migrations.exceptions import (
    ManifestMigrationException,
)
from airbyte_cdk.manifest_migrations.manifest_migration import (
    ManifestMigration,
    ManifestType,
    MigrationTrace,
)
from airbyte_cdk.manifest_migrations.migrations_registry import (
    MANIFEST_MIGRATIONS,
)

METADATA_TAG = "metadata"
MANIFEST_VERSION_TAG = "version"
APPLIED_MIGRATIONS_TAG = "applied_migrations"
WILDCARD_VERSION_PATTERN = ".*"
LOGGER = logging.getLogger("airbyte.cdk.manifest_migrations")


class ManifestMigrationHandler:
    """
    This class is responsible for handling migrations in the manifest.
    """

    def __init__(self, manifest: ManifestType) -> None:
        self._manifest = manifest
        self._migrated_manifest: ManifestType = copy.deepcopy(self._manifest)

    def apply_migrations(self) -> ManifestType:
        """
        Apply all registered migrations to the manifest.

        This method iterates through all migrations in the migrations registry and applies
        them sequentially to the current manifest. If any migration fails with a
        ManifestMigrationException, the original unmodified manifest is returned instead.

        Returns:
            ManifestType: The migrated manifest if all migrations succeeded, or the original
                          manifest if any migration failed.
        """
        try:
            manifest_version = self._get_manifest_version()
            for migration_version, migrations in MANIFEST_MIGRATIONS.items():
                for migration_cls in migrations:
                    self._handle_migration(migration_cls, manifest_version, migration_version)
            return self._migrated_manifest
        except ManifestMigrationException:
            # if any errors occur we return the original resolved manifest
            return self._manifest

    def _handle_migration(
        self,
        migration_class: Type[ManifestMigration],
        manifest_version: str,
        migration_version: str,
    ) -> None:
        """
        Handles a single manifest migration by instantiating the migration class and processing the manifest.

        Args:
            migration_class (Type[ManifestMigration]): The migration class to apply to the manifest.

        Raises:
            ManifestMigrationException: If the migration process encounters any errors.
        """
        try:
            migration_instance = migration_class()
            can_apply_migration, should_bump_version = self._version_is_valid_for_migration(
                manifest_version, migration_version
            )
            if can_apply_migration:
                migration_instance._process_manifest(self._migrated_manifest)
                if migration_instance.is_migrated:
                    if should_bump_version:
                        self._set_manifest_version(migration_version)
                    self._set_migration_trace(migration_class, manifest_version, migration_version)
            else:
                LOGGER.info(
                    f"Manifest migration: `{self._get_migration_name(migration_class)}` is not supported for the given manifest version `{manifest_version}`.",
                )
        except Exception as e:
            raise ManifestMigrationException(str(e)) from e

    def _get_migration_name(self, migration_class: Type[ManifestMigration]) -> str:
        """
        Get the name of the migration instance.

        Returns:
            str: The name of the migration.
        """
        return migration_class.__name__

    def _get_manifest_version(self) -> str:
        """
        Get the manifest version from the manifest.

        :param manifest: The manifest to get the version from
        :return: The manifest version
        """
        return str(self._migrated_manifest.get(MANIFEST_VERSION_TAG, "0.0.0"))

    def _version_is_valid_for_migration(
        self,
        manifest_version: str,
        migration_version: str,
    ) -> Tuple[bool, bool]:
        """
        Decide whether *manifest_version* satisfies the *migration_version* rule.

        Rules
        -----
        1. ``"*"``
           – Wildcard: anything matches.
        2. String starts with a PEP 440 operator (``==``, ``!=``, ``<=``, ``>=``,
           ``<``, ``>``, ``~=``, etc.)
           – Treat *migration_version* as a SpecifierSet and test the manifest
             version against it.
        3. Plain version
           – Interpret both strings as concrete versions and return
             ``manifest_version <= migration_version``.
        """
        if re.match(WILDCARD_VERSION_PATTERN, migration_version):
            return True, False

        if migration_version.startswith(("=", "!", ">", "<", "~")):
            spec = SpecifierSet(migration_version)
            return spec.contains(Version(manifest_version)), False

        return Version(manifest_version) <= Version(migration_version), True

    def _set_manifest_version(self, version: str) -> None:
        """
        Set the manifest version in the manifest.

        :param version: The version to set
        """
        self._migrated_manifest[MANIFEST_VERSION_TAG] = version

    def _set_migration_trace(
        self,
        migration_instance: Type[ManifestMigration],
        manifest_version: str,
        migration_version: str,
    ) -> None:
        """
        Set the migration trace in the manifest, under the `metadata.applied_migrations` property object.

        :param migration_instance: The migration instance to set
        :param manifest_version: The manifest version before migration
        :param migration_version: The manifest version after migration
        """

        if METADATA_TAG not in self._migrated_manifest:
            self._migrated_manifest[METADATA_TAG] = {}
        if APPLIED_MIGRATIONS_TAG not in self._migrated_manifest[METADATA_TAG]:
            self._migrated_manifest[METADATA_TAG][APPLIED_MIGRATIONS_TAG] = []

        migration_trace = MigrationTrace(
            from_version=manifest_version,
            to_version=migration_version,
            migration=self._get_migration_name(migration_instance),
            migrated_at=datetime.now(tz=timezone.utc).isoformat(),
        ).as_dict()

        if migration_version not in self._migrated_manifest[METADATA_TAG][APPLIED_MIGRATIONS_TAG]:
            self._migrated_manifest[METADATA_TAG][APPLIED_MIGRATIONS_TAG].append(migration_trace)
