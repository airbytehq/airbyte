from pathlib import Path
CONNECTORS_DIRECTORY = "../../../../connectors"


def acceptance_test_config_path(connector_name):
    """Returns the path to a given connector's acceptance-test-config.yml file."""
    return Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"
