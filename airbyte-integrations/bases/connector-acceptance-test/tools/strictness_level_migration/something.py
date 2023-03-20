import asyncio
import os
from pathlib import Path

from definitions import ALL_DEFINITIONS
from create_prs import get_connector_name_from_definition, acceptance_test_config_path, CONNECTORS_DIRECTORY


async def run_tests(connector_definition):
    connector_name = get_connector_name_from_definition(connector_definition)
    path_to_acceptance_test_runner = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"
    path_to_acceptance_test_config = acceptance_test_config_path(connector_name)
    failure_output_file = f"results/failures/{connector_name}-results.txt"

    print(f"Start running tests for {connector_name}.")
    process = await asyncio.create_subprocess_exec("sh", path_to_acceptance_test_runner, env=dict(os.environ, CONFIG_PATH=path_to_acceptance_test_config), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    return_code = await process.wait()
    if return_code == 0:
        print(f"{connector_name} succeeded.")
    elif return_code == 1:
        with open(failure_output_file, "wb") as f:
            if return_code == 1:
                contents = await process.stdout.read()
                f.write(contents)
        print(f"{connector_name} failed with exit code {return_code}.")
    else:
        with open(failure_output_file, "w") as f:
            f.write(f"{connector_name} process completed with exit code {return_code}")
        print(f"{connector_name} failed with exit code {return_code}.")


async def main():
    tasks = []
    for definition in ALL_DEFINITIONS[:8]:
        tasks.append(run_tests(definition))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
