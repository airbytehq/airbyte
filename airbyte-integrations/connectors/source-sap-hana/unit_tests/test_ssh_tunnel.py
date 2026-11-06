# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""SSH tunnel tests against a real in-process paramiko SSH server that forwards to a local echo server."""

from __future__ import annotations

import io
import logging
import socket
import threading

import paramiko
import pytest
from source_sap_hana import SourceSapHana
from source_sap_hana.ssh_tunnel import SshTunnel, TunnelConfig, host_key_fingerprint, load_private_key

from airbyte_cdk.models import Status


logger = logging.getLogger("airbyte")
HOST_KEY = paramiko.RSAKey.generate(1024)
CLIENT_KEY = paramiko.RSAKey.generate(1024)


def _private_key_text(key: paramiko.PKey) -> str:
    buffer = io.StringIO()
    key.write_private_key(buffer)
    return buffer.getvalue()


def _listen() -> socket.socket:
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(8)
    return sock


class EchoServer:
    def __init__(self) -> None:
        self.sock = _listen()
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            threading.Thread(target=self._echo, args=(conn,), daemon=True).start()

    @staticmethod
    def _echo(conn: socket.socket) -> None:
        with conn:
            while data := conn.recv(65536):
                conn.sendall(data)


class SshServer(paramiko.ServerInterface):
    """Accepts user 'tunnel' with password 'secret' or CLIENT_KEY, and forwards direct-tcpip channels."""

    def __init__(self) -> None:
        self.sock = _listen()
        self.port = self.sock.getsockname()[1]
        self.transports: list[paramiko.Transport] = []
        self.destinations: list[tuple[str, int]] = []
        threading.Thread(target=self._serve, daemon=True).start()

    # paramiko.ServerInterface
    def get_allowed_auths(self, username: str) -> str:
        return "password,publickey"

    def check_auth_password(self, username: str, password: str) -> int:
        ok = (username, password) == ("tunnel", "secret")
        return paramiko.AUTH_SUCCESSFUL if ok else paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        ok = username == "tunnel" and key.get_fingerprint() == CLIENT_KEY.get_fingerprint()
        return paramiko.AUTH_SUCCESSFUL if ok else paramiko.AUTH_FAILED

    def check_channel_direct_tcpip_request(self, chanid: int, origin: tuple[str, int], destination: tuple[str, int]) -> int:
        self.destinations.append(destination)
        return paramiko.OPEN_SUCCEEDED

    def _serve(self) -> None:
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            transport = paramiko.Transport(conn)
            transport.add_server_key(HOST_KEY)
            transport.start_server(server=self)
            self.transports.append(transport)
            threading.Thread(target=self._channels, args=(transport,), daemon=True).start()

    def _channels(self, transport: paramiko.Transport) -> None:
        while transport.is_active():
            channel = transport.accept(1)
            if channel is None:
                continue
            upstream = socket.create_connection(self.destinations[-1])
            threading.Thread(target=self._pump, args=(channel, upstream), daemon=True).start()
            threading.Thread(target=self._pump, args=(upstream, channel), daemon=True).start()

    @staticmethod
    def _pump(src, dst) -> None:
        try:
            while data := src.recv(65536):
                dst.sendall(data)
        except OSError:
            pass
        finally:
            dst.close()


@pytest.fixture
def echo() -> EchoServer:
    return EchoServer()


@pytest.fixture
def ssh() -> SshServer:
    return SshServer()


def _roundtrip(port: int, payload: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as conn:
        conn.sendall(payload)
        received = b""
        while len(received) < len(payload):
            chunk = conn.recv(65536)
            if not chunk:
                break
            received += chunk
        return received


def password_tunnel(ssh: SshServer, password: str = "secret", fingerprint: str | None = None) -> TunnelConfig:
    raw = {
        "tunnel_method": "SSH_PASSWORD_AUTH",
        "tunnel_host": "127.0.0.1",
        "tunnel_port": ssh.port,
        "tunnel_user": "tunnel",
        "tunnel_user_password": password,
    }
    if fingerprint is not None:
        raw["tunnel_host_key_fingerprint"] = fingerprint
    return TunnelConfig.from_mapping(raw)


def test_no_tunnel():
    assert TunnelConfig.from_mapping(None) is None
    assert TunnelConfig.from_mapping({"tunnel_method": "NO_TUNNEL"}) is None


@pytest.mark.parametrize(
    "raw",
    [
        {"tunnel_method": "SSH_KEY_AUTH", "tunnel_host": "h", "tunnel_user": "u"},
        {"tunnel_method": "SSH_PASSWORD_AUTH", "tunnel_host": "h", "tunnel_user": "u"},
        {"tunnel_method": "SSH_PASSWORD_AUTH", "tunnel_user": "u", "tunnel_user_password": "p"},
        {"tunnel_method": "TELEPORT"},
    ],
)
def test_invalid_tunnel_config(raw):
    with pytest.raises(ValueError):
        TunnelConfig.from_mapping(raw)


def test_load_private_key_rejects_garbage():
    with pytest.raises(ValueError, match="Unable to parse"):
        load_private_key("not a key")


def test_password_tunnel_forwards_bytes(ssh, echo):
    with SshTunnel(password_tunnel(ssh), "127.0.0.1", echo.port, logger) as tunnel:
        assert _roundtrip(tunnel.local_port, b"hello hana" * 1000) == b"hello hana" * 1000
    assert ssh.destinations[-1] == ("127.0.0.1", echo.port)


def test_key_tunnel_forwards_bytes(ssh, echo):
    config = TunnelConfig.from_mapping(
        {
            "tunnel_method": "SSH_KEY_AUTH",
            "tunnel_host": "127.0.0.1",
            "tunnel_port": ssh.port,
            "tunnel_user": "tunnel",
            "ssh_key": _private_key_text(CLIENT_KEY),
        }
    )
    with SshTunnel(config, "127.0.0.1", echo.port, logger) as tunnel:
        assert _roundtrip(tunnel.local_port, b"ping") == b"ping"


def test_wrong_password_fails_fast(ssh, echo):
    with pytest.raises(paramiko.AuthenticationException):
        SshTunnel(password_tunnel(ssh, "wrong"), "127.0.0.1", echo.port, logger).start()


def test_tunnel_reconnects_after_transport_loss(ssh, echo):
    with SshTunnel(password_tunnel(ssh), "127.0.0.1", echo.port, logger) as tunnel:
        assert _roundtrip(tunnel.local_port, b"one") == b"one"
        for transport in ssh.transports:
            transport.close()  # bastion drops the SSH session
        assert _roundtrip(tunnel.local_port, b"two") == b"two"
        assert len(ssh.transports) >= 2


def test_source_routes_hana_through_tunnel(ssh, echo, hana, config):
    """check() opens the tunnel and hands hdbcli the local end of it (fake HANA records the connect kwargs)."""
    config.update(
        encrypt=True,
        tunnel_method={
            "tunnel_method": "SSH_PASSWORD_AUTH",
            "tunnel_host": "127.0.0.1",
            "tunnel_port": ssh.port,
            "tunnel_user": "tunnel",
            "tunnel_user_password": "secret",
        },
    )
    status = SourceSapHana().check(logger, config)
    assert status.status == Status.SUCCEEDED, status.message
    kwargs = hana.connect_calls[-1]
    assert kwargs["address"] == "127.0.0.1"
    assert kwargs["port"] != config["port"]
    assert kwargs["sslHostNameInCertificate"] == "hana.example.com"


def test_pinned_host_key_is_accepted(ssh, echo):
    with SshTunnel(password_tunnel(ssh, fingerprint=host_key_fingerprint(HOST_KEY)), "127.0.0.1", echo.port, logger) as tunnel:
        assert _roundtrip(tunnel.local_port, b"pinned") == b"pinned"


def test_host_key_mismatch_is_rejected(ssh, echo):
    wrong = host_key_fingerprint(paramiko.RSAKey.generate(1024))
    with pytest.raises(paramiko.SSHException, match="host key mismatch"):
        SshTunnel(password_tunnel(ssh, fingerprint=wrong), "127.0.0.1", echo.port, logger).start()


def test_unpinned_host_key_is_logged(ssh, echo, caplog):
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        with SshTunnel(password_tunnel(ssh), "127.0.0.1", echo.port, logger):
            pass
    assert host_key_fingerprint(HOST_KEY) in caplog.text


def test_fingerprint_matches_openssh_format():
    fingerprint = host_key_fingerprint(HOST_KEY)
    assert fingerprint.startswith("SHA256:") and not fingerprint.endswith("=") and len(fingerprint) == 50
