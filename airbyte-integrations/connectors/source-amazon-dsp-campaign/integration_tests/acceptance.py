#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
<<<<<<< HEAD
import docker
=======

>>>>>>> 9ef4df2b95 (Adding amazon-dsp-campaign connector)
pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
<<<<<<< HEAD
    # client = docker.from_env()
    # container = client.containers.run("airbyte/source-amazon-dsp-campaign:dev", detach=True)
    # yield container
    # container.stop()
=======
    # TODO: setup test dependencies if needed. otherwise remove the TODO comments
    yield
    # TODO: clean up test dependencies
>>>>>>> 9ef4df2b95 (Adding amazon-dsp-campaign connector)
