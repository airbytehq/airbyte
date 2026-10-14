#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from unittest import mock
from urllib.parse import parse_qsl, urlparse

import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RateLimitedMultipleTokenAuthenticator as RateLimitedMultipleTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    UnionPartitionRouter as UnionPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def make_source(config=None, catalog=None, state=None, config_path=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config, catalog=catalog, state=state, config_path=config_path)


def _get_access_token(config: Mapping[str, Any]) -> str:
    # Token precedence mirroring the legacy `get_access_token` (and the manifest's `tokens`
    # interpolation): root-level `access_token`, then `credentials.access_token`, then
    # `credentials.personal_access_token`.
    if "access_token" in config:
        return config["access_token"]
    credentials = config.get("credentials", {})
    if "access_token" in credentials:
        return credentials["access_token"]
    if "personal_access_token" in credentials:
        return credentials["personal_access_token"]
    raise Exception("Invalid config format")


def resolve_repositories_and_organizations(source: YamlDeclarativeSource, config: Mapping[str, Any]) -> Tuple[List[str], List[str]]:
    """Resolve wildcard patterns and explicit repos by enumerating the manifest's partition
    routers — the same components manifest streams slice on at read time. Test-side port of
    the connector's former `SourceGithub._resolve_repositories_and_organizations`.

    Returns (organizations, repositories), both sorted and deduplicated.
    """
    try:
        token = _get_access_token(config)
    except Exception:
        token = ""
    if not any(t.strip() for t in (token or "").split(",")):
        raise AirbyteTracedException(
            message="No authentication tokens found in config.",
            failure_type=FailureType.config_error,
        )

    def enumerate_router(definition_name: str, partition_key: str) -> List[str]:
        router = source._constructor.create_component(
            model_type=UnionPartitionRouterModel,
            component_definition=source.resolved_manifest["definitions"][definition_name],
            config=config,
            stream_name=f"{partition_key}_resolution",
        )
        return sorted({stream_slice.partition[partition_key] for stream_slice in router.stream_slices()})

    repositories = enumerate_router("repository_partition_router", "repository")
    # `organization_resolution_partition_router`, not `organization_partition_router`: a
    # login that config only *claims* is an org must never reach the org-scoped streams.
    # The `in repository_owners` filter is a backstop: an org owning no resolved repository
    # has nothing to sync.
    repository_owners = {repository.split("/", 1)[0] for repository in repositories}
    organizations = [
        organization
        for organization in enumerate_router("organization_resolution_partition_router", "organization")
        if organization in repository_owners
    ]
    return organizations, repositories


def get_authenticator(source: YamlDeclarativeSource, config: Mapping[str, Any]) -> DeclarativeAuthenticator:
    """Return the manifest's `RateLimitedMultipleTokenAuthenticator` — the same cached
    instance the manifest streams' requesters use (`ModelToComponentFactory` caches by
    resolved constructor arguments). `config` must be the normalized config the source was
    constructed with: a differently resolved config yields a different cached instance."""
    return source._constructor.create_component(
        model_type=RateLimitedMultipleTokenAuthenticatorModel,
        component_definition=source.resolved_manifest["definitions"]["requester_base"]["authenticator"],
        config=config,
    )


def read_full_refresh(stream_instance: Stream) -> Iterable[Mapping[str, Any]]:
    for stream_slice in stream_instance.stream_slices(sync_mode=SyncMode.full_refresh):
        yield from stream_instance.read_records(stream_slice=stream_slice, sync_mode=SyncMode.full_refresh)


class ProjectsResponsesAPI:
    """
    Fake Responses API for github projects, columns, cards
    """

    projects_url = "https://api.github.com/repos/organization/repository/projects"
    columns_url = "https://api.github.com/projects/{project_id}/columns"
    cards_url = "https://api.github.com/projects/columns/{column_id}/cards"

    @classmethod
    def get_json_projects(cls, data):
        res = []
        for n, project in enumerate(data, start=1):
            name = f"project_{n}"
            res.append({"id": n, "name": name, "updated_at": project["updated_at"]})
        return res

    @classmethod
    def get_json_columns(cls, project, project_id):
        res = []
        for n, column in enumerate(project.get("columns", []), start=1):
            column_id = int(str(project_id) + str(n))
            name = f"column_{column_id}"
            res.append({"id": column_id, "name": name, "updated_at": column["updated_at"]})
        return res

    @classmethod
    def get_json_cards(cls, column, column_id):
        res = []
        for n, card in enumerate(column.get("cards", []), start=1):
            card_id = int(str(column_id) + str(n))
            name = f"card_{card_id}"
            res.append({"id": card_id, "name": name, "updated_at": card["updated_at"]})
        return res

    @classmethod
    def register(cls, data, requests_mock):
        requests_mock.get(cls.projects_url, json=cls.get_json_projects(data))
        for project_id, project in enumerate(data, start=1):
            requests_mock.get(cls.columns_url.format(project_id=project_id), json=cls.get_json_columns(project, project_id))
            for n, column in enumerate(project.get("columns", []), start=1):
                column_id = int(str(project_id) + str(n))
                requests_mock.get(cls.cards_url.format(column_id=column_id), json=cls.get_json_cards(column, column_id))


def command_check(source: Source, config):
    logger = mock.MagicMock()
    connector_config, _ = split_config(config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)


class ProbeStream(HttpStream):
    """A minimal repo-scoped stream used to drive real HTTP traffic through the shared
    authenticator: `GET repos/{repository}/probe_stream?per_page=<page size>`.

    Every GitHub stream now lives in the manifest, so there is no connector stream left to
    borrow for the authenticator tests. This stands in for one: no parent, no cache, no
    envelope, and no error handling of its own.
    """

    primary_key = "id"

    def __init__(
        self,
        repositories: List[str],
        page_size_for_large_streams: int = 10,
        api_url: str = "https://api.github.com/",
        start_date: str = "",
        **kwargs: Any,
    ) -> None:
        # `start_date` is accepted and ignored so the tests can pass the arguments a
        # semi-incremental stream used to take.
        super().__init__(**kwargs)
        self.repositories = repositories
        self.page_size = page_size_for_large_streams
        self._api_url = api_url

    @property
    def url_base(self) -> str:
        return self._api_url

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs: Any) -> str:
        return f"repos/{stream_slice['repository']}/probe_stream"

    def stream_slices(self, **kwargs: Any) -> Iterable[Optional[Mapping[str, Any]]]:
        for repository in self.repositories:
            yield {"repository": repository}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs: Any) -> Mapping[str, Any]:
        return {"per_page": self.page_size, **(next_page_token or {})}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # GitHub's `Link: <...>; rel="next"` pagination, kept because the quota tests need the
        # stream to keep issuing requests until the authenticator runs its tokens down.
        next_link = response.links.get("next", {}).get("url")
        if not next_link:
            return None
        return dict(parse_qsl(urlparse(next_link).query))

    def get_cursor(self) -> None:
        # Without this, `HttpStream` hands the stream a `ResumableFullRefreshCursor` and reads a
        # single page per slice. The quota tests need every page to be requested in one pass.
        return None

    def parse_response(self, response: requests.Response, **kwargs: Any) -> Iterable[Mapping[str, Any]]:
        yield from response.json()

    def get_json_schema(self) -> Mapping[str, Any]:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "properties": {}}
