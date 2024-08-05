# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable

import certifi
from snoop import logger
from mitmproxy import http, io  # type: ignore
from mitmproxy.addons import default_addons, script
from mitmproxy.master import Master
from mitmproxy.options import Options


class MitmProxy:
    proxy_host = "0.0.0.0"

    def __init__(self, proxy_port: int, har_dump_path: Path, replay_session_path: str | None = None) -> None:
        self.proxy_port = proxy_port
        self.har_dump_path = har_dump_path
        self.proxy_process = None
        self.session_path = tempfile.NamedTemporaryFile(delete=False).name
        self.replay_session_path = replay_session_path
        self.http_flows = None

    def get_http_flows_from_mitm_dump(self) -> list[http.HTTPFlow]:
        """Get http flows from a mitmproxy dump file.

        Args:
            mitm_dump_path (Path): Path to the mitmproxy dump file.

        Returns:
            List[http.HTTPFlow]: List of http flows.
        """
        with open(self.session_path, "rb") as dump_file:
            return [f for f in io.FlowReader(dump_file).stream() if isinstance(f, http.HTTPFlow)]

    @property
    def mitm_command(self):
        default_command = [
            "/root/.local/share/pipx/venvs/snoop/bin/mitmdump",
            f"--listen-host={self.proxy_host}",
            f"--listen-port={self.proxy_port}",
            "--set",
            f"hardump={str(self.har_dump_path)}",
            "--save-stream-file",
            
            self.session_path,
        ]
        if self.replay_session_path is not None:
            return default_command + ["--server-replay", self.replay_session_path]
        return default_command

    def _start_mitmdump(self):
        logger.info(f"Running mitmdump: {' '.join(self.mitm_command)}")
        return subprocess.Popen(
            self.mitm_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def __enter__(self) -> MitmProxy:
        self.proxy_process = self._start_mitmdump()
        self._set_proxy_environment()
        logger.info(f"Started proxy on port {self.proxy_port}")
        return self

    def __exit__(self, *_) -> None:
        self.proxy_process.terminate()
        self.proxy_process.wait()
        self.http_flows = self.get_http_flows_from_mitm_dump()
        replay_count = len([flow for flow in self.http_flows if flow.is_replay])
        logger.info(f"Replayed {replay_count} requests")
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""

    def _set_proxy_environment(self):
        extra_ca_certificates_dir = Path("/usr/local/share/ca-certificates/extra")
        extra_ca_certificates_dir.mkdir(exist_ok=True)
        self_signed_cert_path = extra_ca_certificates_dir / "mitm.crt"
        if not self_signed_cert_path.exists():
            mitmproxy_dir = Path.home() / ".mitmproxy"
            mitmproxy_pem_path = mitmproxy_dir / "mitmproxy-ca.pem"
            while not mitmproxy_pem_path.exists():
                time.sleep(0.1)
            subprocess.run(
                ["openssl", "x509", "-in", str(mitmproxy_pem_path), "-out", str(extra_ca_certificates_dir / "mitm.crt")],
                check=True,
                capture_output=True,
            )
            subprocess.run(["update-ca-certificates", "--fresh"], check=True, capture_output=True)
        os.environ["HTTP_PROXY"] = f"{self.proxy_host}:{self.proxy_port}"
        os.environ["HTTPS_PROXY"] = f"{self.proxy_host}:{self.proxy_port}"
