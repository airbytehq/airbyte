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
    container_without_printenv = container.with_exec(["rm", "/usr/bin/printenv"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_env_var_with_printenv(container_without_printenv, expected_env_var_name, expected_env_var_value)


async def test_check_timezone_is_utc(dagger_client):
    container = dagger_client.container().from_(root_images.PYTHON_3_9_18.address)
    # This containers has UTC as timezone by default
    await sanity_checks.check_timezone_is_utc(container)
    container_not_on_utc = container.with_exec(["ln", "-sf", "/usr/share/zoneinfo/Europe/Paris", "/etc/localtime"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_timezone_is_utc(container_not_on_utc)
    container_without_date = container.with_exec(["rm", "/usr/bin/date"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_timezone_is_utc(container_without_date)


async def test_check_a_command_is_available_using_version_option(dagger_client):
    container = dagger_client.container().from_(root_images.PYTHON_3_9_18.address)
    await sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
    container_without_bash = container.with_exec(["rm", "/usr/bin/bash"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_bash, "bash")
    container_without_ls = container.with_exec(["rm", "/usr/bin/ls"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_ls, "ls")
    container_without_date = container.with_exec(["rm", "/usr/bin/date"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_date, "date")
    container_without_printenv = container.with_exec(["rm", "/usr/bin/printenv"])
    with pytest.raises(SanityCheckError):
        await sanity_checks.check_a_command_is_available_using_version_option(container_without_printenv, "printenv")


async def test_check_socat_version(mocker):
    # Mocking is used in this test because it's hard to install a different socat version in the PYTHON_3_9_18 container

    # Mock the container and its 'with_exec' method
    mock_container = mocker.Mock()
    # Set the expected version
    expected_version = "1.2.3.4"

    # Mock the 'stdout' method and return an output different from the socat -V command
    mock_stdout = mocker.AsyncMock(return_value="foobar")
    mock_container.with_exec.return_value.stdout = mock_stdout

    # Run the function
    with pytest.raises(SanityCheckError) as exc_info:
        await sanity_checks.check_socat_version(mock_container, expected_version)

    # Check the error message
    assert str(exc_info.value) == "Could not parse the socat version from the output: foobar"

    # Mock the 'stdout' method and return a "socat version" line but with a version structure not matching the pattern from the socat -V command
    mock_stdout = mocker.AsyncMock(
        return_value="socat by Gerhard Rieger and contributors - see www.dest-unreach.org\nsocat version 1.1 on 06 Nov 2022 08:15:51"
    )
    mock_container.with_exec.return_value.stdout = mock_stdout

    # Run the function
    with pytest.raises(SanityCheckError) as exc_info:
        await sanity_checks.check_socat_version(mock_container, expected_version)
    # Check the error message
    assert str(exc_info.value) == "Could not find the socat version in the version output: socat version 1.1 on 06 Nov 2022 08:15:51"

    # Mock the 'stdout' method and return a correct "socat version" line but with a version different from the expected one
    mock_stdout = mocker.AsyncMock(
        return_value="socat by Gerhard Rieger and contributors - see www.dest-unreach.org\nsocat version 1.7.4.4 on 06 Nov 2022 08:15:51"
    )
    mock_container.with_exec.return_value.stdout = mock_stdout

    # Run the function
    with pytest.raises(SanityCheckError) as exc_info:
        await sanity_checks.check_socat_version(mock_container, expected_version)
    # Check the error message
    assert str(exc_info.value) == "unexpected socat version: 1.7.4.4"

    # Mock the 'stdout' method and return a correct "socat version" matching the expected one
    mock_stdout = mocker.AsyncMock(
        return_value=f"socat by Gerhard Rieger and contributors - see www.dest-unreach.org\nsocat version {expected_version} on 06 Nov 2022 08:15:51"
    )
    mock_container.with_exec.return_value.stdout = mock_stdout

    # No exception should be raised by this function call
    await sanity_checks.check_socat_version(mock_container, expected_version)
