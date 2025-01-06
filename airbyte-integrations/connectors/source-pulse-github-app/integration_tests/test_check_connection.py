import pytest
import json
import os
from airbyte_cdk import AirbyteLogger
from source_pulse_github_app import SourcePulseGithubApp

@pytest.mark.integration
def test_check_connection():
    # Construct the path to the secret/config.json file
    # (Assuming this test file is inside the connector's source/test folders.)
    # If your project layout is different, adjust accordingly.
    connector_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    secret_config_path = os.path.join(connector_root, "secrets", "config.json")

    # Read config data from the JSON file
    with open(secret_config_path, "r") as f:
        config = json.load(f)

    logger = AirbyteLogger()
    source = SourcePulseGithubApp()

    # Test the connection using the loaded config
    success, error = source.check_connection(logger, config)

    assert success
    assert error is None
