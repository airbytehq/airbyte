#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import shutil, os
import tempfile
from zipfile import ZipFile
from unit_tests.test_csv_parser import TestCsvParser
import docker
import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    yield


@pytest.fixture(scope="session", autouse=True)
def minio_setup():
    client = docker.from_env()
    tmp_dir = tempfile.mkdtemp()
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(tmp_dir)
    # generates a big CSV files separately
    big_file_folder = os.path.join(tmp_dir, "big_files")
    os.makedirs(big_file_folder)
    filepath = os.path.join(big_file_folder, "file.csv")
    _, file_size = TestCsvParser.generate_big_file(filepath, 0.2, 500)

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
