#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import os.path
import shutil
import tempfile
import time
from pathlib import Path
from typing import Mapping
from zipfile import ZipFile

import docker
import pytest
import requests
from airbyte_cdk import AirbyteLogger
from docker.errors import APIError
from netifaces import AF_INET, ifaddresses, interfaces
from requests.exceptions import ConnectionError

logger = AirbyteLogger()
TMP_FOLDER = tempfile.mkdtemp()


def get_local_ip() -> str:
    all_interface_ips = []
    for iface_name in interfaces():
        all_interface_ips += [i["addr"] for i in ifaddresses(iface_name).setdefault(AF_INET, [{"addr": None}]) if i["addr"]]
    logger.info(f"detected interface IPs: {all_interface_ips}")
    for ip in sorted(all_interface_ips):
        if not ip.startswith("127."):
            return ip

    assert False, "not found an non-localhost interface"


@pytest.fixture(scope="session")
def minio_credentials() -> Mapping:
    config_template = Path(__file__).parent / "config_minio.template.json"
    assert config_template.is_file() is not None, f"not found {config_template}"
    config_file = Path(__file__).parent / "config_minio.json"
    config_file.write_text(config_template.read_text().replace("<local_ip>", get_local_ip()))
    with open(str(config_file)) as f:
        return json.load(f)


@pytest.fixture(scope="session", autouse=True)
def minio_setup(minio_credentials):
    with ZipFile("./integration_tests/minio_data.zip") as archive:
        archive.extractall(TMP_FOLDER)
    client = docker.from_env()
    # Minio should be attached to non-localhost interface.
    # Because another test container should have direct connection to it
    local_ip = get_local_ip()
    logger.debug(f"minio settings: {minio_credentials}")
    try:
        container = client.containers.run(
            image="minio/minio:RELEASE.2021-10-06T23-36-31Z",
            command=f"server {TMP_FOLDER}",
            name="ci_test_minio",
            auto_remove=True,
            volumes=[f"/{TMP_FOLDER}/minio_data:/{TMP_FOLDER}"],
            detach=True,
            ports={"9000/tcp": (local_ip, 9000)},
        )
    except APIError as err:
        if err.status_code == 409:
            for container in client.containers.list():
                if container.name == "ci_test_minio":
                    logger.info("minio was started before")
                    break
        else:
            raise

    check_url = f"http://{local_ip}:9000/minio/health/live"
    while True:
        try:
            data = requests.get(check_url)
        except ConnectionError as err:
            logger.warn(f"minio error: {err}")
            time.sleep(0.5)
            continue
        if data.status_code == 200:
            break
        logger.info("Run a minio/minio container...")
    yield

    # if os.path.exists(TMP_FOLDER):
    #     shutil.rmtree(TMP_FOLDER)

    # logger.info("minio was stopped")
    # container.stop()
