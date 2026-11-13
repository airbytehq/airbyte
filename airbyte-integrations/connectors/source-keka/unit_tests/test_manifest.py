# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import fnmatch
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jsonschema
import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


CONNECTOR_DIR = Path(__file__).resolve().parents[1]
CONFIG = {
    "subdomain": "example-company",
    "client_id": "test-client",
    "client_secret": "test-secret",
    "api_key": "test-key",
    "grant_type": "kekaapi",
    "scope": "kekaapi",
}
STREAM_PATHS = {
    "Employees": "/hris/employees",
    "Attendance": "/time/attendance",
    "Clients": "/psa/clients",
    "Projects": "/psa/projects",
    "Project Timesheets": "/psa/timeentries",
    "Leave Type": "/time/leavetypes",
    "Leave Request": "/time/leaverequests",
}


@pytest.mark.parametrize("stream_name,path", STREAM_PATHS.items())
def test_company_url_authentication_and_pagination(monkeypatch, stream_name, path):
    pages = []
    login_requests = []
    hosts = yaml.safe_load((CONNECTOR_DIR / "metadata.yaml").read_text())["data"]["allowedHosts"]["hosts"]

    def send(adapter, request, **kwargs):
        url = urlparse(request.url)
        assert any(fnmatch.fnmatch(url.hostname, host) for host in hosts)
        if url.hostname == "login.keka.com":
            assert url.path == "/connect/token"
            assert request.method == "POST"
            assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
            assert parse_qs(request.body) == {key: [value] for key, value in CONFIG.items() if key != "subdomain"}
            login_requests.append(request)
            body = {"access_token": "test-access-token", "expires_in": 86400, "token_type": "Bearer"}
        else:
            assert url.hostname == "example-company.keka.com"
            assert url.path == "/api/v1" + path
            assert request.method == "GET"
            assert request.headers["Authorization"] == "Bearer test-access-token"
            params = parse_qs(url.query)
            assert params["pageSize"] == ["100"]
            page = int(params["pageNumber"][0])
            assert page == len(pages) + 1
            pages.append(page)
            ids = range(100) if page == 1 else [100]
            body = {
                "data": [{"id": str(i), "identifier": str(i)} for i in ids],
                "pageNumber": page,
                "pageSize": 100,
                "nextPage": "?pageNumber=2&pageSize=100" if page == 1 else None,
            }
        response = requests.Response()
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response._content = json.dumps(body).encode()
        response.request = request
        response.url = request.url
        return response

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", send)
    source = YamlDeclarativeSource(str(CONNECTOR_DIR / "manifest.yaml"), config=CONFIG)
    stream = next(stream for stream in source.streams(CONFIG) if stream.name == stream_name)
    records = [record for partition in stream.generate_partitions() for record in partition.read()]

    assert len(records) == 101
    assert pages == [1, 2]
    assert len(login_requests) == 1


@pytest.mark.parametrize("subdomain", [None, "", "https://acme.keka.com", "acme.keka.com", "acme/path", "-acme"])
def test_company_subdomain_is_required_and_not_a_url(subdomain):
    schema = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())["spec"]["connection_specification"]
    config = dict(CONFIG)
    if subdomain is None:
        del config["subdomain"]
    else:
        config["subdomain"] = subdomain
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(config, schema)


def test_valid_company_subdomain():
    schema = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())["spec"]["connection_specification"]
    jsonschema.validate(CONFIG, schema)
