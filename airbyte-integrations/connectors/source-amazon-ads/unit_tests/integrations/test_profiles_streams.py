# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .ad_requests import OAuthRequestBuilder, ProfilesRequestBuilder
from .ad_responses import OAuthResponseBuilder, ProfilesResponseBuilder
from .ad_responses.records import ProfilesRecordBuilder
from .config import ConfigBuilder
from .utils import read_stream


class TestProfilesStream(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _given_oauth(self, http_mocker: HttpMocker, config: dict) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(
                client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
            ).build(),
            OAuthResponseBuilder.token_response().build(),
        )

    @HttpMocker()
    def test_profiles_request_includes_access_level_view(self, http_mocker: HttpMocker):
        """
        Verify that the profiles endpoint includes accessLevel=view so that
        accounts with view-level OAuth grants (e.g. Vendor Central) are returned.
        """
        config = self._config
        self._given_oauth(http_mocker, config)

        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response().with_record(ProfilesRecordBuilder.profiles_record()).build(),
        )

        output = read_stream("profiles", SyncMode.full_refresh, config)
        assert len(output.records) == 1
        assert output.records[0].record.data["profileId"] == 1

    @HttpMocker()
    def test_profiles_filtered_request_includes_access_level_view(self, http_mocker: HttpMocker):
        """
        Verify that the profiles_filtered (used as a parent stream partition router)
        also includes accessLevel=view.
        """
        config = self._config
        self._given_oauth(http_mocker, config)

        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response().with_record(ProfilesRecordBuilder.profiles_record()).build(),
        )

        read_stream("sponsored_brands_campaigns", SyncMode.full_refresh, config)
        # The profiles request was matched with accessLevel=view — if it hadn't been
        # included, the HttpMocker would raise an error for an unexpected request.
        # We don't assert on records here because the downstream sponsored_brands_campaigns
        # request will fail (not mocked), but the profiles request itself succeeded.
