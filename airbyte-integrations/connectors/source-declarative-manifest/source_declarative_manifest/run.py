#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import json
import pkgutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, List, Mapping, Optional

from orjson import orjson

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
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState


class SourceLocalYaml(YamlDeclarativeSource):
    """
    Declarative source defined by a yaml file in the local filesystem
    """

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
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
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})


def _is_local_manifest_command(args: List[str]) -> bool:
    # Check for a local manifest.yaml file
    return Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml").exists()


def handle_command(args: List[str]) -> None:
    if _is_local_manifest_command(args):
        handle_local_manifest_command(args)
    else:
        handle_remote_manifest_command(args)


def _get_local_yaml_source(args: List[str]) -> SourceLocalYaml:
    try:
        config, catalog, state = _parse_inputs_into_config_catalog_state(args)
        return SourceLocalYaml(config=config, catalog=catalog, state=state)
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=int(datetime.now().timestamp() * 1000),
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


def handle_local_manifest_command(args: List[str]) -> None:
    source = _get_local_yaml_source(args)
    launch(source, args)


def handle_remote_manifest_command(args: List[str]) -> None:
    """Overrides the spec command to return the generalized spec for the declarative manifest source.

    This is different from a typical low-code, but built and published separately source built as a ManifestDeclarativeSource,
    because that will have a spec method that returns the spec for that specific source. Other than spec,
    the generalized connector behaves the same as any other, since the manifest is provided in the config.
    """
    if args[0] == "spec":
        json_spec = pkgutil.get_data("source_declarative_manifest", "spec.json")
        spec_obj = json.loads(json_spec)
        spec = ConnectorSpecificationSerializer.load(spec_obj)

        message = AirbyteMessage(type=Type.SPEC, spec=spec)
        print(AirbyteEntrypoint.airbyte_message_to_string(message))
    else:
        source = create_declarative_source(args)
        launch(source, args)


def create_declarative_source(args: List[str]) -> ConcurrentDeclarativeSource:
    """Creates the source with the injected config.

    This essentially does what other low-code sources do at build time, but at runtime,
    with a user-provided manifest in the config. This better reflects what happens in the
    connector builder.
    """
    try:
        config, catalog, state = _parse_inputs_into_config_catalog_state(args)
        if "__injected_declarative_manifest" not in config:
            raise ValueError(
                f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
            )
        return ConcurrentDeclarativeSource(
            config=config, catalog=catalog, state=state, source_config=config.get("__injected_declarative_manifest")
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=int(datetime.now().timestamp() * 1000),
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
    args: List[str],
) -> (Optional[Mapping[str, Any]], Optional[ConfiguredAirbyteCatalog], List[AirbyteStateMessage]):
    parsed_args = AirbyteEntrypoint.parse_args(args)
    config = ConcurrentDeclarativeSource.read_config(parsed_args.config) if hasattr(parsed_args, "config") else None
    catalog = ConcurrentDeclarativeSource.read_catalog(parsed_args.catalog) if hasattr(parsed_args, "catalog") else None
    state = ConcurrentDeclarativeSource.read_state(parsed_args.state) if hasattr(parsed_args, "state") else []

    return config, catalog, state


def run():
    args = sys.argv[1:]
    handle_command(args)
