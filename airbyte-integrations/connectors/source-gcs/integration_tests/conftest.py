# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import os
import shutil
import time
import uuid
from typing import Any, Mapping

import docker
import google
import pytest
import source_gcs
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

from .utils import get_docker_ip


LOCAL_GCP_PORT = 4443

from urllib.parse import urlparse, urlunparse


# Monkey patch generate_signed_url to use media_link in integration tests with local server
def generate_signed_url(self, *args, **kwargs):
    parsed_url = urlparse(self.media_link)
    new_netloc = parsed_url.netloc.replace("0.0.0.0", get_docker_ip())
    modified_url = urlunparse(parsed_url._replace(netloc=new_netloc))
    self._properties["mediaLink"] = modified_url
    return modified_url


google.cloud.storage.blob.Blob.generate_signed_url = generate_signed_url


# Monkey patch gcs_client to use AnonymousCredentials in integration tests with local server
def _initialize_gcs_client(self):
    if self.config is None:
        raise ValueError("Source config is missing; cannot create the GCS client.")
    if self._gcs_client is None:
        self._gcs_client = storage.Client(
            credentials=AnonymousCredentials(),
            project="test",
            client_options={"api_endpoint": f"http://{get_docker_ip()}:{LOCAL_GCP_PORT}"},
        )

    return self._gcs_client


source_gcs.stream_reader.SourceGCSStreamReader._initialize_gcs_client = _initialize_gcs_client


@pytest.fixture(scope="session")
def docker_client() -> docker.client.DockerClient:
    return docker.from_env()


TMP_FOLDER = "/tmp/test_gcs_source"


@pytest.fixture(scope="session", autouse=True)
def connector_setup_fixture(docker_client) -> None:
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    shutil.copytree(f"{os.path.dirname(__file__)}/integration_bucket_data", TMP_FOLDER)

    container = docker_client.containers.run(
        image="fsouza/fake-gcs-server",
        command=["-scheme", "http"],
        name=f"gcs_integration_{uuid.uuid4().hex}",
        hostname="gcs-server",
        ports={LOCAL_GCP_PORT: ("0.0.0.0", LOCAL_GCP_PORT)},
        detach=True,
        volumes={f"{TMP_FOLDER}": {"bind": "/data", "mode": "rw"}},
    )
    time.sleep(5)

    yield

    container.kill()
    container.remove()
