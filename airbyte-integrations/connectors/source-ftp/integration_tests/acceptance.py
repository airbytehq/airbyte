import os
import time
import pytest
import docker

pytest_plugins = ("source_acceptance_test.plugin",)

@pytest.fixture(scope="module", autouse=True)
def connector_setup():
    docker_client = docker.from_env()
    dir_path = os.getcwd() + "/integration_tests"

    container = docker_client.containers.run(
        "atmoz/sftp",
        f"foo:pass",
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
