#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import asyncio
import logging
import os
from pathlib import Path

import definitions
import utils
from migrations.fail_on_extra_columns import config

parser = argparse.ArgumentParser(description="Run connector acceptance tests for a list of connectors.")
utils.add_connectors_param(parser)
utils.add_allow_alpha_param(parser)
utils.add_allow_beta_param(parser)
parser.add_argument("--max_concurrency", type=int, default=10, help="The maximum number of acceptance tests that should happen at once.")


async def run_tests(connector_name):
    path_to_acceptance_test_runner = utils.acceptance_test_docker_sh_path(connector_name)
    path_to_acceptance_test_config = utils.acceptance_test_config_path(connector_name)

    logging.info(f"Start running tests for {connector_name}.")
    process = await asyncio.create_subprocess_exec(
        "sh",
        path_to_acceptance_test_runner,
        env=dict(os.environ, CONFIG_PATH=path_to_acceptance_test_config),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return_code = await process.wait()

    output_path = Path(utils.MIGRATIONS_FOLDER) / config.MODULE_NAME / "output" / str(return_code)
    output_path.mkdir(parents=True, exist_ok=True)

    contents = await process.stdout.read()
    with open(f"{output_path}/{connector_name}", "wb") as f:
        f.write(contents)

    if return_code == 0:
        logging.info(f"{connector_name} succeeded.")
    else:
        logging.info(f"{connector_name} tests failed with exit code {return_code}.")


async def semaphore_gather(coroutines, num_semaphores):
    # Limit the amount of connectors we want to test at once
    # To avoid crashing our docker by spinning up too many containers
    # Or using too much CPU. How many you can run at once effectively
    # will depend on the specs you've allocated to Docker
    semaphore = asyncio.Semaphore(num_semaphores)

    async def _wrap_coroutine(coroutine):
        async with semaphore:
            return await coroutine

    return await asyncio.gather(*(_wrap_coroutine(coroutine) for coroutine in coroutines), return_exceptions=False)


async def main(args):
    tasks = []
    for definition in utils.get_valid_definitions_from_args(args):
        connector_name = definitions.get_airbyte_connector_name_from_definition(definition)
        tasks.append(run_tests(connector_name))
    await asyncio.gather(semaphore_gather(tasks, num_semaphores=args.max_concurrency))


if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(main(args))
