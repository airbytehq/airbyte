#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import docker
import yaml
import os
import time

pytest_plugins = ("connector_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    with open('docker_run_config.yaml', 'r') as f:
        docker_run_config = yaml.safe_load(f)

    image = docker_run_config['saphana']['image']
    ports = {p.split(':')[0]:p.split(':')[1] for p in docker_run_config['saphana']['ports']}
    command = docker_run_config['saphana']['command']
    volumes = [os.path.abspath(vol) for vol in docker_run_config['saphana']['volumes']]

    client = docker.from_env()
    container = client.containers.run(
        image=image,
        ports=ports,
        command=command,
        volumes=volumes,
        detach=True
    )

    finished = False
    while not finished:
        finished = container.logs(tail=1).decode()==('Startup finished!\n')
        time.sleep(20)
    
    yield
    
    container.kill()
    container.remove()
