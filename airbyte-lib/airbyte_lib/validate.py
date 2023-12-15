import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import List
import yaml
import airbyte_lib as ab


def _parse_args():
    parser = argparse.ArgumentParser(description="Validate a connector")
    parser.add_argument(
        "--connector-dir",
        type=str,
        required=True,
        help="Path to the connector directory",
    )
    parser.add_argument(
        "--sample-config",
        type=str,
        required=True,
        help="Path to the sample config.json file",
    )
    return parser.parse_args()


def _run_subprocess_and_raise_on_failure(args: List[str]):
    result = subprocess.run(args)
    if result.returncode != 0:
        raise Exception(f"{args} exited with code {result.returncode}")

def tests(connector_name, sample_config):
    print("Creating source and validating spec and version...")
    source = ab.get_connector(connector_name, config=json.load(open(sample_config)))

    print("Running check...")
    source.check()

    print("Fetching streams...")
    first_stream = source.get_available_streams()[0]

    source.set_streams([first_stream])

    print("Performing read...")
    source.peek(first_stream, 1)

def run():
    """
    This is a CLI entrypoint for the `airbyte-lib-validate-source` command.
    It's called like this: airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json

    It performs a basic smoke test to make sure the connector in question is airbyte-lib compliant:
    * Can be installed into a venv
    * Can be called via cli entrypoint
    * Answers according to the Airbyte protocol when called with spec, check, discover and read
    """

    # parse args
    args = _parse_args()
    connector_dir = args.connector_dir
    sample_config = args.sample_config

    # read metadata.yaml
    metadata_path = Path(connector_dir) / "metadata.yaml"
    with open(metadata_path, "r") as stream:
        metadata = yaml.safe_load(stream)["data"]

    connector_name = metadata["dockerRepository"].replace("airbyte/", "")

    # create a venv and install the connector
    venv_name = f".venv-{connector_name}"
    venv_path = Path(venv_name)
    if not venv_path.exists():
        _run_subprocess_and_raise_on_failure([sys.executable, "-m", "venv", venv_name])

    pip_path = os.path.join(venv_name, "bin", "pip")

    _run_subprocess_and_raise_on_failure([pip_path, "install", "-e", connector_dir])

    # write basic registry to temp json file
    registry = {
        "sources": [
            {
                "dockerRepository": f"airbyte/{connector_name}",
                "dockerImageTag": "0.0.0",
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w+t", delete=True) as temp_file:   
        temp_file.write(json.dumps(registry))
        temp_file.seek(0)
        os.environ["AIRBYTE_LOCAL_REGISTRY"] = str(temp_file.name)
        tests(connector_name, sample_config)
