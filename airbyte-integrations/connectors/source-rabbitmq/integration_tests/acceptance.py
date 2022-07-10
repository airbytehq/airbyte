#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any
import pytest
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from testcontainers.rabbitmq import RabbitMqContainer

pytest_plugins = ("source_acceptance_test.plugin",)
rabbit: RabbitMqContainer

def rabbitmq_setup() -> RabbitMqContainer:
    rabbit_container = RabbitMqContainer('rabbitmq:management-alpine')
    rabbit_container.start()
    while not rabbit_container.readiness_probe:
        print('RabbitMQ is not ready')
    return rabbit_container

def _get_rabbitmq() -> RabbitMqContainer:
    if rabbit in None:
        return rabbitmq_setup()
    else: 
        return rabbit

def generate_messages(connection_params: ConnectionParameters, exhcange: str):
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as channel:
            channel.basic_publish(exchange=exhcange, body='sample')
        

@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    # TODO: setup test dependencies
    rabbitmq_container = rabbitmq_setup()
    generate_messages(rabbitmq_container.get_connection_params(), 'AIRBYTE_ACCEPTENCE')
    yield
    # TODO: clean up test dependencies

def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    rabbit_container = _get_rabbitmq()
    rabbit_container.stop(force=True, delete_volume=True)