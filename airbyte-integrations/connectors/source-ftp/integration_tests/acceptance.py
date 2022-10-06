import os
import time
import pytest
import docker

pytest_plugins = ("source_acceptance_test.plugin",)

@pytest.fixture(scope="module", autouse=True)
def connector_setup():
    docker_client = docker.from_env()
    dir_path = os.getcwd() + "/integration_tests"

    config = {
        "host": "0.0.0.0",
        "port": 22,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
    }

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"{config['username']}:{config['password']}",
        name="mysftpacceptance",
        ports={22: 22},
        volumes={
            f"{dir_path}/files": {"bind": "/home/foo/files", "mode": "rw"},
        },
        detach=True,
    )

    time.sleep(5)
    yield

    container.kill()
    container.remove()
