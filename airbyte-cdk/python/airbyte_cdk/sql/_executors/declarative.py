# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Support for declarative yaml source testing."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import IO, TYPE_CHECKING, cast

import pydantic
import yaml
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._executors.base import Executor

if TYPE_CHECKING:
    from collections.abc import Iterator

    from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator


def _suppress_cdk_pydantic_deprecation_warnings() -> None:
    """Suppress deprecation warnings from Pydantic in the CDK.

    CDK has deprecated uses of `json()` and `parse_obj()`, and we don't want users
    to see these warnings.
    """
    warnings.filterwarnings(
        "ignore",
        category=pydantic.warnings.PydanticDeprecatedSince20,
    )


class DeclarativeExecutor(Executor):
    """An executor for declarative sources."""

    def __init__(
        self,
        name: str,
        manifest: dict[str, str] | Path,
    ) -> None:
        """Initialize a declarative executor.

        - If `manifest` is a path, it will be read as a json file.
        - If `manifest` is a string, it will be parsed as an HTTP path.
        - If `manifest` is a dict, it will be used as is.
        """
        _suppress_cdk_pydantic_deprecation_warnings()

        self.name = name
        self._manifest_dict: dict[str, str]
        if isinstance(manifest, Path):
            self._manifest_dict = cast(dict[str, str], yaml.safe_load(manifest.read_text()))

        elif isinstance(manifest, dict):
            self._manifest_dict = manifest

        self._validate_manifest(self._manifest_dict)
        self.declarative_source = ManifestDeclarativeSource(source_config=self._manifest_dict)

        self.reported_version: str | None = self._manifest_dict.get("version", None)

    def get_installed_version(
        self,
        *,
        raise_on_error: bool = False,
        recheck: bool = False,
    ) -> str | None:
        """Detect the version of the connector installed."""
        _ = raise_on_error, recheck  # Not used
        return self.reported_version

    def _validate_manifest(self, manifest_dict: dict[str, str]) -> None:
        """Validate the manifest."""
        manifest_text = yaml.safe_dump(manifest_dict)
        if "class_name:" in manifest_text:
            raise exc.AirbyteConnectorInstallationError(
                message=(
                    "The provided manifest requires additional code files (`class_name` key "
                    "detected). This feature is not compatible with the declarative YAML "
                    "executor. To use this executor, please try again with the Python "
                    "executor."
                ),
                connector_name=self.name,
            )

    @property
    def _cli(self) -> list[str]:
        """Not applicable."""
        return []  # N/A

    def execute(
        self,
        args: list[str],
        *,
        stdin: IO[str] | AirbyteMessageIterator | None = None,
    ) -> Iterator[str]:
        """Execute the declarative source."""
        _ = stdin  # Not used
        source_entrypoint = AirbyteEntrypoint(self.declarative_source)
        parsed_args = source_entrypoint.parse_args(args)
        yield from source_entrypoint.run(parsed_args)

    def ensure_installation(self, *, auto_fix: bool = True) -> None:
        """No-op. The declarative source is included with Airbyte."""
        _ = auto_fix
        pass

    def install(self) -> None:
        """No-op. The declarative source is included with Airbyte."""
        pass

    def uninstall(self) -> None:
        """No-op. The declarative source is included with Airbyte."""
        pass
