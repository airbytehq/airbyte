#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Mapping

import requests  # noqa
from airbyte_cdk import AirbyteLogger
from netifaces import AF_INET, ifaddresses, interfaces
from pytest import fixture
from requests.exceptions import ConnectionError  # noqa
from source_s3 import SourceS3

logger = AirbyteLogger()

TMP_FOLDER = os.path.join(tempfile.gettempdir(), "test_generated")

shutil.rmtree(TMP_FOLDER, ignore_errors=True)
os.makedirs(TMP_FOLDER, exist_ok=True)


def pytest_generate_tests(metafunc: Any) -> None:
    if "file_info" in metafunc.fixturenames:
        cases = metafunc.cls.cached_cases()
        metafunc.parametrize("file_info", cases.values(), ids=cases.keys())


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """whole test run finishes."""
    shutil.rmtree(TMP_FOLDER, ignore_errors=True)


@fixture(name="config")
def config_fixture(tmp_path):
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as fp:
        json.dump(
            {
                "dataset": "dummy",
                "provider": {"bucket": "test-test", "endpoint": "test", "use_ssl": "test", "verify_ssl_cert": "test"},
                "path_pattern": "",
                "format": {"delimiter": "\\t"},
            },
            fp,
        )
    source = SourceS3()
    config = source.read_config(config_file)
    return config


def get_local_ip() -> str:
    all_interface_ips: List[str] = []
    for iface_name in interfaces():
        all_interface_ips += [i["addr"] for i in ifaddresses(iface_name).setdefault(AF_INET, [{"addr": None}]) if i["addr"]]
    logger.info(f"detected interface IPs: {all_interface_ips}")
    for ip in sorted(all_interface_ips):
        if not ip.startswith("127."):
            return ip

    assert False, "not found an non-localhost interface"


@fixture(scope="session")
def minio_credentials() -> Mapping[str, Any]:
    config_template = Path(__file__).parent / "config_minio.template.json"
    assert config_template.is_file() is not None, f"not found {config_template}"
    config_file = Path(__file__).parent / "config_minio.json"
    config_file.write_text(config_template.read_text().replace("<local_ip>", get_local_ip()))

    with open(str(config_file)) as f:
        credentials = json.load(f)
    return credentials
