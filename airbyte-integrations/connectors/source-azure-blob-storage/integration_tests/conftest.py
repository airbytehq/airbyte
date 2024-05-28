# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import logging
import os
import subprocess
import time
import uuid
from typing import Any, Mapping

import azure
import docker
import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy
from fastavro import parse_schema, writer
from pandas import read_csv
from source_azure_blob_storage import SourceAzureBlobStorage

from .utils import get_docker_ip, load_config

logger = logging.getLogger("airbyte")

JSON_TO_AVRO_TYPES = {"string": "string", "integer": "long", "number": "float", "object": "record"}


# Monkey patch credentials method to make it work with "global-docker-host" inside dagger
# (original method handles only localhost and 127.0.0.1 addresses)
def _format_shared_key_credential(account_name, credential):
    credentials = {"account_key": "key1", "account_name": "account1"}
    return SharedKeyCredentialPolicy(**credentials)


azure.storage.blob._shared.base_client._format_shared_key_credential = _format_shared_key_credential


@pytest.fixture(scope="session")
def docker_client() -> docker.client.DockerClient:
    return docker.from_env()


def get_container_client() -> ContainerClient:
    docker_ip = get_docker_ip()
    blob_service_client = BlobServiceClient(f"http://{docker_ip}:10000/account1", credential="key1")
    container_client = blob_service_client.get_container_client("testcontainer")
    return container_client


def generate_random_csv_with_source_faker():
    """Generate csv files using source-faker and save output to folder: /tmp/csv"""
    subprocess.run(f"{os.path.dirname(__file__)}/csv_export/main.sh")


@pytest.fixture(scope="session", autouse=True)
def connector_setup_fixture(docker_client) -> None:
    generate_random_csv_with_source_faker()
    container = docker_client.containers.run(
        image="mcr.microsoft.com/azure-storage/azurite",
        command="azurite-blob --blobHost 0.0.0.0 -l /data --loose",
        name=f"azurite_integration_{uuid.uuid4().hex}",
        hostname="azurite",
        ports={10000: ("0.0.0.0", 10000), 10001: ("0.0.0.0", 10001), 10002: ("0.0.0.0", 10002)},
        environment={"AZURITE_ACCOUNTS": "account1:key1"},
        detach=True,
    )
    time.sleep(10)
    container_client = get_container_client()
    container_client.create_container()

    yield

    container.kill()
    container.remove()


def upload_csv_files(container_client: ContainerClient) -> None:
    """upload 30 csv files"""
    for table in ("products", "purchases", "users"):
        csv_large_file = open(f"/tmp/csv/{table}.csv", "rb").read()
        for i in range(10):
            container_client.upload_blob(f"test_csv_{table}_{i}.csv", csv_large_file, validate_content=False)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    return SourceAzureBlobStorage.read_catalog(f"{os.path.dirname(__file__)}/integration_configured_catalog/configured_catalog.json")


@pytest.fixture(name="config_csv", scope="function")
def config_csv_fixture() -> Mapping[str, Any]:
    config = load_config("config_integration_csv.json")
    config["azure_blob_storage_endpoint"] = config["azure_blob_storage_endpoint"].replace("localhost", get_docker_ip())
    container_client = get_container_client()
    upload_csv_files(container_client)
    yield config
    for blob in container_client.list_blobs():
        container_client.delete_blob(blob.name)


def upload_jsonl_files(container_client: ContainerClient) -> None:
    """upload 30 csv files"""
    for table in ("products", "purchases", "users"):
        df = read_csv(f"/tmp/csv/{table}.csv")
        df.to_json(f"/tmp/csv/{table}.jsonl", orient="records", lines=True)
        jsonl_file = open(f"/tmp/csv/{table}.jsonl", "rb").read()
        for i in range(10):
            container_client.upload_blob(f"test_jsonl_{table}_{i}.jsonl", jsonl_file, validate_content=False)


@pytest.fixture(name="config_jsonl", scope="function")
def config_jsonl_fixture() -> Mapping[str, Any]:
    config = load_config("config_integration_jsonl.json")
    config["azure_blob_storage_endpoint"] = config["azure_blob_storage_endpoint"].replace("localhost", get_docker_ip())
    container_client = get_container_client()
    upload_jsonl_files(container_client)
    yield config
    for blob in container_client.list_blobs():
        container_client.delete_blob(blob.name)


def upload_parquet_files(container_client: ContainerClient) -> None:
    """upload 30 parquet files"""
    for table in ("products", "purchases", "users"):
        df = read_csv(f"/tmp/csv/{table}.csv")
        parquet_file = df.to_parquet()
        for i in range(10):
            container_client.upload_blob(f"test_parquet_{table}_{i}.parquet", parquet_file, validate_content=False)


@pytest.fixture(name="config_parquet", scope="function")
def config_parquet_fixture() -> Mapping[str, Any]:
    config = load_config("config_integration_parquet.json")
    config["azure_blob_storage_endpoint"] = config["azure_blob_storage_endpoint"].replace("localhost", get_docker_ip())
    container_client = get_container_client()
    upload_parquet_files(container_client)
    yield config
    for blob in container_client.list_blobs():
        container_client.delete_blob(blob.name)


def upload_avro_files(container_client: ContainerClient, json_schemas: Mapping) -> None:
    """upload 30 avro files"""
    for table in ("products", "purchases", "users"):
        schema = {
            "name": table,
            "namespace": "test",
            "type": "record",
            "fields": [
                {
                    "name": k,
                    "type": JSON_TO_AVRO_TYPES.get(v.get("type")[1] if isinstance(v.get("type"), list) else v.get("type")),
                    "default": "" if (v.get("type")[1] if isinstance(v.get("type"), list) else v.get("type")) == "string" else 0,
                }
                for k, v in json_schemas.get(table)["properties"].items()
            ],
        }
        df_records = read_csv(f"/tmp/csv/{table}.csv").fillna("").to_dict("records")
        parsed_schema = parse_schema(schema)
        with open(f"/tmp/csv/{table}.avro", "wb") as out:
            writer(out, parsed_schema, df_records)
        avro_file = open(f"/tmp/csv/{table}.avro", "rb").read()
        for i in range(10):
            container_client.upload_blob(f"test_avro_{table}_{i}.avro", avro_file, validate_content=False)


@pytest.fixture(name="config_avro", scope="function")
def config_avro_fixture(configured_catalog) -> Mapping[str, Any]:
    schemas = {x.stream.name: x.stream.json_schema for x in configured_catalog.streams}
    config = load_config("config_integration_avro.json")
    config["azure_blob_storage_endpoint"] = config["azure_blob_storage_endpoint"].replace("localhost", get_docker_ip())
    container_client = get_container_client()
    upload_avro_files(container_client, schemas)
    yield config
    for blob in container_client.list_blobs():
        container_client.delete_blob(blob.name)
