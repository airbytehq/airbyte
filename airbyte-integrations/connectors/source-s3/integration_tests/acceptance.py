#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import shutil
import tempfile
from zipfile import ZipFile

import docker
import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """ This fixture is a placeholder for external resources that acceptance test might require."""
    yield


@pytest.fixture(scope="session", autouse=True)
def minio_setup():
    client = docker.from_env()
    tmp_dir = tempfile.mkdtemp()
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(tmp_dir)

    container = client.containers.run(
        "minio/minio",
        f"server {tmp_dir}/minio_data",
        network_mode="host",
        volumes=["/tmp:/tmp", "/var/run/docker.sock:/var/run/docker.sock"],
        detach=True,
    )
    yield
    shutil.rmtree(tmp_dir)
    container.stop()
