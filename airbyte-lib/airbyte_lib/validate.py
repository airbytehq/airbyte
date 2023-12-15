import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
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

def run():
    """
    This is a CLI entrypoint for the `airbyte-lib-validate-source` command.
    It's called like this: airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json
    """

    # parse args
    args = _parse_args()
    connector_dir = args.connector_dir
    connector_version = args.connector_version
    sample_config = args.sample_config

    # read metadata.yaml
    metadata_path = Path(connector_dir) / "metadata.yaml"
    metadata = yaml.safe_load(metadata_path)["data"]
    connector_name = metadata["name"]

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
                "sourceDefinitionId": "9f32dab3-77cb-45a1-9d33-347aa5fbe363",
                "name": "Test Source",
                "dockerRepository": f"airbyte/source-{connector_name}",
                "dockerImageTag": "0.0.0",
                "documentationUrl": "https://docs.airbyte.com/integrations/sources/test",
                "icon": "test.svg",
                "iconUrl": "https://connectors.airbyte.com/files/metadata/airbyte/source-test/latest/icon.svg",
                "sourceType": "api",
                "spec": {},
                "tombstone": False,
                "public": True,
                "custom": False,
                "releaseStage": "alpha",
                "supportLevel": "community",
                "ab_internal": {"sl": 100, "ql": 200},
                "tags": ["language:python"],
                "githubIssueLabel": "source-test",
                "license": "MIT",
            }
        ]
    }

    registry_path = Path("registry.json")
    registry_path.write_text(json.dumps(registry))

    os.environ["AIRBYTE_LOCAL_REGISTRY"] = str(registry_path)

    source = ab.get_connector(connector_name, config=json.load(open(sample_config)))

    source.check()

    first_stream = source.get_available_streams()[0]

    source.set_streams([first_stream])

    source.peek(first_stream, 1)
