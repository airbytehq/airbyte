#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise

import pytest
from base_images import root_images, sanity_checks
from base_images.errors import SanityCheckError

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.parametrize(
    "docker_image, expected_env_var_name, expected_env_var_value, expected_error",
    [
        (root_images.PYTHON_3_9_18.address, "PYTHON_VERSION", "3.9.18", does_not_raise()),
        (root_images.PYTHON_3_9_18.address, "PYTHON_VERSION", "3.9.19", pytest.raises(SanityCheckError)),
        (root_images.PYTHON_3_9_18.address, "NOT_EXISTING_ENV_VAR", "3.9.19", pytest.raises(SanityCheckError)),
    ],
)
async def test_check_env_var_with_printenv(dagger_client, docker_image, expected_env_var_name, expected_env_var_value, expected_error):
    container = dagger_client.container().from_(docker_image)
    with expected_error:
        await sanity_checks.check_env_var_with_printenv(container, expected_env_var_name, expected_env_var_value)
    container_without_printenv = container.with_exec(["rm", "/usr/bin/printenv"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_env_var_with_printenv(container_without_printenv, expected_env_var_name, expected_env_var_value)


async def test_check_timezone_is_utc(dagger_client):
    container = dagger_client.container().from_(root_images.PYTHON_3_9_18.address)
    # This containers has UTC as timezone by default
    await sanity_checks.check_timezone_is_utc(container)
    container_not_on_utc = container.with_exec(["ln", "-sf", "/usr/share/zoneinfo/Europe/Paris", "/etc/localtime"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_timezone_is_utc(container_not_on_utc)
    container_without_date = container.with_exec(["rm", "/usr/bin/date"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_timezone_is_utc(container_without_date)


async def test_check_a_command_is_available_using_version_option(dagger_client):
    container = dagger_client.container().from_(root_images.PYTHON_3_9_18.address)
    await sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
    container_without_bash = container.with_exec(["rm", "/usr/bin/bash"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_bash, "bash")
    container_without_ls = container.with_exec(["rm", "/usr/bin/ls"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_ls, "ls")
    container_without_date = container.with_exec(["rm", "/usr/bin/date"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_date, "date")
    container_without_printenv = container.with_exec(["rm", "/usr/bin/printenv"], skip_entrypoint=True)
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_printenv, "printenv")
