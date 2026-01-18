# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
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
from .helpers import given_posts, given_posts_multiple
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, PostCommentsRecordBuilder, PostCommentsResponseBuilder
from .utils import (
    datetime_to_string,
    extract_cursor_value_from_state,
    get_log_messages_by_log_level,
    get_partition_ids_from_state,
    read_stream,
    string_to_datetime,
)


_NOW = ab_datetime_now()
_START_DATE = ab_datetime_now().subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestPostsCommentsStreamFullRefresh(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_posts_comments_then_return_records(self, http_mocker):
        """
        A normal full refresh sync without pagination
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        post = posts_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response().with_record(PostCommentsRecordBuilder.posts_comments_record()).build(),
        )

        output = read_stream("post_comments", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_parent_posts_when_read_then_return_records_from_both_parents(self, http_mocker):
        """
        Test substream with 2+ parent records (per playbook requirement).
        Verifies that child records are fetched for each parent post.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Setup 2 parent posts
        post1_builder, post2_builder = given_posts_multiple(
            http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator
        )
        post1 = post1_builder.build()
        post2 = post2_builder.build()

        # Mock child endpoint for post 1
        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post1["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response()
            .with_record(PostCommentsRecordBuilder.posts_comments_record().with_id(2001))
            .build(),
        )

        # Mock child endpoint for post 2
        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post2["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response()
            .with_record(PostCommentsRecordBuilder.posts_comments_record().with_id(2002))
            .build(),
        )

        output = read_stream("post_comments", SyncMode.full_refresh, self._config)

        # Verify records from both parent posts are returned
        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 2001 in record_ids
        assert 2002 in record_ids

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

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("post_comments", SyncMode.full_refresh, self._config)
        assert len(output.records) == 0
        assert output.get_stream_statuses("post_comments")[-1] == AirbyteStreamStatus.INCOMPLETE
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

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("post_comments", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        assert output.get_stream_statuses("post_comments")[-1] == AirbyteStreamStatus.INCOMPLETE
        assert any(
            [
                "failed with status code '404' and error message" in error
                for error in get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
            ]
        )

    @HttpMocker()
    def test_given_500_error_when_read_posts_comments_then_stop_syncing(self, http_mocker):
        """
        Get a 500 error and then stop the stream
        """
        api_token_authenticator = self.get_authenticator(self._config)
        # todo: Add this back once the CDK supports conditional streams on an endpoint
        # _ = given_ticket_forms(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)
        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        post = posts_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ErrorResponseBuilder.response_with_status(500).build(),
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("post_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0

        error_logs = get_log_messages_by_log_level(output.logs, LogLevel.ERROR)
        assert any(["Internal server error" in error for error in error_logs])


@freezegun.freeze_time(_NOW.isoformat())
class TestPostsCommentsStreamIncremental(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
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
        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        post = posts_record_builder.build()
        post_comments_record_builder = PostCommentsRecordBuilder.posts_comments_record()

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response().with_record(post_comments_record_builder).build(),
        )

        output = read_stream("post_comments", SyncMode.incremental, self._config)
        assert len(output.records) == 1

        post_comment = post_comments_record_builder.build()
        assert output.most_recent_state.stream_descriptor.name == "post_comments"

        # Use flexible state assertion that handles different CDK state formats
        state_dict = output.most_recent_state.stream_state.__dict__
        expected_cursor_value = str(int(string_to_datetime(post_comment["updated_at"]).timestamp()))
        actual_cursor_value = extract_cursor_value_from_state(state_dict, "updated_at")
        assert actual_cursor_value == expected_cursor_value, f"Expected cursor {expected_cursor_value}, got {actual_cursor_value}"

        # Verify partition contains the expected post_id
        partition_ids = get_partition_ids_from_state(state_dict, "post_id")
        assert post["id"] in partition_ids, f"Expected post_id {post['id']} in partitions, got {partition_ids}"

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker):
        """
        Simplified incremental sync test - verifies that:
        1. Records are returned
        2. State is produced
        3. State cursor matches the latest record's updated_at

        This replaces the complex state+pagination test which tested CDK internals
        rather than connector behavior.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        # Setup parent post
        posts_record_builder = given_posts(http_mocker, start_date, api_token_authenticator)
        post = posts_record_builder.build()

        # Create 2 comments with different timestamps
        older_comment_time = start_date.add(timedelta(days=1))
        newer_comment_time = start_date.add(timedelta(days=2))

        older_comment_builder = (
            PostCommentsRecordBuilder.posts_comments_record()
            .with_field(FieldPath("updated_at"), datetime_to_string(older_comment_time))
            .with_id(2001)
        )

        newer_comment_builder = (
            PostCommentsRecordBuilder.posts_comments_record()
            .with_field(FieldPath("updated_at"), datetime_to_string(newer_comment_time))
            .with_id(2002)
        )

        # Mock the comments endpoint with both records (no pagination)
        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response()
            .with_record(older_comment_builder)
            .with_record(newer_comment_builder)
            .build(),
        )

        # Read stream
        output = read_stream("post_comments", SyncMode.incremental, self._config)

        # Verify records returned
        assert len(output.records) == 2

        # Verify state produced
        assert output.most_recent_state.stream_descriptor.name == "post_comments"

        # Verify state cursor matches the NEWER (latest) comment timestamp
        state_dict = output.most_recent_state.stream_state.__dict__
        expected_cursor_value = str(int(newer_comment_time.timestamp()))
        actual_cursor_value = extract_cursor_value_from_state(state_dict, "updated_at")
        assert actual_cursor_value == expected_cursor_value, f"Expected state cursor to match latest record timestamp"


@freezegun.freeze_time(_NOW.isoformat())
class TestPostCommentsTransformations(TestCase):
    """Test transformations for post_comments stream.

    Per playbook: All streams that support transformations should validate
    that transformations are applied on the resulting records.

    The post_comments stream has an AddFields transformation that adds
    _airbyte_parent_id with value { 'post_id': record['post_id'], 'comment_id': record['id'] }
    """

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_record_when_read_then_airbyte_parent_id_transformation_applied(self, http_mocker):
        """Test that _airbyte_parent_id transformation is applied to records.

        The transformation adds _airbyte_parent_id field with value:
        { 'post_id': record['post_id'], 'comment_id': record['id'] }
        """
        api_token_authenticator = self._get_authenticator(self._config)
        posts_record_builder = given_posts(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        post = posts_record_builder.build()
        comment_id = 12345
        post_comments_record_builder = PostCommentsRecordBuilder.posts_comments_record().with_id(comment_id)

        http_mocker.get(
            ZendeskSupportRequestBuilder.posts_comments_endpoint(api_token_authenticator, post["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            PostCommentsResponseBuilder.posts_comments_response().with_record(post_comments_record_builder).build(),
        )

        output = read_stream("post_comments", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

        record_data = output.records[0].record.data
        # Verify _airbyte_parent_id transformation is applied
        assert "_airbyte_parent_id" in record_data, "Expected _airbyte_parent_id field to be present"
        assert record_data["_airbyte_parent_id"]["post_id"] == post["id"], "Expected post_id in _airbyte_parent_id"
        assert record_data["_airbyte_parent_id"]["comment_id"] == comment_id, "Expected comment_id in _airbyte_parent_id"
