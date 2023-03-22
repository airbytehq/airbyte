#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import asyncio
import os
from pathlib import Path

import utils
from definitions import GA_DEFINITIONS, is_airbyte_connector, find_by_name, get_airbyte_connector_name_from_definition
from definitions import ALL_DEFINITIONS

MODULE_NAME = "fail_on_extra_columns"

parser = argparse.ArgumentParser(
    description="Run tests for a list of connectors."
)
parser.add_argument("--connectors", nargs='*')
parser.add_argument("--file")
parser.add_argument("--max_concurrency", type=int, default=10)


async def run_tests(connector_name):
    path_to_acceptance_test_runner = Path(utils.CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-docker.sh"
    path_to_acceptance_test_config = utils.acceptance_test_config_path(connector_name)
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

    dir_path = Path(f"results/{return_code}")
    dir_path.mkdir(parents=True, exist_ok=True)

    if return_code in [0, 1]:
        with open(f"{dir_path}/{connector_name}.txt", "wb") as f:
            contents = await process.stdout.read()
            f.write(contents)
        if return_code == 0:
            print(f"{connector_name} succeeded.")
        else:
            print(f"{connector_name} tests failed.")
    else:
        with open(f"{dir_path}/{connector_name}.txt", "w") as f:
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


async def main(definitions, num_semaphores):
    tasks = []

    for definition in definitions:
        if is_airbyte_connector(definition):
            connector_name = get_airbyte_connector_name_from_definition(definition)
            tasks.append(run_tests(connector_name))
    await asyncio.gather(semaphore_gather(tasks, num_semaphores=num_semaphores))


if __name__ == "__main__":
    args = parser.parse_args()

    definitions = []
    if args.connectors:
        definitions = find_by_name(args.connectors)
    elif args.file:
        with open(f"templates/{MODULE_NAME}/{args.file}", "r") as f:
            connector_names = [line.strip() for line in f]
        definitions = find_by_name(connector_names)
    else:
        definitions = ALL_DEFINITIONS

    num_semaphores = args.max_concurrency

    asyncio.run(main(definitions=definitions, num_semaphores=num_semaphores))
