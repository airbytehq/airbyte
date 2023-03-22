#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import asyncio
import os
from pathlib import Path

from create_prs import CONNECTORS_DIRECTORY, acceptance_test_config_path, get_airbyte_connector_name_from_definition, is_airbyte_connector
from definitions import ALL_DEFINITIONS

parser = argparse.ArgumentParser(
    description="Run tests for a list of connectors."
)
parser.add_argument("--connectors", nargs='*')
parser.add_argument("--file")
parser.add_argument("--max_concurrency", default=10)


async def run_tests(connector_name):
    path_to_acceptance_test_runner = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"
    path_to_acceptance_test_config = acceptance_test_config_path(connector_name)
    failure_output_file = f"results/failures/{connector_name}.txt"
    success_output_file = f"results/successes/{connector_name}.txt"

    print(f"Start running tests for {connector_name}.")
    process = await asyncio.create_subprocess_exec(
        "sh",
        path_to_acceptance_test_runner,
        env=dict(os.environ, CONFIG_PATH=path_to_acceptance_test_config),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return_code = await process.wait()
    if return_code == 0:
        with open(success_output_file, "wb") as f:
            contents = await process.stdout.read()
            f.write(contents)
        print(f"{connector_name} succeeded.")
    elif return_code == 1:
        with open(failure_output_file, "wb") as f:
            if return_code == 1:
                contents = await process.stdout.read()
                f.write(contents)
        print(f"{connector_name} failed with exit code {return_code}.")
    else:
        with open(failure_output_file, "w") as f:
            f.write(f"{connector_name} failed with exit code {return_code}.")
        print(f"{connector_name} failed with exit code {return_code}.")


async def semaphore_gather(coroutines, num_semaphores):
    # Limit the amount of connectors we want to test at once
    # To avoid crashing our docker by spinning up too many containers
    # Or using too much CPU. How many you can run will depend on the
    # specs you've allocated to Docker
    semaphore = asyncio.Semaphore(num_semaphores)

    async def _wrap_coro(coroutine):
        async with semaphore:
            return await coroutine

    return await asyncio.gather(*(_wrap_coro(coroutine) for coroutine in coroutines), return_exceptions=False)


async def main(num_semaphores):
    tasks = []

    for definition in ALL_DEFINITIONS:
        if is_airbyte_connector(definition):
            connector_name = get_airbyte_connector_name_from_definition(definition)
            tasks.append(run_tests(connector_name))
    await asyncio.gather(semaphore_gather(tasks, num_semaphores=num_semaphores))


if __name__ == "__main__":
    args = parser.parse_args()
    num_semaphores = args.max_concurrency

    asyncio.run(main(num_semaphores=num_semaphores))
