# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""SSH tunnel (local port forwarding) used when HANA is only reachable through a bastion host.

Implemented directly on paramiko: a local listening socket on 127.0.0.1 forwards every accepted
connection through a `direct-tcpip` channel to HANA. If the SSH transport dies (bastion restart,
idle timeout), it is re-established on the next connection attempt, so the connector's normal
reconnect logic also covers tunnel failures.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import logging
import select
import socket
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import paramiko


NO_TUNNEL = "NO_TUNNEL"
SSH_KEY_AUTH = "SSH_KEY_AUTH"
SSH_PASSWORD_AUTH = "SSH_PASSWORD_AUTH"


@dataclass(frozen=True)
class TunnelConfig:
    method: str
    host: str
    port: int = 22
    user: str = ""
    ssh_key: str | None = None
    password: str | None = None
    host_key_fingerprint: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> TunnelConfig | None:
        """Parses Airbyte's standard `tunnel_method` object; returns None when no tunnel is configured."""
        method = (raw or {}).get("tunnel_method", NO_TUNNEL)
        if method == NO_TUNNEL:
            return None
        if method not in (SSH_KEY_AUTH, SSH_PASSWORD_AUTH):
            raise ValueError(f"Unsupported tunnel_method {method!r}")
        assert raw is not None
        for field in ("tunnel_host", "tunnel_user"):
            if not raw.get(field):
                raise ValueError(f"SSH tunnel: '{field}' is required")
        if method == SSH_KEY_AUTH and not raw.get("ssh_key"):
            raise ValueError("SSH tunnel: 'ssh_key' is required for SSH_KEY_AUTH")
        if method == SSH_PASSWORD_AUTH and not raw.get("tunnel_user_password"):
            raise ValueError("SSH tunnel: 'tunnel_user_password' is required for SSH_PASSWORD_AUTH")
        return cls(
            method=method,
            host=raw["tunnel_host"],
            port=int(raw.get("tunnel_port") or 22),
            user=raw["tunnel_user"],
            ssh_key=raw.get("ssh_key"),
            password=raw.get("tunnel_user_password"),
            host_key_fingerprint=(raw.get("tunnel_host_key_fingerprint") or "").strip() or None,
        )


def load_private_key(text: str) -> paramiko.PKey:
    """Loads an OpenSSH/PEM private key of any type paramiko supports."""
    errors = []
    for key_class in (paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.RSAKey):
        try:
            return key_class.from_private_key(io.StringIO(text.strip() + "\n"))
        except (paramiko.SSHException, ValueError) as error:
            errors.append(f"{key_class.__name__}: {error}")
    raise ValueError("Unable to parse the SSH private key (" + "; ".join(errors) + ")")


def host_key_fingerprint(key: paramiko.PKey) -> str:
    """OpenSSH-style SHA256 fingerprint, as printed by `ssh-keygen -lf` (e.g. SHA256:MOyN...)."""
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")


class FingerprintPolicy(paramiko.MissingHostKeyPolicy):
    """Verifies the bastion host key against a configured SHA256 fingerprint.

    Without a configured fingerprint the key is trusted on first use, like Airbyte's other database
    connectors do, but its fingerprint is logged so it can be pinned via `tunnel_host_key_fingerprint`.
    """

    def __init__(self, expected: str | None, logger: logging.Logger):
        self.expected = expected
        self.logger = logger

    def missing_host_key(self, client: paramiko.SSHClient, hostname: str, key: paramiko.PKey) -> None:
        fingerprint = host_key_fingerprint(key)
        if self.expected is None:
            self.logger.warning(
                f"SSH tunnel: accepting unverified {key.get_name()} host key {fingerprint} for {hostname}; "
                "set tunnel_host_key_fingerprint to pin it"
            )
            return
        if fingerprint != self.expected:
            raise paramiko.SSHException(
                f"SSH tunnel: host key mismatch for {hostname}: server presented {fingerprint}, expected {self.expected}"
            )


class SshTunnel:
    """Forwards 127.0.0.1:<local_port> to remote_host:remote_port through an SSH server."""

    def __init__(self, config: TunnelConfig, remote_host: str, remote_port: int, logger: logging.Logger):
        self.config = config
        self.remote = (remote_host, remote_port)
        self.logger = logger
        self._client: paramiko.SSHClient | None = None
        self._lock = threading.Lock()
        self._server: socket.socket | None = None
        self._closed = threading.Event()
        self._threads: list[threading.Thread] = []
        self.local_port: int | None = None

    # -------------------------------------------------------------- lifecycle

    def __enter__(self) -> SshTunnel:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def start(self) -> None:
        self._transport()  # fail fast on bad credentials / unreachable bastion
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(16)
        server.settimeout(0.5)  # lets the accept loop notice stop() on every platform
        self._server = server
        self.local_port = server.getsockname()[1]
        self._spawn(self._accept_loop, "ssh-tunnel-accept")
        self.logger.info(
            f"SSH tunnel open: 127.0.0.1:{self.local_port} -> {self.config.user}@{self.config.host}:{self.config.port} "
            f"-> {self.remote[0]}:{self.remote[1]}"
        )

    def stop(self) -> None:
        """Closes the tunnel and waits for its threads, so nothing writes to stderr during interpreter shutdown."""
        self._closed.set()
        if self._server is not None:
            # The listening socket may already be closed; there is nothing left to release then.
            with contextlib.suppress(OSError):
                self._server.close()
        for thread in self._threads:
            thread.join(timeout=5)
        with self._lock:
            if self._client is not None:
                transport = self._client.get_transport()
                self._client.close()
                if transport is not None:
                    transport.join(timeout=5)
                self._client = None

    def _spawn(self, target: Any, name: str, *args: Any) -> None:
        thread = threading.Thread(target=target, args=args, name=name, daemon=True)
        self._threads = [t for t in self._threads if t.is_alive()] + [thread]
        thread.start()

    # ------------------------------------------------------------- internals

    def _transport(self, force_reconnect: bool = False) -> paramiko.Transport:
        with self._lock:
            transport = self._client.get_transport() if self._client else None
            if transport is not None and transport.is_active() and not force_reconnect:
                return transport
            if self._client is not None:
                self.logger.warning("SSH tunnel transport lost, reconnecting to the bastion host")
                self._client.close()
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(FingerprintPolicy(self.config.host_key_fingerprint, self.logger))
            client.connect(
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.user,
                pkey=load_private_key(self.config.ssh_key) if self.config.method == SSH_KEY_AUTH and self.config.ssh_key else None,
                password=self.config.password if self.config.method == SSH_PASSWORD_AUTH else None,
                allow_agent=False,
                look_for_keys=False,
                timeout=30,
                banner_timeout=30,
                auth_timeout=30,
            )
            transport = client.get_transport()
            assert transport is not None
            transport.set_keepalive(30)
            self._client = client
            return transport

    def _accept_loop(self) -> None:
        assert self._server is not None
        while not self._closed.is_set():
            try:
                local, peer = self._server.accept()
            except TimeoutError:
                continue
            except OSError:
                return  # server socket closed
            local.settimeout(None)
            if self._closed.is_set():
                local.close()
                return
            self._spawn(self._forward, "ssh-tunnel-forward", local, peer)

    def _forward(self, local: socket.socket, peer: tuple[str, int]) -> None:
        channel = None
        for attempt in (1, 2):
            try:
                # A transport can still look active for a moment after the bastion dropped it:
                # if the channel cannot be opened, reconnect once before giving up.
                channel = self._transport(force_reconnect=attempt == 2).open_channel("direct-tcpip", self.remote, peer)
                break
            except Exception as error:  # noqa: BLE001 - the client sees a closed socket and retries
                if attempt == 2 or self._closed.is_set():
                    if not self._closed.is_set():
                        self.logger.warning(f"SSH tunnel could not open a channel to {self.remote[0]}:{self.remote[1]}: {error}")
                    local.close()
                    return
        assert channel is not None
        try:
            while not self._closed.is_set():
                readable, _, _ = select.select([local, channel], [], [], 1.0)
                if local in readable:
                    data = local.recv(65536)
                    if not data:
                        break
                    channel.sendall(data)
                if channel in readable:
                    data = channel.recv(65536)
                    if not data:
                        break
                    local.sendall(data)
        except OSError:
            # Either side closed the connection: nothing to forward any more, clean up below.
            pass
        finally:
            channel.close()
            local.close()
