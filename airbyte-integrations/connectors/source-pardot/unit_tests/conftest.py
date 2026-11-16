# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterator, Mapping
from urllib.parse import urlsplit

import requests_mock
import yaml
from freezegun import freeze_time
from pytest import MonkeyPatch, fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    """Get path to manifest.yaml, handling both CI and local environments."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))
_NOW = "2026-06-01T00:00:00Z"
METADATA_PATH = Path(__file__).parent.parent / "metadata.yaml"
ALLOWED_HOSTS = set(yaml.safe_load(METADATA_PATH.read_text())["data"]["allowedHosts"]["hosts"])


def get_source(config: Mapping[str, Any], catalog=None, state=None) -> YamlDeclarativeSource:
    """Create a YamlDeclarativeSource instance with the given config."""
    catalog = catalog or CatalogBuilder().build()
    state = StateBuilder().build() if state is None else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch):
    """Keep the CDK's HTTP request cache in memory during tests."""
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    yield


@fixture(autouse=True)
def waits(monkeypatch: MonkeyPatch) -> Iterator[list[float]]:
    """Run every test on a frozen clock. A wait is not slept: it is recorded and moves the clock forward."""
    recorded: list[float] = []
    with freeze_time(_NOW) as clock:

        def wait(seconds: float = 0, *_args: Any, **_kwargs: Any) -> None:
            if seconds:
                recorded.append(seconds)
            clock.tick(delta=timedelta(seconds=seconds))

        monkeypatch.setattr(time, "sleep", wait)
        yield recorded


@fixture(autouse=True)
def only_allowed_hosts(monkeypatch: MonkeyPatch) -> Iterator[None]:
    """Fail a test whose reads send a request to a host that `allowedHosts` in metadata.yaml does not list."""
    hosts: set[str] = set()
    send = requests_mock.adapter.Adapter.send

    def record_host(adapter: requests_mock.adapter.Adapter, request: Any, **kwargs: Any) -> Any:
        hosts.add(urlsplit(request.url).hostname)
        return send(adapter, request, **kwargs)

    monkeypatch.setattr(requests_mock.adapter.Adapter, "send", record_host)
    yield
    assert hosts <= ALLOWED_HOSTS, f"requests sent to hosts that allowedHosts does not list: {sorted(hosts - ALLOWED_HOSTS)}"
