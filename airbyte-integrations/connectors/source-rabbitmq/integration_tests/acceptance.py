#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from testcontainers.rabbitmq import RabbitMqContainer

pytest_plugins = ("source_acceptance_test.plugin",)


def create_environment():
    with RabbitMqContainer('rabbitmq:management-alpine') as rabbitmq:
        while not rabbitmq.readiness_probe:
            print('RabbitMQ is not ready')

@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    # TODO: setup test dependencies
    create_environment()
    yield
    # TODO: clean up test dependencies
