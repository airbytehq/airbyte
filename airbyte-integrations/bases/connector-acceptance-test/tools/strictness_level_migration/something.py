import subprocess
import os
from pathlib import Path

from definitions import ALL_DEFINITIONS
from create_prs import get_connector_name_from_definition, acceptance_test_config_path, CONNECTORS_DIRECTORY


if __name__ == "__main__":
    successes = {}
    failures = {}
    for definition in ALL_DEFINITIONS[:8]:
        connector_name = get_connector_name_from_definition(definition)
        path_to_acceptance_test_runner = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"
        path_to_acceptance_test_config = acceptance_test_config_path(connector_name)

        print(f"Start running tests for {connector_name}.")
        result = subprocess.run(["sh", path_to_acceptance_test_runner], env=dict(os.environ, CONFIG_PATH=path_to_acceptance_test_config), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            successes[connector_name] = result
            print(f"{connector_name} succeeded.")
        else:
            failures[connector_name] = result
            print(f"{connector_name} failed.")

    for connector_name, results in failures.items():
        with open(f"results/failures/{connector_name}-results.txt", "w") as f:
            f.write("Results:")
            print("\n")
            for line in results.stdout.splitlines():
                f.write(line)
                f.write("\n")

    with open("results/successes.txt", "w") as f:
        for connector_name in successes.keys():
            f.write(connector_name)
            f.write("'n")
