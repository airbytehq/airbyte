# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch

import freezegun
import pytest

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStreamStatus, SyncMode
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .helpers import given_post_comments, given_posts, given_ticket_forms
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    PostCommentsRecordBuilder,
    PostCommentsResponseBuilder,
    PostCommentVotesRecordBuilder,
    PostCommentVotesResponseBuilder,
    PostsRecordBuilder,
    PostsResponseBuilder,
)
from .utils import (
    datetime_to_string,
    extract_cursor_value_from_state,
    get_log_messages_by_log_level,
    get_partition_ids_from_state,
    read_stream,
    string_to_datetime,
)


_NOW = datetime.now(timezone.utc)


@freezegun.freeze_time(_NOW.isoformat())
class TestPostsCommentVotesStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(weeks=104)))
            .build()
        )

    def get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_posts_comments_votes_then_return_records(self, http_mocker):
        """
        A normal full refresh sync without pagination
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        post = posts_record_builder.build()

        posts_comments_record_builder = given_post_comments(
            http_mocker, string_to_datetime(self._config["start_date"]), post["id"], api_token_authenticator
        )
        post_comment = posts_comments_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentVotesResponseBuilder.post_comment_votes_response()
            .with_record(PostCommentVotesRecordBuilder.post_commetn_votes_record())
            .build(),
        )

        output = read_stream("post_comment_votes", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_parent_comments_when_read_then_return_records_from_both_parents(self, http_mocker):
        """
        Test nested substream with 2+ parent comments (per playbook requirement).
        Verifies that child records are fetched for each parent comment across different posts.

        Structure: posts (grandparent) → post_comments (parent) → post_comment_votes (child)
        """
        api_token_authenticator = self.get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        # Setup 2 grandparent posts with explicit IDs
        posts_record_builder_1 = (
            PostsRecordBuilder.posts_record()
            .with_id(1001)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(seconds=1))))
        )
        posts_record_builder_2 = (
            PostsRecordBuilder.posts_record()
            .with_id(1002)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(seconds=2))))
        )

        # Mock the grandparent endpoint with both posts
        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_endpoint(api_token_authenticator)
            .with_start_time(datetime_to_string(start_date))
            .with_page_size(100)
            .build(),
            PostsResponseBuilder.posts_response().with_record(posts_record_builder_1).with_record(posts_record_builder_2).build(),
        )

        post1 = posts_record_builder_1.build()
        post2 = posts_record_builder_2.build()

        # Setup parent comment for post1
        comment1_builder = (
            PostCommentsRecordBuilder.post_comments_record()
            .with_id(2001)
            .with_field(FieldPath("post_id"), post1["id"])
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(seconds=3))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comments_endpoint(api_token_authenticator, post1["id"])
            .with_start_time(datetime_to_string(start_date))
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.post_comments_response().with_record(comment1_builder).build(),
        )
        comment1 = comment1_builder.build()

        # Setup parent comment for post2
        comment2_builder = (
            PostCommentsRecordBuilder.post_comments_record()
            .with_id(2002)
            .with_field(FieldPath("post_id"), post2["id"])
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(seconds=4))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comments_endpoint(api_token_authenticator, post2["id"])
            .with_start_time(datetime_to_string(start_date))
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.post_comments_response().with_record(comment2_builder).build(),
        )
        comment2 = comment2_builder.build()

        # Mock child votes for comment1 (from post1)
        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post1["id"], comment1["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentVotesResponseBuilder.post_comment_votes_response()
            .with_record(PostCommentVotesRecordBuilder.post_commetn_votes_record().with_id(3001))
            .build(),
        )

        # Mock child votes for comment2 (from post2)
        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post2["id"], comment2["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentVotesResponseBuilder.post_comment_votes_response()
            .with_record(PostCommentVotesRecordBuilder.post_commetn_votes_record().with_id(3002))
            .build(),
        )

        output = read_stream("post_comment_votes", SyncMode.full_refresh, self._config)

        # Verify records from both parent comments
        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 3001 in record_ids
        assert 3002 in record_ids

    @HttpMocker()
    def test_given_403_error_when_read_posts_comments_then_skip_stream(self, http_mocker):
        """
        Get a 403 error and then skip the stream
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        post = posts_record_builder.build()

        posts_comments_record_builder = given_post_comments(
            http_mocker, string_to_datetime(self._config["start_date"]), post["id"], api_token_authenticator
        )
        post_comment = posts_comments_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("post_comment_votes", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0
        assert output.get_stream_statuses("post_comment_votes")[-1] == AirbyteStreamStatus.INCOMPLETE
        assert any(
            [
                "failed with status code '403' and error message" in error
                for error in get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
            ]
        )

    @HttpMocker()
    def test_given_404_error_when_read_posts_comments_then_skip_stream(self, http_mocker):
        """
        Get a 404 error and then skip the stream
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        post = posts_record_builder.build()

        posts_comments_record_builder = given_post_comments(
            http_mocker, string_to_datetime(self._config["start_date"]), post["id"], api_token_authenticator
        )
        post_comment = posts_comments_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("post_comment_votes", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0
        assert output.get_stream_statuses("post_comment_votes")[-1] == AirbyteStreamStatus.INCOMPLETE
        assert any(
            [
                "failed with status code '404' and error message" in error
                for error in get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
            ]
        )

    @HttpMocker()
    def test_given_500_error_when_read_posts_comments_then_stop_syncing(self, http_mocker):
        """
        Get a 500 error and then stop syncing
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        post = posts_record_builder.build()

        posts_comments_record_builder = given_post_comments(
            http_mocker, string_to_datetime(self._config["start_date"]), post["id"], api_token_authenticator
        )
        post_comment = posts_comments_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("post_comment_votes", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any(["Internal server error" in error for error in error_logs])


@freezegun.freeze_time(_NOW.isoformat())
class TestPostsCommentVotesStreamIncremental(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(weeks=104)))
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_now(self, http_mocker):
        """
        A normal incremental sync without pagination
        """
        api_token_authenticator = self._get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        post_updated_at = string_to_datetime(self._config["start_date"]).add(timedelta(minutes=5))
        posts_record_builder = given_posts(
            http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator, post_updated_at
        )
        post = posts_record_builder.build()

        post_comments_updated_at = string_to_datetime(self._config["start_date"]).add(timedelta(minutes=10))
        post_comments_record_builder = given_post_comments(
            http_mocker,
            string_to_datetime(self._config["start_date"]),
            post["id"],
            api_token_authenticator,
            post_comments_updated_at,
        )
        post_comment = post_comments_record_builder.build()

        post_comment_votes_record_builder = PostCommentVotesRecordBuilder.post_commetn_votes_record()
        post_comment_votes = post_comment_votes_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentVotesResponseBuilder.post_comment_votes_response()
            .with_record(PostCommentVotesRecordBuilder.post_commetn_votes_record())
            .build(),
        )

        output = read_stream("post_comment_votes", SyncMode.incremental, self._config)
        assert len(output.records) == 1

        assert output.most_recent_state.stream_descriptor.name == "post_comment_votes"

        # Use flexible state assertion that handles different CDK state formats
        state_dict = output.most_recent_state.stream_state.__dict__
        expected_cursor_value = str(int(string_to_datetime(post_comment_votes["updated_at"]).timestamp()))
        actual_cursor_value = extract_cursor_value_from_state(state_dict, "updated_at")
        assert actual_cursor_value == expected_cursor_value, f"Expected cursor {expected_cursor_value}, got {actual_cursor_value}"

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker):
        """
        Simplified incremental sync test for nested substream - verifies that:
        1. Records are returned
        2. State is produced
        3. State cursor matches the latest record's updated_at

        This replaces the complex state+pagination test which tested CDK internals
        rather than connector behavior.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        # Setup grandparent post
        posts_record_builder = given_posts(http_mocker, start_date, api_token_authenticator)
        post = posts_record_builder.build()

        # Setup parent post_comment
        post_comments_record_builder = given_post_comments(
            http_mocker,
            start_date,
            post["id"],
            api_token_authenticator,
        )
        post_comment = post_comments_record_builder.build()

        # Create 2 comment votes with different timestamps
        older_vote_time = start_date.add(timedelta(days=1))
        newer_vote_time = start_date.add(timedelta(days=2))

        older_vote_builder = (
            PostCommentVotesRecordBuilder.post_commetn_votes_record()
            .with_field(FieldPath("updated_at"), datetime_to_string(older_vote_time))
            .with_id("vote_1001")
        )

        newer_vote_builder = (
            PostCommentVotesRecordBuilder.post_commetn_votes_record()
            .with_field(FieldPath("updated_at"), datetime_to_string(newer_vote_time))
            .with_id("vote_1002")
        )

        # Mock the comment votes endpoint with both records (no pagination)
        http_mocker.get(
            ZendeskSupportRequestBuilder.post_comment_votes_endpoint(api_token_authenticator, post["id"], post_comment["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentVotesResponseBuilder.post_comment_votes_response()
            .with_record(older_vote_builder)
            .with_record(newer_vote_builder)
            .build(),
        )

        # Read stream
        output = read_stream("post_comment_votes", SyncMode.incremental, self._config)

        # Verify records returned
        assert len(output.records) == 2

        # Verify state produced
        assert output.most_recent_state.stream_descriptor.name == "post_comment_votes"

        # Verify state cursor matches the NEWER (latest) vote timestamp
        state_dict = output.most_recent_state.stream_state.__dict__
        expected_cursor_value = str(int(newer_vote_time.timestamp()))
        actual_cursor_value = extract_cursor_value_from_state(state_dict, "updated_at")
        assert actual_cursor_value == expected_cursor_value, f"Expected state cursor to match latest record timestamp"
