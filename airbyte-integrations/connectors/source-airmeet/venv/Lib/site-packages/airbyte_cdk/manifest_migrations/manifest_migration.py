#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict

ManifestType = Dict[str, Any]


TYPE_TAG = "type"

NON_MIGRATABLE_TYPES = [
    # more info here: https://github.com/airbytehq/airbyte-internal-issues/issues/12423
    "DynamicDeclarativeStream",
]


@dataclass
class MigrationTrace:
    """
    This class represents a migration that has been applied to the manifest.
    It contains information about the migration, including the version it was applied from,
    the version it was applied to, and the time it was applied.
    """

    from_version: str
    to_version: str
    migration: str
    migrated_at: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ManifestMigration(ABC):
    """
    Base class for manifest migrations.
    This class provides a framework for migrating manifest components.
    It defines the structure for migration classes, including methods for checking if a migration is needed,
    performing the migration, and validating the migration.
    """

    def __init__(self) -> None:
        self.is_migrated: bool = False

    @abstractmethod
    def should_migrate(self, manifest: ManifestType) -> bool:
        """
        Check if the manifest should be migrated.

        :param manifest: The manifest to potentially migrate

        :return: true if the manifest is of the expected format and should be migrated. False otherwise.
        """

    @abstractmethod
    def migrate(self, manifest: ManifestType) -> None:
        """
        Migrate the manifest. Assumes should_migrate(manifest) returned True.

        :param manifest: The manifest to migrate
        """

    @abstractmethod
    def validate(self, manifest: ManifestType) -> bool:
        """
        Validate the manifest to ensure the migration was successfully applied.

        :param manifest: The manifest to validate
        """

    def _is_component(self, obj: Dict[str, Any]) -> bool:
        """
        Check if the object is a component.

        :param obj: The object to check
        :return: True if the object is a component, False otherwise
        """
        return TYPE_TAG in obj.keys()

    def _is_migratable_type(self, obj: Dict[str, Any]) -> bool:
        """
        Check if the object is a migratable component,
        based on the Type of the component and the migration version.

        :param obj: The object to check
        :return: True if the object is a migratable component, False otherwise
        """
        return obj[TYPE_TAG] not in NON_MIGRATABLE_TYPES

    def _process_manifest(self, obj: Any) -> None:
        """
        Recursively processes a manifest object, migrating components that match the migration criteria.

        This method traverses the entire manifest structure (dictionaries and lists) and applies
        migrations to components that:
        1. Have a type tag
        2. Are not in the list of non-migratable types
        3. Meet the conditions defined in the should_migrate method

        Parameters:
            obj (Any): The object to process, which can be a dictionary, list, or any other type.
                       Dictionary objects are checked for component type tags and potentially migrated.
                       List objects have each of their items processed recursively.
                       Other types are ignored.

        Returns:
            None, since we process the manifest in place.
        """
        if isinstance(obj, dict):
            # Check if the object is a component
            if self._is_component(obj):
                # Check if the object is allowed to be migrated
                if not self._is_migratable_type(obj):
                    return

                # Check if the object should be migrated
                if self.should_migrate(obj):
                    # Perform the migration, if needed
                    self.migrate(obj)
                    # validate the migration
                    self.is_migrated = self.validate(obj)

            # Process all values in the dictionary
            for value in list(obj.values()):
                self._process_manifest(value)

        elif isinstance(obj, list):
            # Process all items in the list
            for item in obj:
                self._process_manifest(item)
