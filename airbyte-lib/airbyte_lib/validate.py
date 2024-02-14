# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Defines the `airbyte-lib-validate-source` CLI.

This tool checks if connectors are compatible with airbyte-lib.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from rich import print

import airbyte_lib as ab
from airbyte_lib import exceptions as exc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a connector")
    parser.add_argument(
        "--connector-dir",
        type=str,
        required=True,
        help="Path to the connector directory",
    )
    parser.add_argument(
        "--validate-install-only",
        action="store_true",
        help="Only validate that the connector can be installed and config can be validated.",
    )
    parser.add_argument(
        "--sample-config",
        type=str,
        required=False,
        help="Path to the sample config.json file. Required without --validate-install-only.",
    )
    return parser.parse_args()


def _run_subprocess_and_raise_on_failure(args: list[str]) -> None:
    result = subprocess.run(
        args,
        check=False,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise exc.AirbyteSubprocessFailedError(
            run_args=args,
            exit_code=result.returncode,
            log_text=result.stderr.decode("utf-8"),
        )


def full_tests(connector_name: str, sample_config: str) -> None:
    print("Creating source and validating spec and version...")
    source = ab.get_source(
        # TODO: FIXME: noqa: SIM115, PTH123
        connector_name,
        config=json.load(open(sample_config)),  # noqa: SIM115, PTH123,
        install_if_missing=False,
    )

    print("Running check...")
    source.check()

    print("Fetching streams...")
    streams = source.get_available_streams()

    # try to peek all streams - if one works, stop, if none works, throw exception
    for stream in streams:
        try:
            print(f"Trying to read from stream {stream}...")
            record = next(source.get_records(stream))
            assert record, "No record returned"
            break
        except exc.AirbyteError as e:
            print(f"Could not read from stream {stream}: {e}")
        except Exception as e:
            print(f"Unhandled error occurred when trying to read from {stream}: {e}")
    else:
        raise exc.AirbyteNoDataFromConnectorError(
            context={"selected_streams": streams},
        )


def install_only_test(connector_name: str) -> None:
    print("Creating source and validating spec is returned successfully...")
    source = ab.get_source(connector_name)
    source._get_spec(force_refresh=True)  # noqa: SLF001


def run() -> None:
    """Handle CLI entrypoint for the `airbyte-lib-validate-source` command.

    It's called like this:
    > airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json

    It performs a basic smoke test to make sure the connector in question is airbyte-lib compliant:
    * Can be installed into a venv
    * Can be called via cli entrypoint
    * Answers according to the Airbyte protocol when called with spec, check, discover and read.
    """
    # parse args
    args = _parse_args()
    connector_dir = args.connector_dir
    sample_config = args.sample_config
    validate_install_only = args.validate_install_only
    validate(connector_dir, sample_config, validate_install_only=validate_install_only)


def validate(connector_dir: str, sample_config: str, *, validate_install_only: bool) -> None:
    # read metadata.yaml
    metadata_path = Path(connector_dir) / "metadata.yaml"
    with Path(metadata_path).open() as stream:
        metadata = yaml.safe_load(stream)["data"]

    # TODO: Use remoteRegistries.pypi.packageName once set for connectors
    connector_name = metadata["dockerRepository"].replace("airbyte/", "")

    # create a venv and install the connector
    venv_name = f".venv-{connector_name}"
    venv_path = Path(venv_name)
    if not venv_path.exists():
        _run_subprocess_and_raise_on_failure([sys.executable, "-m", "venv", venv_name])

    pip_path = str(venv_path / "bin" / "pip")

    _run_subprocess_and_raise_on_failure([pip_path, "install", connector_dir])

    # write basic registry to temp json file
    registry = {
        "sources": [
            {
                "dockerRepository": f"airbyte/{connector_name}",
                "dockerImageTag": "0.0.1",
                "remoteRegistries": {
                    "pypi": {"packageName": "airbyte-{connector_name}", "enabled": True}
                },
            },
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w+t", delete=True) as temp_file:
        temp_file.write(json.dumps(registry))
        temp_file.seek(0)
        os.environ["AIRBYTE_LOCAL_REGISTRY"] = str(temp_file.name)
        if validate_install_only:
            install_only_test(connector_name)
        else:
            if not sample_config:
                raise exc.AirbyteLibInputError(
                    input_value="--sample-config is required without --validate-install-only set"
                )
            full_tests(connector_name, sample_config)
