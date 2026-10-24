# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import re
from urllib.parse import parse_qs, urlsplit

from source_commercetools.components import CommerceToolsOauth2Authenticator
from source_commercetools.source import SourceCommercetools

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {
    "region": "us-central1",
    "host": "gcp",
    "project_key": "my-project",
    "client_id": "cid",
    "client_secret": "csecret",
    "start_date": "2024-01-01",
}
AUTH_URL = "https://auth.us-central1.gcp.commercetools.com/oauth/token"
API_URL = "https://api.us-central1.gcp.commercetools.com/my-project/customers"


def test_streams_discovered():
    source = SourceCommercetools(config=CONFIG)
    streams = source.streams(CONFIG)

    assert {stream.name for stream in streams} == {"customers", "discount_codes", "orders", "payments", "products"}


def test_custom_authenticator_requests_client_credentials_token(requests_mock):
    requests_mock.post(AUTH_URL, json={"access_token": "tok", "expires_in": 3600})
    source = SourceCommercetools(config=CONFIG)
    stream = source.streams(CONFIG)[0]
    authenticator = stream._stream_partition_generator._partition_factory._retriever.requester.authenticator

    assert isinstance(authenticator, CommerceToolsOauth2Authenticator)
    assert authenticator.get_access_token() == "tok"

    request = requests_mock.last_request
    body = parse_qs(request.text)
    assert body["grant_type"] == ["client_credentials"]
    assert body["scope"] == ["manage_project:my-project"]
    if "client_id" in body or "client_secret" in body:
        assert body["client_id"] == ["cid"]
        assert body["client_secret"] == ["csecret"]
    else:
        expected_credentials = base64.b64encode(b"cid:csecret").decode()
        assert request.headers["Authorization"] == f"Basic {expected_credentials}"


def test_read_customers_uses_bearer_token(requests_mock):
    requests_mock.post(AUTH_URL, json={"access_token": "tok", "expires_in": 3600})
    requests_mock.get(
        re.compile(rf"^{re.escape(API_URL)}(?:\?.*)?$"),
        json={
            "results": [{"id": "customer-1", "lastModifiedAt": "2024-01-02T00:00:00.000Z"}],
            "total": 1,
            "offset": 0,
            "limit": 500,
        },
    )
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="customers", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    source = SourceCommercetools(catalog=catalog, config=CONFIG)
    output = read(source, config=CONFIG, catalog=catalog)

    assert len(output.records) == 1
    api_request = next(request for request in requests_mock.request_history if request.url.startswith(API_URL))
    assert urlsplit(api_request.url).path == "/my-project/customers"
    query = parse_qs(urlsplit(api_request.url).query)
    assert query["limit"] == ["500"]
    assert query.get("offset", ["0"]) == ["0"]
    assert query["var.date"] == ["2024-01-01T00:00:00.000000+0000"]
    assert api_request.headers["Authorization"] == "Bearer tok"
