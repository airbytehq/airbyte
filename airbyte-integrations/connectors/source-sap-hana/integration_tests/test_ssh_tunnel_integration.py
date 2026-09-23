"""SSH tunnel against a real HANA: starts a throwaway OpenSSH bastion in Docker and routes the connector through it.

    uv run pytest integration_tests -m integration -k tunnel -s

Requires Docker and a bastion-reachable HANA in secrets/config.json. The SSH key is generated per run.
"""

import json
import logging
import shutil
import subprocess
import time
from pathlib import Path

import paramiko
import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode, Type

from source_sap_hana import SourceSapHana

CONFIG_PATH = Path(__file__).parent.parent / "secrets" / "config.json"
BASTION_IMAGE = "panubo/sshd:latest"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not CONFIG_PATH.exists(), reason="secrets/config.json not found"),
    pytest.mark.skipif(shutil.which("docker") is None, reason="docker not available"),
]

logger = logging.getLogger("airbyte")


@pytest.fixture(scope="module")
def bastion(tmp_path_factory):
    """Yields (host, port, private_key_text) of a disposable SSH bastion with TCP forwarding enabled."""
    workdir = tmp_path_factory.mktemp("bastion")
    key = paramiko.RSAKey.generate(2048)
    key_file = workdir / "id_rsa"
    key.write_private_key_file(str(key_file))
    (workdir / "authorized_keys").write_text(f"{key.get_name()} {key.get_base64()} airbyte-it\n")
    (workdir / "authorized_keys").chmod(0o644)
    name = f"source-sap-hana-it-bastion-{int(time.time())}"
    subprocess.run(
        [
            "docker", "run", "-d", "--rm", "--name", name, "-p", "127.0.0.1::22",
            "-e", "SSH_USERS=airbyte:1000:1000", "-e", "TCP_FORWARDING=true",
            "-v", f"{workdir / 'authorized_keys'}:/etc/authorized_keys/airbyte:ro", BASTION_IMAGE,
        ],
        check=True,
        capture_output=True,
    )  # fmt: skip
    try:
        port = int(subprocess.run(["docker", "port", name, "22/tcp"], check=True, capture_output=True, text=True).stdout.split(":")[-1])
        for _ in range(30):  # wait for sshd
            try:
                paramiko.Transport(("127.0.0.1", port)).close()
                break
            except Exception:  # noqa: BLE001
                time.sleep(1)
        yield "127.0.0.1", port, key_file.read_text()
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


def test_check_discover_read_through_tunnel(bastion):
    host, port, private_key = bastion
    config = json.loads(CONFIG_PATH.read_text())
    config["table_name_patterns"] = ["CSKT"]
    config["tunnel_method"] = {
        "tunnel_method": "SSH_KEY_AUTH",
        "tunnel_host": host,
        "tunnel_port": port,
        "tunnel_user": "airbyte",
        "ssh_key": private_key,
    }
    source = SourceSapHana()
    status = source.check(logger, config)
    assert status.status == Status.SUCCEEDED, status.message

    streams = source.discover(logger, config).streams
    assert [s.name for s in streams] == ["CSKT"]

    configured = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=streams[0], sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
        ]
    )
    records = [m for m in source.read(logger, config, configured, []) if m.type == Type.RECORD]
    assert records
    print(f"\nread {len(records)} CSKT records through the SSH tunnel")
