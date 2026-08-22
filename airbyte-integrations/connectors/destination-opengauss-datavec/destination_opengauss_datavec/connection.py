#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional

import psycopg2

from destination_opengauss_datavec.config import OpenGaussDataVecIndexingModel, SslModeVerifyCa


def get_connection(config: OpenGaussDataVecIndexingModel, ssl_connection_options: "OpenGaussSslConnectionOptions") -> Any:
    """Open and return a psycopg2 connection. Caller is responsible for commit/rollback/close."""
    connection_options = {
        "host": config.host,
        "port": config.port,
        "dbname": config.database,
        "user": config.username,
        "password": config.credentials.password,
        "connect_timeout": 20,
        "keepalives": 1,
        "keepalives_idle": 60,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
    connection_options.update(ssl_connection_options.build())
    return psycopg2.connect(**connection_options)


class OpenGaussSslConnectionOptions:
    """Build psycopg2 SSL options from Airbyte-style certificate config."""

    def __init__(self, config: OpenGaussDataVecIndexingModel):
        self.config = config
        self._certificate_dir: Optional[TemporaryDirectory] = None

    def build(self) -> Dict[str, str]:
        ssl_mode = self.config.ssl_mode
        if isinstance(ssl_mode, SslModeVerifyCa):
            return self._build_verify_ca_options(ssl_mode)

        return {"sslmode": ssl_mode.mode}

    def _build_verify_ca_options(self, ssl_mode: SslModeVerifyCa) -> Dict[str, str]:
        certificate_dir = self._get_certificate_dir()
        options = {
            "sslmode": ssl_mode.mode,
            "sslrootcert": str(self._write_certificate_file(certificate_dir, "ca.crt", ssl_mode.ca_certificate)),
        }

        return options

    def _get_certificate_dir(self) -> Path:
        if self._certificate_dir is None:
            self._certificate_dir = TemporaryDirectory(prefix="airbyte-opengauss-ssl-")
        return Path(self._certificate_dir.name)

    def _write_certificate_file(self, directory: Path, file_name: str, content: str) -> Path:
        path = directory / file_name
        path.write_text(content, encoding="utf-8")
        return path
