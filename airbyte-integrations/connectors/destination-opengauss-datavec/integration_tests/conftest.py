#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import time
from contextlib import closing
from typing import Dict

import psycopg2
import pytest
from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


OPENGAUSS_IMAGE = "opengauss/opengauss-server:7.0.0-RC3.B025"
OPENGAUSS_DATABASE = "postgres"
OPENGAUSS_USERNAME = "gaussdb"
OPENGAUSS_PASSWORD = "openGauss@123"
OPENGAUSS_PORT = 5432
OPENGAUSS_READY_TIMEOUT_SECONDS = 120

testcontainers_config.ryuk_disabled = True


@pytest.fixture(scope="session")
def opengauss_container():
    container = (
        DockerContainer(OPENGAUSS_IMAGE)
        .with_env("GS_PASSWORD", OPENGAUSS_PASSWORD)
        .with_exposed_ports(OPENGAUSS_PORT)
        .waiting_for(LogMessageWaitStrategy("ready for start up").with_startup_timeout(OPENGAUSS_READY_TIMEOUT_SECONDS))
    )
    try:
        container.start()
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(OPENGAUSS_PORT))
        wait_for_opengauss(host, port)
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
def opengauss_config(opengauss_container) -> Dict:
    return {
        "processing": {
            "text_fields": ["title"],
            "metadata_fields": ["id", "title", "category"],
            "chunk_size": 1000,
            "chunk_overlap": 0,
        },
        "embedding": {
            "mode": "fake",
        },
        "indexing": {
            "host": opengauss_container.get_container_host_ip(),
            "port": int(opengauss_container.get_exposed_port(OPENGAUSS_PORT)),
            "database": OPENGAUSS_DATABASE,
            "default_schema": "public",
            "username": OPENGAUSS_USERNAME,
            "ssl_mode": {
                "mode": "disable",
            },
            "credentials": {
                "password": OPENGAUSS_PASSWORD,
            },
        },
        "omit_raw_text": False,
    }


def wait_for_opengauss(host: str, port: int) -> None:
    deadline = time.monotonic() + OPENGAUSS_READY_TIMEOUT_SECONDS
    last_error = None

    while time.monotonic() < deadline:
        try:
            with closing(
                psycopg2.connect(
                    host=host,
                    port=port,
                    dbname=OPENGAUSS_DATABASE,
                    user=OPENGAUSS_USERNAME,
                    password=OPENGAUSS_PASSWORD,
                    sslmode="disable",
                    connect_timeout=5,
                )
            ) as conn:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        return
        except Exception as exc:
            last_error = exc
            time.sleep(2)

    raise TimeoutError(f"openGauss container did not become ready: {last_error}")
