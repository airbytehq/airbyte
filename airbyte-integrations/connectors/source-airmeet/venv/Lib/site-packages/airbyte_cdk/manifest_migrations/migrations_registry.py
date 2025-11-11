#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import importlib
import inspect
import os
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Type

import yaml

from airbyte_cdk.manifest_migrations.manifest_migration import (
    ManifestMigration,
)

DiscoveredMigrations = Dict[str, List[Type[ManifestMigration]]]

MIGRATIONS_PATH = Path(__file__).parent / "migrations"
REGISTRY_PATH = MIGRATIONS_PATH / "registry.yaml"


def _find_migration_module(name: str) -> str:
    """
    Finds the migration module by name in the migrations directory.
    The name should match the file name of the migration module (without the .py extension).
    Raises ImportError if the module is not found.
    """

    for migration_file in os.listdir(MIGRATIONS_PATH):
        migration_name = name + ".py"
        if migration_file == migration_name:
            return migration_file.replace(".py", "")

    raise ImportError(f"Migration module '{name}' not found in {MIGRATIONS_PATH}.")


def _get_migration_class(module: ModuleType) -> Type[ManifestMigration]:
    """
    Returns the ManifestMigration subclass defined in the module.
    """
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, ManifestMigration):
            return obj

    raise ImportError(f"No ManifestMigration subclass found in module {module.__name__}.")


def _discover_migrations() -> DiscoveredMigrations:
    """
    Discovers and returns a list of ManifestMigration subclasses in the order specified by registry.yaml.
    """
    with open(REGISTRY_PATH, "r") as f:
        registry = yaml.safe_load(f)
        migrations: DiscoveredMigrations = {}
        # Iterate through the registry and import the migration classes
        # based on the version and order specified in the registry.yaml
        for version_entry in registry.get("manifest_migrations", []):
            migration_version = version_entry.get("version", "0.0.0")
            if not migration_version in migrations:
                migrations[migration_version] = []

            for migration in sorted(version_entry.get("migrations", []), key=lambda m: m["order"]):
                module = importlib.import_module(
                    f"airbyte_cdk.manifest_migrations.migrations.{_find_migration_module(migration['name'])}"
                )
                migration_class = _get_migration_class(module)
                migrations[migration_version].append(migration_class)

    return migrations


# registered migrations
MANIFEST_MIGRATIONS: DiscoveredMigrations = _discover_migrations()
