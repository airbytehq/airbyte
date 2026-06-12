#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import socket
from pathlib import Path
from typing import Mapping

import paramiko
import paramiko.client
import pytest
from paramiko.ssh_exception import SSHException


HERE = Path(__file__).parent.absolute()
SSH_KEYS_DIR = HERE / "ssh_keys"

# Credentials baked into docker-compose.yml.
PASSWORD_USER = "user1"
PASSWORD = "abc123"
KEY_USER = "user2"


def _fetch_host_key(ip: str, port: int) -> paramiko.PKey:
    """
    Open a bare transport to the running SFTP container and return the host key
    it presents. The atmoz/sftp image generates its host key on startup, so the
    expected key is only known at test time.
    """
    sock = socket.create_connection((ip, port), timeout=10.0)
    transport = paramiko.Transport(sock)
    try:
        transport.start_client(timeout=10.0)
        return transport.get_remote_server_key()
    finally:
        transport.close()


def _generate_ssh_key() -> paramiko.RSAKey:
    """
    Generate an RSA keypair and publish the public half where the atmoz/sftp
    container expects it (mounted via docker-compose.yml). Returns the private
    key so tests can authenticate with it.
    """
    SSH_KEYS_DIR.mkdir(exist_ok=True)
    key = paramiko.RSAKey.generate(bits=2048)
    public_key = f"{key.get_name()} {key.get_base64()} {KEY_USER}\n"
    (SSH_KEYS_DIR / f"{KEY_USER}.pub").write_text(public_key)
    return key


@pytest.fixture(scope="session")
def ssh_private_key() -> str:
    """The private key (PEM string) matching the public key mounted into the container."""
    key = _generate_ssh_key()
    buffer = io.StringIO()
    key.write_private_key(buffer)
    return buffer.getvalue()


@pytest.fixture(scope="session")
def docker_compose_file(ssh_private_key) -> Path:
    # Depending on ssh_private_key ensures the public key file is written before
    # docker compose brings the SFTP server up.
    return HERE / "docker-compose.yml"


def is_sftp_ready(ip: str, port: int) -> bool:
    """Helper function that checks if sftp is served on provided ip address and port."""
    try:
        with paramiko.client.SSHClient() as ssh:
            # The atmoz/sftp container generates a host key on startup; accept it for test readiness checks.
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Hardcoding the credentials is okay here, we're not testing them explicitly.
            ssh.connect(ip, port=port, username=PASSWORD_USER, password=PASSWORD, look_for_keys=False, allow_agent=False)
        return True
    except (SSHException, socket.error):
        return False


@pytest.fixture(scope="module")
def config(docker_ip, docker_services) -> Mapping:
    """
    Provides the SFTP configuration (password authentication) using docker_services.
    Waits for the docker container to become available before returning the config.
    """
    port = docker_services.port_for("sftp", 22)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_sftp_ready(docker_ip, port))
    return {
        "host": docker_ip,
        "port": port,
        "username": PASSWORD_USER,
        "credentials": {"auth_method": "SSH_PASSWORD_AUTH", "auth_user_password": PASSWORD},
        "destination_path": "upload",
    }


@pytest.fixture(scope="module")
def config_ssh_key(docker_ip, docker_services, ssh_private_key) -> Mapping:
    """Provides the SFTP configuration using SSH key authentication."""
    port = docker_services.port_for("sftp", 22)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_sftp_ready(docker_ip, port))
    return {
        "host": docker_ip,
        "port": port,
        "username": KEY_USER,
        "credentials": {"auth_method": "SSH_KEY_AUTH", "auth_ssh_key": ssh_private_key},
        "destination_path": "upload",
    }


@pytest.fixture(scope="module")
def config_strict_host_key(docker_ip, docker_services) -> Mapping:
    """
    Provides a password-auth SFTP configuration that pins the container's host
    key via strict host key checking.
    """
    port = docker_services.port_for("sftp", 22)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_sftp_ready(docker_ip, port))
    host_key = _fetch_host_key(docker_ip, port)
    return {
        "host": docker_ip,
        "port": port,
        "username": PASSWORD_USER,
        "credentials": {"auth_method": "SSH_PASSWORD_AUTH", "auth_user_password": PASSWORD},
        "destination_path": "upload",
        "host_key_checking": {
            "mode": "strict",
            "host_key_type": host_key.get_name(),
            "host_key": host_key.get_base64(),
        },
    }
