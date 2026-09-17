# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "videos"
_ACCOUNTS_PAGE_SIZE = 500

# What LinkedIn returns on a video or post the authenticated user cannot read.
_FORBIDDEN_BODY = json.dumps(
    {
        "message": "Accessing this video resource is forbidden. Please check your permissions for this resource",
        "status": 403,
    }
)
_NOT_FOUND_BODY = json.dumps({"message": "Could not find entity", "status": 404, "code": "NOT_FOUND"})
# What the Posts API returns when the URN in the path is not a post URN
# (e.g. a Message Ads creative's urn:li:adInMailContent reference).
_INVALID_URN_TYPE_BODY = json.dumps(
    {
        "message": "resourceKey value urn:li:adInMailContent:5001 must be a ugcPost URN",
        "status": 400,
        "code": "INVALID_URN_TYPE",
    }
)
# What the Posts API returns when the path key is not a URN at all
# (e.g. the literal `None` produced by an explicitly null content.reference).
_MALFORMED_URN_BODY = json.dumps(
    {
        "message": "Invalid URN in path key 'postsId': 'None' is not a valid URN",
        "status": 400,
    }
)


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


def _create_creative_record(creative_id: int, account_id: int, post_urn: str = None) -> dict:
    record = {
        "id": f"urn:li:sponsoredCreative:{creative_id}",
        "account": f"urn:li:sponsoredAccount:{account_id}",
        "campaign": f"urn:li:sponsoredCampaign:{creative_id}",
        "isServing": True,
        "createdAt": "2024-01-01T00:00:00+0000",
        "lastModifiedAt": "2024-06-01T00:00:00+0000",
    }
    if post_urn is not None:
        record["content"] = {"reference": post_urn}
    return record


def _create_post_record(post_urn: str, media_urn: str) -> dict:
    return {
        "id": post_urn,
        "author": "urn:li:organization:2414183",
        "lifecycleState": "PUBLISHED",
        "publishedAt": 1717200000000,
        "content": {"media": {"id": media_urn, "title": "Test media"}},
    }


def _create_video_record(video_id: str, duration: int = 30000) -> dict:
    return {
        "id": f"urn:li:video:{video_id}",
        "owner": "urn:li:organization:2414183",
        "duration": duration,
        "aspectRatioWidth": 16,
        "aspectRatioHeight": 9,
        "downloadUrl": f"https://example.com/{video_id}.mp4",
        "downloadUrlExpiresAt": 1735689600000,
        "thumbnail": f"https://media.licdn.com/dms/image/{video_id}/ads-video-thumbnail_720_1280",
        "status": "AVAILABLE",
    }


def _accounts_request():
    return LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(_ACCOUNTS_PAGE_SIZE).build()


def _creatives_request(account_id: int):
    return LinkedInAdsRequestBuilder.creatives_endpoint(account_id).with_any_query_params().build()


def _single_object_response(record: dict) -> HttpResponse:
    return HttpResponse(body=json.dumps(record), status_code=200)


@freezegun.freeze_time(_NOW.isoformat())
class TestVideosStream(TestCase):
    """
    Tests for the LinkedIn Ads 'videos' stream.

    The stream resolves each creative's sponsored-content reference to its post
    (GET /rest/posts/{urn}), keeps the posts whose media is a video, and fetches each
    video individually (GET /rest/videos/{urn}). It deliberately avoids the Videos API
    `q=associatedAccount` finder, which LinkedIn gates at the application level and
    which returns 403 ACCESS_DENIED to applications holding only r_ads.
    """

    @HttpMocker()
    def test_full_refresh_resolves_videos_from_creative_posts(self, http_mocker: HttpMocker):
        """
        Given: Creatives referencing a video post, an image post, and no post at all
        When: Running a full refresh sync
        Then: Only the video referenced by the video post is fetched and emitted
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_creative_record(2001, 111111111, "urn:li:share:1000001"),
                    _create_creative_record(2002, 111111111, "urn:li:ugcPost:1000002"),
                    _create_creative_record(2003, 111111111),  # text ad: no content.reference, no post request
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000001").build(),
            _single_object_response(_create_post_record("urn:li:share:1000001", "urn:li:video:AAA111")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:ugcPost:1000002").build(),
            _single_object_response(_create_post_record("urn:li:ugcPost:1000002", "urn:li:image:BBB222")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.video_endpoint("urn:li:video:AAA111").build(),
            _single_object_response(_create_video_record("AAA111", duration=45500)),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "urn:li:video:AAA111"
        assert record["duration"] == 45500
        assert output.records[0].record.stream == _STREAM_NAME
        assert not output.errors

    @HttpMocker()
    def test_legacy_asset_reference_is_ignored(self, http_mocker: HttpMocker):
        """
        Given: A creative whose post references a legacy Assets API media (urn:li:digitalmediaAsset)
        When: Running a full refresh sync
        Then: No videos request is made and the sync completes without records or errors

        Legacy assets are not retrievable through the Videos API; this is the documented
        limitation of the stream.
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "urn:li:share:1000001")]),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000001").build(),
            _single_object_response(_create_post_record("urn:li:share:1000001", "urn:li:digitalmediaAsset:LEGACY1")),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 0
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_deleted_post_is_skipped_without_failing_the_sync(self, http_mocker: HttpMocker):
        """
        Given: Two creatives, one referencing a deleted post (404) and one a live video post
        When: Running a full refresh sync
        Then: The deleted post is skipped and the other creative's video still syncs
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_creative_record(2001, 111111111, "urn:li:share:1000001"),
                    _create_creative_record(2002, 111111111, "urn:li:share:1000002"),
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000001").build(),
            HttpResponse(body=_NOT_FOUND_BODY, status_code=404),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000002").build(),
            _single_object_response(_create_post_record("urn:li:share:1000002", "urn:li:video:CCC333")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.video_endpoint("urn:li:video:CCC333").build(),
            _single_object_response(_create_video_record("CCC333")),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "urn:li:video:CCC333"
        assert not output.errors

    @HttpMocker()
    def test_inmail_creative_reference_is_skipped_without_failing_the_sync(self, http_mocker: HttpMocker):
        """
        Given: Two creatives, one referencing Message Ads InMail content (urn:li:adInMailContent,
               rejected by the Posts API with 400 INVALID_URN_TYPE) and one a live video post
        When: Running a full refresh sync
        Then: The InMail reference is skipped and the other creative's video still syncs
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_creative_record(2001, 111111111, "urn:li:adInMailContent:5001"),
                    _create_creative_record(2002, 111111111, "urn:li:share:1000002"),
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:adInMailContent:5001").build(),
            HttpResponse(body=_INVALID_URN_TYPE_BODY, status_code=400),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000002").build(),
            _single_object_response(_create_post_record("urn:li:share:1000002", "urn:li:video:CCC333")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.video_endpoint("urn:li:video:CCC333").build(),
            _single_object_response(_create_video_record("CCC333")),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "urn:li:video:CCC333"
        assert not output.errors

    @HttpMocker()
    def test_null_creative_reference_is_skipped_without_failing_the_sync(self, http_mocker: HttpMocker):
        """
        Given: Two creatives, one carrying an explicitly null content.reference (the partition
               is still emitted and requests the literal path posts/None, which LinkedIn
               rejects with 400) and one referencing a live video post
        When: Running a full refresh sync
        Then: The null reference is skipped and the other creative's video still syncs
        """
        config = ConfigBuilder().build()

        creative_with_null_reference = _create_creative_record(2001, 111111111)
        creative_with_null_reference["content"] = {"reference": None}

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    creative_with_null_reference,
                    _create_creative_record(2002, 111111111, "urn:li:share:1000002"),
                ]
            ),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("None").build(),
            HttpResponse(body=_MALFORMED_URN_BODY, status_code=400),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000002").build(),
            _single_object_response(_create_post_record("urn:li:share:1000002", "urn:li:video:CCC333")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.video_endpoint("urn:li:video:CCC333").build(),
            _single_object_response(_create_video_record("CCC333")),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "urn:li:video:CCC333"
        assert not output.errors

    @HttpMocker()
    def test_forbidden_video_is_skipped_without_failing_the_sync(self, http_mocker: HttpMocker):
        """
        Given: A video post whose video the authenticated user cannot read (403)
        When: Running a full refresh sync
        Then: The video is skipped and the sync completes without failing
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            _accounts_request(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )
        http_mocker.get(
            _creatives_request(111111111),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_creative_record(2001, 111111111, "urn:li:share:1000001")]),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.posts_endpoint("urn:li:share:1000001").build(),
            _single_object_response(_create_post_record("urn:li:share:1000001", "urn:li:video:AAA111")),
        )
        http_mocker.get(
            LinkedInAdsRequestBuilder.video_endpoint("urn:li:video:AAA111").build(),
            HttpResponse(body=_FORBIDDEN_BODY, status_code=403),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        )

        assert len(output.records) == 0
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
