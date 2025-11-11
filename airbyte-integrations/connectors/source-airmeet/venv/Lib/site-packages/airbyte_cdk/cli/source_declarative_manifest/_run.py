# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Defines the `source-declarative-manifest` connector, which installs alongside CDK.

This file was originally imported from the dedicated connector directory, under the
`airbyte` monorepo.

Usage:

```
pipx install airbyte-cdk
source-declarative-manifest --help
source-declarative-manifest spec
...
```
"""

from __future__ import annotations

import argparse
import json
import pkgutil
import sys
import traceback
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, cast

import orjson
import yaml

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecificationSerializer,
    TraceType,
    Type,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


class SourceLocalYaml(YamlDeclarativeSource):
    """
    Declarative source defined by a yaml file in the local filesystem
    """

    def __init__(
        self,
        catalog: ConfiguredAirbyteCatalog | None,
        config: MutableMapping[str, Any] | None,
        state: TState,
        config_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        HACK!
            Problem: YamlDeclarativeSource relies on the calling module name/path to find the yaml file.
            Implication: If you call YamlDeclarativeSource directly it will look for the yaml file in the wrong place. (e.g. the airbyte-cdk package)
            Solution: Subclass YamlDeclarativeSource from the same location as the manifest to load.

            When can we remove this?
                When the airbyte-cdk is updated to not rely on the calling module name/path to find the yaml file.
                When all manifest connectors are updated to use the new airbyte-cdk.
                When all manifest connectors are updated to use the source-declarative-manifest as the base image.
        """
        super().__init__(
            catalog=catalog,
            config=config,
            state=state,  # type: ignore [arg-type]
            path_to_yaml="manifest.yaml",
            config_path=config_path,
        )


def _is_local_manifest_command(args: list[str]) -> bool:
    # Check for a local manifest.yaml file
    return Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml").exists()


def handle_command(args: list[str]) -> None:
    if _is_local_manifest_command(args):
        handle_local_manifest_command(args)
    else:
        handle_remote_manifest_command(args)


def _get_local_yaml_source(args: list[str]) -> SourceLocalYaml:
    try:
        parsed_args = AirbyteEntrypoint.parse_args(args)
        config, catalog, state = _parse_inputs_into_config_catalog_state(parsed_args)
        return SourceLocalYaml(
            config=config,
            catalog=catalog,
            state=state,
            config_path=parsed_args.config if hasattr(parsed_args, "config") else None,
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=ab_datetime_now().to_epoch_millis(),
                            error=AirbyteErrorTraceMessage(
                                message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        raise error


def handle_local_manifest_command(args: list[str]) -> None:
    source = _get_local_yaml_source(args)
    launch(
        source=source,
        args=args,
    )


def handle_remote_manifest_command(args: list[str]) -> None:
    """Overrides the spec command to return the generalized spec for the declarative manifest source.

    This is different from a typical low-code, but built and published separately source built as a ManifestDeclarativeSource,
    because that will have a spec method that returns the spec for that specific source. Other than spec,
    the generalized connector behaves the same as any other, since the manifest is provided in the config.
    """
    if args[0] == "spec":
        json_spec = pkgutil.get_data(
            "airbyte_cdk.cli.source_declarative_manifest",
            "spec.json",
        )
        if json_spec is None:
            raise FileNotFoundError(
                "Could not find `spec.json` file for source-declarative-manifest"
            )

        spec_obj = json.loads(json_spec)
        spec = ConnectorSpecificationSerializer.load(spec_obj)

        message = AirbyteMessage(type=Type.SPEC, spec=spec)
        print(AirbyteEntrypoint.airbyte_message_to_string(message))
    else:
        source = create_declarative_source(args)
        launch(
            source=source,
            args=args,
        )


def create_declarative_source(
    args: list[str],
) -> ConcurrentDeclarativeSource:  # type: ignore [type-arg]
    """Creates the source with the injected config.

    This essentially does what other low-code sources do at build time, but at runtime,
    with a user-provided manifest in the config. This better reflects what happens in the
    connector builder.
    """
    try:
        config: MutableMapping[str, Any] | None
        catalog: ConfiguredAirbyteCatalog | None
        state: list[AirbyteStateMessage]

        parsed_args = AirbyteEntrypoint.parse_args(args)
        config, catalog, state = _parse_inputs_into_config_catalog_state(parsed_args)

        if config is None:
            raise ValueError(
                "Invalid config: `__injected_declarative_manifest` should be provided at the root "
                "of the config or using the --manifest-path argument."
            )

        # If a manifest_path is provided in the args, inject it into the config
        if hasattr(parsed_args, "manifest_path") and parsed_args.manifest_path:
            injected_manifest = _parse_manifest_from_file(parsed_args.manifest_path)
            if injected_manifest:
                config["__injected_declarative_manifest"] = injected_manifest

        if "__injected_declarative_manifest" not in config:
            raise ValueError(
                "Invalid config: `__injected_declarative_manifest` should be provided at the root "
                "of the config or using the --manifest-path argument. "
                f"Config only has keys: {list(config.keys() if config else [])}"
            )
        if not isinstance(config["__injected_declarative_manifest"], dict):
            raise ValueError(
                "Invalid config: `__injected_declarative_manifest` should be a dictionary, "
                f"but got type: {type(config['__injected_declarative_manifest'])}"
            )

        if hasattr(parsed_args, "components_path") and parsed_args.components_path:
            _register_components_from_file(parsed_args.components_path)

        return ConcurrentDeclarativeSource(
            config=config,
            catalog=catalog,
            state=state,
            source_config=cast(dict[str, Any], config["__injected_declarative_manifest"]),
            config_path=parsed_args.config if hasattr(parsed_args, "config") else None,
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=ab_datetime_now().to_epoch_millis(),
                            error=AirbyteErrorTraceMessage(
                                message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        raise error


def _parse_inputs_into_config_catalog_state(
    parsed_args: argparse.Namespace,
) -> tuple[
    MutableMapping[str, Any] | None,
    ConfiguredAirbyteCatalog | None,
    list[AirbyteStateMessage],
]:
    config = (
        ConcurrentDeclarativeSource.read_config(parsed_args.config)
        if hasattr(parsed_args, "config")
        else None
    )
    catalog = (
        ConcurrentDeclarativeSource.read_catalog(parsed_args.catalog)
        if hasattr(parsed_args, "catalog")
        else None
    )
    state = (
        ConcurrentDeclarativeSource.read_state(parsed_args.state)
        if hasattr(parsed_args, "state")
        else []
    )

    return config, catalog, state


def _parse_manifest_from_file(filepath: str) -> dict[str, Any] | None:
    """Extract and parse a manifest file specified in the args."""
    try:
        with open(filepath, "r", encoding="utf-8") as manifest_file:
            manifest_content = yaml.safe_load(manifest_file)
            if manifest_content is None:
                raise ValueError(f"Manifest file at {filepath} is empty")
            if not isinstance(manifest_content, dict):
                raise ValueError(f"Manifest must be a dictionary, got {type(manifest_content)}")
            return manifest_content
    except Exception as error:
        raise ValueError(f"Failed to load manifest file from {filepath}: {error}")


def _register_components_from_file(filepath: str) -> None:
    """Load and register components from a Python file specified in the args."""
    import importlib.util
    import sys

    components_path = Path(filepath)

    module_name = "components"
    sdm_module_name = "source_declarative_manifest.components"

    # Create module spec
    spec = importlib.util.spec_from_file_location(module_name, components_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {components_path}")

    # Create module and execute code, registering the module before executing its code
    # To avoid issues with dataclasses that look up the module
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    sys.modules[sdm_module_name] = module

    spec.loader.exec_module(module)


def run() -> None:
    """Run the `source-declarative-manifest` CLI.

    Args are detected from the command line, and the appropriate command is executed.
    """
    args: list[str] = sys.argv[1:]
    handle_command(args)
