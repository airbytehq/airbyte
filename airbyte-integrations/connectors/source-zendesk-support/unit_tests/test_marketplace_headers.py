# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
In Airbyte Cloud every request to Zendesk carries the Zendesk Marketplace headers: data requests, article attachment
downloads and the OAuth token refresh, for every authentication option. Outside Cloud none of them does. The OAuth
authorization code exchange, which the platform makes from the spec, carries them in every edition.
"""

import copy
import logging
from datetime import timedelta
from typing import Any, Dict, Iterator, List, Mapping, Optional

import pytest
import requests_mock
import yaml
from components import MARKETPLACE_HEADERS, MARKETPLACE_HEADERS_CONFIG_KEY, MarketplaceHeaders

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import _YAML_FILE_PATH, get_source
from .mock_server.config import ConfigBuilder
from .mock_server.response_builder import (
    ArticleAttachmentsRecordBuilder,
    ArticleAttachmentsResponseBuilder,
    ArticlesRecordBuilder,
    ArticlesResponseBuilder,
    TagsRecordBuilder,
    TagsResponseBuilder,
)
from .mock_server.utils import read_stream


_EDITION = "AIRBYTE_EDITION"
_NOT_CLOUD = [None, "", "COMMUNITY", "ENTERPRISE"]
_API = "https://d3v-airbyte.zendesk.com/api/v2"
_TOKEN_URL = "https://d3v-airbyte.zendesk.com/oauth/tokens"
_START_DATE = ab_datetime_now().subtract(timedelta(weeks=104))
_REQUEST_HEADERS_TEMPLATE = "{{ config.get('__marketplace_headers', {}) }}"


def _base_config() -> ConfigBuilder:
    return ConfigBuilder().with_subdomain("d3v-airbyte").with_start_date(_START_DATE)


def _oauth_refresh_config(token_expires_in: timedelta) -> Dict[str, Any]:
    return (
        _base_config()
        .with_oauth_refresh_credentials(
            client_id="client-id",
            client_secret="client-secret",
            refresh_token="refresh-token",
            access_token="access-token",
            token_expiry_date=ab_datetime_now().add(token_expires_in).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        .build()
    )


_API_TOKEN_CONFIG = _base_config().with_basic_auth_credentials("user@example.com", "password").build()
_LEGACY_OAUTH_CONFIG = _base_config().with_oauth_credentials("legacy-token").build()
_OAUTH_REFRESH_CONFIG = _oauth_refresh_config(timedelta(days=1))
_EXPIRED_OAUTH_REFRESH_CONFIG = _oauth_refresh_config(timedelta(days=-1))
_EVERY_AUTH_OPTION = [
    pytest.param(_API_TOKEN_CONFIG, id="api_token"),
    pytest.param(_LEGACY_OAUTH_CONFIG, id="oauth2.0"),
    pytest.param(_OAUTH_REFRESH_CONFIG, id="oauth2_refresh"),
]


def _set_edition(monkeypatch: pytest.MonkeyPatch, edition: Optional[str]) -> None:
    if edition is None:
        monkeypatch.delenv(_EDITION, raising=False)
    else:
        monkeypatch.setenv(_EDITION, edition)


def _marketplace_headers(request: Any) -> Dict[str, str]:
    return {name: value for name, value in request.headers.items() if name.lower().startswith("x-zendesk-marketplace")}


def _requests_to(mocker: requests_mock.Mocker, url: str) -> List[Any]:
    requests = [request for request in mocker.request_history if request.url.split("?")[0] == url]
    assert requests, f"No request was sent to {url}. Sent: {[request.url for request in mocker.request_history]}"
    return requests


def _mock_tags(mocker: requests_mock.Mocker) -> None:
    mocker.get(f"{_API}/tags", text=TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build().body)


def _mock_token_refresh(mocker: requests_mock.Mocker) -> None:
    mocker.post(_TOKEN_URL, json={"access_token": "new-access-token", "refresh_token": "new-refresh-token", "expires_in": 7200})


def _mock_article_attachments(mocker: requests_mock.Mocker) -> str:
    """Mocks the parent stream, the attachments list and the file itself. Returns the URL of the file."""
    article = ArticlesRecordBuilder.articles_record().with_id(123)
    attachment = ArticleAttachmentsRecordBuilder.article_attachments_record()
    mocker.get(
        f"{_API}/help_center/incremental/articles", text=ArticlesResponseBuilder.articles_response().with_record(article).build().body
    )
    mocker.get(
        f"{_API}/help_center/articles/123/attachments",
        text=ArticleAttachmentsResponseBuilder.article_attachments_response().with_record(attachment).build().body,
    )
    download_url = attachment.build()["content_url"]
    mocker.get(download_url, content=b"file content")
    return download_url


def _walk(node: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _components_of_type(component_type: str) -> List[Mapping[str, Any]]:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    return [node for node in _walk(manifest) if node.get("type") == component_type]


@pytest.mark.parametrize("config", _EVERY_AUTH_OPTION)
def test_data_request_carries_marketplace_headers_in_cloud(monkeypatch, config):
    _set_edition(monkeypatch, "CLOUD")

    with requests_mock.Mocker() as mocker:
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(config))

    assert len(output.records) == 1
    assert [_marketplace_headers(request) for request in _requests_to(mocker, f"{_API}/tags")] == [dict(MARKETPLACE_HEADERS)]


@pytest.mark.parametrize("edition", _NOT_CLOUD)
@pytest.mark.parametrize("config", _EVERY_AUTH_OPTION)
def test_data_request_has_no_marketplace_headers_outside_cloud(monkeypatch, config, edition):
    _set_edition(monkeypatch, edition)

    with requests_mock.Mocker() as mocker:
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(config))

    assert len(output.records) == 1
    assert [_marketplace_headers(request) for request in _requests_to(mocker, f"{_API}/tags")] == [{}]


@pytest.mark.parametrize("edition", ["CLOUD", "cloud"])
def test_token_refresh_carries_marketplace_headers_in_cloud(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    with requests_mock.Mocker() as mocker:
        _mock_token_refresh(mocker)
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(_EXPIRED_OAUTH_REFRESH_CONFIG))

    assert len(output.records) == 1
    refreshes = _requests_to(mocker, _TOKEN_URL)
    assert [_marketplace_headers(request) for request in refreshes] == [dict(MARKETPLACE_HEADERS)] * len(refreshes)
    assert [_marketplace_headers(request) for request in _requests_to(mocker, f"{_API}/tags")] == [dict(MARKETPLACE_HEADERS)]


@pytest.mark.parametrize("edition", _NOT_CLOUD)
def test_token_refresh_has_no_marketplace_headers_outside_cloud(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    with requests_mock.Mocker() as mocker:
        _mock_token_refresh(mocker)
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(_EXPIRED_OAUTH_REFRESH_CONFIG))

    assert len(output.records) == 1
    refreshes = _requests_to(mocker, _TOKEN_URL)
    assert [_marketplace_headers(request) for request in refreshes] == [{}] * len(refreshes)
    assert not any(name.lower().startswith("x-zendesk") for request in refreshes for name in request.headers)


def test_attachment_download_carries_marketplace_headers_in_cloud(monkeypatch):
    _set_edition(monkeypatch, "CLOUD")

    with requests_mock.Mocker() as mocker:
        download_url = _mock_article_attachments(mocker)
        output = read_stream("article_attachments", SyncMode.full_refresh, copy.deepcopy(_API_TOKEN_CONFIG))

    assert len(output.records) == 1
    assert [_marketplace_headers(request) for request in _requests_to(mocker, download_url)] == [dict(MARKETPLACE_HEADERS)]
    assert all(_marketplace_headers(request) == dict(MARKETPLACE_HEADERS) for request in mocker.request_history)


@pytest.mark.parametrize("edition", _NOT_CLOUD)
def test_attachment_download_has_no_marketplace_headers_outside_cloud(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    with requests_mock.Mocker() as mocker:
        download_url = _mock_article_attachments(mocker)
        output = read_stream("article_attachments", SyncMode.full_refresh, copy.deepcopy(_API_TOKEN_CONFIG))

    assert len(output.records) == 1
    assert [_marketplace_headers(request) for request in _requests_to(mocker, download_url)] == [{}]
    assert not any(_marketplace_headers(request) for request in mocker.request_history)


@pytest.mark.parametrize("edition, expected", [("CLOUD", dict(MARKETPLACE_HEADERS)), ("COMMUNITY", {})])
def test_check_request_follows_the_edition(monkeypatch, edition, expected):
    _set_edition(monkeypatch, edition)
    config = copy.deepcopy(_API_TOKEN_CONFIG)

    with requests_mock.Mocker() as mocker:
        _mock_tags(mocker)
        status = get_source(config=config).check(logger=logging.getLogger("airbyte"), config=config)

    assert status.status == Status.SUCCEEDED, status.message
    assert [_marketplace_headers(request) for request in mocker.request_history] == [expected] * len(mocker.request_history)


def test_every_requester_in_the_manifest_sends_the_marketplace_headers():
    """
    Only two requesters are written out in the manifest; every stream reaches one of them through `$ref`. A new
    requester that is written out, or a `$ref` sibling that sets `request_headers`, would drop the headers silently.
    """
    requesters = _components_of_type("HttpRequester")

    assert len(requesters) > 2
    assert {requester.get("request_headers") for requester in requesters} == {_REQUEST_HEADERS_TEMPLATE}
    assert not _components_of_type("CustomRequester")


def test_every_oauth_authenticator_sends_the_marketplace_headers_on_refresh():
    authenticators = _components_of_type("OAuthAuthenticator")

    assert authenticators
    for authenticator in authenticators:
        assert authenticator.get("refresh_request_headers") == {
            name: "{{ config['__marketplace_headers']['" + name + "'] | tojson if config.get('__marketplace_headers') else None }}"
            for name in MARKETPLACE_HEADERS
        }


@pytest.mark.parametrize("edition", ["CLOUD", *_NOT_CLOUD])
def test_authorization_code_exchange_sends_the_marketplace_headers_in_every_edition(monkeypatch, edition):
    """
    The platform, not the connector, exchanges the authorization code for tokens, with the headers listed under
    `access_token_headers` in the spec. The spec is the same in every edition. A non-empty `access_token_headers`
    replaces the platform's default headers, so `Content-Type` and `Accept` must stay next to the Marketplace headers.
    """
    _set_edition(monkeypatch, edition)

    spec = get_source(config=copy.deepcopy(_API_TOKEN_CONFIG)).spec(logging.getLogger("airbyte"))

    oauth_input = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification
    assert oauth_input.access_token_headers == {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        **MARKETPLACE_HEADERS,
    }


def test_marketplace_headers_are_the_three_zendesk_asks_for():
    assert list(MARKETPLACE_HEADERS) == [
        "X-Zendesk-Marketplace-Name",
        "X-Zendesk-Marketplace-Organization-Id",
        "X-Zendesk-Marketplace-App-Id",
    ]
    assert MARKETPLACE_HEADERS["X-Zendesk-Marketplace-Name"] == "Airbyte"
    assert all(isinstance(value, str) and value for value in MARKETPLACE_HEADERS.values())
    assert MARKETPLACE_HEADERS_CONFIG_KEY == "__marketplace_headers"


def test_marketplace_ids_are_the_ones_zendesk_assigned():
    """
    The Organization-Id is on the Organization page of the Zendesk Marketplace portal and the App-Id is on the
    Airbyte app listing there. Zendesk attributes the traffic by these two values.
    """
    assert MARKETPLACE_HEADERS == {
        "X-Zendesk-Marketplace-Name": "Airbyte",
        "X-Zendesk-Marketplace-Organization-Id": "5102",
        "X-Zendesk-Marketplace-App-Id": "1319815",
    }


def test_transformation_sets_only_the_marketplace_headers_in_cloud(monkeypatch):
    _set_edition(monkeypatch, "CLOUD")
    config = copy.deepcopy(_OAUTH_REFRESH_CONFIG)

    MarketplaceHeaders().transform(config)

    assert config.pop(MARKETPLACE_HEADERS_CONFIG_KEY) == dict(MARKETPLACE_HEADERS)
    assert config == _OAUTH_REFRESH_CONFIG


@pytest.mark.parametrize("edition", _NOT_CLOUD)
def test_transformation_changes_nothing_outside_cloud(monkeypatch, edition):
    _set_edition(monkeypatch, edition)
    config = copy.deepcopy(_OAUTH_REFRESH_CONFIG)

    MarketplaceHeaders().transform(config)

    assert config == _OAUTH_REFRESH_CONFIG


def test_headers_stored_in_the_config_are_not_sent_outside_cloud(monkeypatch):
    """A token rotation in Cloud writes the derived key to the stored config. Outside Cloud it must be ignored."""
    _set_edition(monkeypatch, "COMMUNITY")
    config = {**copy.deepcopy(_API_TOKEN_CONFIG), MARKETPLACE_HEADERS_CONFIG_KEY: dict(MARKETPLACE_HEADERS)}

    with requests_mock.Mocker() as mocker:
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, config)

    assert len(output.records) == 1
    assert [_marketplace_headers(request) for request in _requests_to(mocker, f"{_API}/tags")] == [{}]


def test_headers_stored_in_the_config_are_replaced_in_cloud(monkeypatch):
    """The stored copy never wins over the current values, so a change of the IDs reaches every source."""
    _set_edition(monkeypatch, "CLOUD")
    config = {
        **copy.deepcopy(_API_TOKEN_CONFIG),
        MARKETPLACE_HEADERS_CONFIG_KEY: {"X-Zendesk-Marketplace-Name": "stale", "X-Other": "stale"},
    }

    with requests_mock.Mocker() as mocker:
        _mock_tags(mocker)
        output = read_stream("tags", SyncMode.full_refresh, config)

    assert len(output.records) == 1
    (request,) = _requests_to(mocker, f"{_API}/tags")
    assert _marketplace_headers(request) == dict(MARKETPLACE_HEADERS)
    assert "X-Other" not in request.headers
