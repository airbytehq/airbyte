# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from typing import List
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "videos"
_PAGE_SIZE = 500


def _create_account_record(account_id: int, name: str = "Test Account") -> dict:
    return {
        "id": account_id,
        "name": name,
        "type": "BUSINESS",
        "status": "ACTIVE",
        "currency": "USD",
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": "2024-06-01T00:00:00.000Z",
    }


def _create_video_record(video_id: str, account_id: int, asset_name: str = "Test Video") -> dict:
    return {
        "id": f"urn:li:video:{video_id}",
        "owner": f"urn:li:organization:{account_id}",
        "duration": 30000,
        "aspectRatioWidth": 16,
        "aspectRatioHeight": 9,
        "downloadUrl": f"https://example.com/{video_id}.mp4",
        "downloadUrlExpiresAt": 1735689600000,
        "thumbnail": f"urn:li:image:{video_id}-thumb",
        "status": "AVAILABLE",
        "mediaLibraryMetadata": {
            "associatedAccount": f"urn:li:sponsoredAccount:{account_id}",
            "assetName": asset_name,
            "mediaLibraryStatus": "ACTIVE",
        },
    }


def _accounts_request():
    return LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(_PAGE_SIZE).build()


def _full_page_of_videos(account_id: int) -> List[dict]:
    """Exactly `_PAGE_SIZE` records, which is what makes OffsetIncrement ask for another page."""
    return [_create_video_record(f"FULL{index:04d}", account_id) for index in range(_PAGE_SIZE)]


@freezegun.freeze_time(_NOW.isoformat())
class TestVideosStream(TestCase):
    """
    Tests for the LinkedIn Ads 'videos' stream.

    Unlike the other account substreams, this one uses:
    - OffsetIncrement pagination injecting `start` as a request parameter (not `pageToken`)
    - full refresh only — the Videos API exposes no modification timestamp to filter on
    - a `q=associatedAccount` filter rather than a path-scoped account
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Given: Two parent accounts, each with videos in its media library
        When: Running a full refresh sync
        Then: The connector fetches videos per account and preserves the video URNs
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_account_record(111111111, "Account 1"),
                    _create_account_record(222222222, "Account 2"),
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.videos_endpoint(111111111).with_count(_PAGE_SIZE).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_video_record("AAA111", 111111111, "Video 1"),
                    _create_video_record("BBB222", 111111111, "Video 2"),
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.videos_endpoint(222222222).with_count(_PAGE_SIZE).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_video_record("CCC333", 222222222, "Video 3")]),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 3
        assert {record.record.data["id"] for record in output.records} == {
            "urn:li:video:AAA111",
            "urn:li:video:BBB222",
            "urn:li:video:CCC333",
        }
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_offset_pagination_requests_next_page(self, http_mocker: HttpMocker):
        """
        Given: A first page returning exactly `count` records, then a shorter page
        When: Running a full refresh sync
        Then: The connector asks for the next offset and returns records from both pages

        This is the behaviour that distinguishes `videos` from the other substreams, which
        paginate on `pageToken`. A regression here would silently truncate every account's
        media library at 500 videos.
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.videos_endpoint(111111111).with_count(_PAGE_SIZE).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(_full_page_of_videos(111111111)),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.videos_endpoint(111111111).with_count(_PAGE_SIZE).with_start(_PAGE_SIZE).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_video_record("LAST999", 111111111, "Last Video")]),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == _PAGE_SIZE + 1
        assert "urn:li:video:LAST999" in {record.record.data["id"] for record in output.records}

    @HttpMocker()
    def test_media_library_metadata_is_preserved(self, http_mocker: HttpMocker):
        """
        Given: A video carrying the nested `mediaLibraryMetadata` object
        When: Running a full refresh sync
        Then: The nested object and its declared properties survive record processing

        `mediaLibraryMetadata` is the only nested object in the schema, and it is what ties an
        asset to a sponsored account, so it must not be flattened away or dropped.
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.videos_endpoint(111111111).with_count(_PAGE_SIZE).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_video_record("AAA111", 111111111, "Launch teaser")]),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["mediaLibraryMetadata"] == {
            "associatedAccount": "urn:li:sponsoredAccount:111111111",
            "assetName": "Launch teaser",
            "mediaLibraryStatus": "ACTIVE",
        }
        assert record["duration"] == 30000
