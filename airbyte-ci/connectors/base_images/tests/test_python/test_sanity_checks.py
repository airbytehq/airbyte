#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise

import pytest
from base_images import root_images
from base_images.errors import SanityCheckError
from base_images.python import sanity_checks

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.parametrize(
    "docker_image, python_version, expected_error",
    [
        (root_images.PYTHON_3_9_18.address, "3.9.18", does_not_raise()),
        (root_images.PYTHON_3_9_18.address, "3.9.19", pytest.raises(SanityCheckError)),
        ("hello-world:latest", "3.9.19", pytest.raises(SanityCheckError)),
    ],
)
async def test_check_python_version(dagger_client, docker_image, python_version, expected_error):
    container_with_python = dagger_client.container().from_(docker_image)
    with expected_error:
        await sanity_checks.check_python_version(container_with_python, python_version)


@pytest.mark.parametrize(
    "docker_image, pip_version, expected_error",
    [
        (root_images.PYTHON_3_9_18.address, "23.0.1", does_not_raise()),
        (root_images.PYTHON_3_9_18.address, "23.0.2", pytest.raises(SanityCheckError)),
        ("hello-world:latest", "23.0.1", pytest.raises(SanityCheckError)),
    ],
)
async def test_check_pip_version(dagger_client, docker_image, pip_version, expected_error):
    container_with_python = dagger_client.container().from_(docker_image)
    with expected_error:
        await sanity_checks.check_pip_version(container_with_python, pip_version)


@pytest.mark.parametrize(
    "docker_image, poetry_version, expected_error",
    [
        ("pfeiffermax/python-poetry:1.6.0-poetry1.6.1-python3.9.18-slim-bookworm", "1.6.1", does_not_raise()),
        ("pfeiffermax/python-poetry:1.6.0-poetry1.4.2-python3.9.18-bookworm", "1.6.1", pytest.raises(SanityCheckError)),
        (root_images.PYTHON_3_9_18.address, "23.0.2", pytest.raises(SanityCheckError)),
    ],
)
async def test_check_poetry_version(dagger_client, docker_image, poetry_version, expected_error):
    container_with_python = dagger_client.container().from_(docker_image)
    with expected_error:
        await sanity_checks.check_poetry_version(container_with_python, poetry_version)
