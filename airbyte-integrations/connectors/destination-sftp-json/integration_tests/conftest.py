#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import socket
from pathlib import Path
from typing import Mapping

import paramiko
import paramiko.client
import pytest
from paramiko.ssh_exception import SSHException


HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    return HERE / "docker-compose.yml"


def is_sftp_ready(ip: str, config: Mapping) -> bool:
    """Helper function that checks if sftp is served on provided ip address and port."""
    try:
        with paramiko.client.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            # hardcoding the credentials is okay here, we're not testing them explicitly.
            ssh.connect(
                ip,
                port=config["port"],
                username=config["username"],
                password=config["password"],
            )
        return True
    except (SSHException, socket.error):
        return False


@pytest.fixture(scope="module")
def config(docker_ip, docker_services) -> Mapping:
    """
    Provides the SFTP configuration using docker_services.
    Waits for the docker container to become available before returning the config.
    """
    port = docker_services.port_for("sftp", 22)
    config_data = {"host": docker_ip, "port": port, "username": "user1", "password": "abc123", "destination_path": "upload"}
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_sftp_ready(docker_ip, config_data))
    return config_data
