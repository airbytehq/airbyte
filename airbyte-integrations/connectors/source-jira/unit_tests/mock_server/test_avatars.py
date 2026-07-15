# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "avatars"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestAvatarsStream(TestCase):
    """
    Tests for the Jira 'avatars' stream.

    This is a full refresh stream without pagination.
    Uses ListPartitionRouter with slices: issuetype, project, user
    Endpoint: /rest/api/3/avatar/{slice}/system
    Extract field: system
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh_all_slices(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns avatars from all slices (issuetype, project, user).
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Issue type avatars
        issuetype_avatars = {
            "system": [
                {"id": "10000", "isSystemAvatar": True, "isSelected": False, "isDeletable": False},
                {"id": "10001", "isSystemAvatar": True, "isSelected": False, "isDeletable": False},
            ]
        }

        # Project avatars
        project_avatars = {
            "system": [
                {"id": "10100", "isSystemAvatar": True, "isSelected": False, "isDeletable": False},
            ]
        }

        # User avatars
        user_avatars = {
            "system": [
                {"id": "10200", "isSystemAvatar": True, "isSelected": False, "isDeletable": False},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "issuetype").build(),
            HttpResponse(body=json.dumps(issuetype_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "project").build(),
            HttpResponse(body=json.dumps(project_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "user").build(),
            HttpResponse(body=json.dumps(user_avatars), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 4

        avatar_ids = [r.record.data["id"] for r in output.records]
        assert "10000" in avatar_ids
        assert "10001" in avatar_ids
        assert "10100" in avatar_ids
        assert "10200" in avatar_ids

    @HttpMocker()
    def test_avatar_properties(self, http_mocker: HttpMocker):
        """
        Test that avatar properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        issuetype_avatars = {
            "system": [
                {
                    "id": "10000",
                    "isSystemAvatar": True,
                    "isSelected": True,
                    "isDeletable": False,
                    "fileName": "bug.svg",
                },
            ]
        }

        project_avatars = {"system": []}
        user_avatars = {"system": []}

        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "issuetype").build(),
            HttpResponse(body=json.dumps(issuetype_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "project").build(),
            HttpResponse(body=json.dumps(project_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "user").build(),
            HttpResponse(body=json.dumps(user_avatars), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "10000"
        assert record["isSystemAvatar"] is True
        assert record["isSelected"] is True

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        empty_avatars = {"system": []}

        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "issuetype").build(),
            HttpResponse(body=json.dumps(empty_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "project").build(),
            HttpResponse(body=json.dumps(empty_avatars), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.avatars_endpoint(_DOMAIN, "user").build(),
            HttpResponse(body=json.dumps(empty_avatars), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
