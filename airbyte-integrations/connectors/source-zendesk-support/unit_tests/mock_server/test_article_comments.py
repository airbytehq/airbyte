# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ArticleCommentsRecordBuilder,
    ArticleCommentsResponseBuilder,
    ArticlesRecordBuilder,
    ArticlesResponseBuilder,
)
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestArticleCommentsStreamFullRefresh(TestCase):
    """Test article_comments stream which is a substream of articles with transformation."""

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
    def test_given_one_page_when_read_article_comments_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        article_builder = (
            ArticlesRecordBuilder.articles_record()
            .with_id(123)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder).build(),
        )

        article = article_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ArticleCommentsResponseBuilder.article_comments_response()
            .with_record(ArticleCommentsRecordBuilder.article_comments_record())
            .build(),
        )

        output = read_stream("article_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_parent_articles_when_read_then_return_records_from_both_parents(self, http_mocker):
        """Test substream with 2+ parent records per playbook requirement."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        article_builder_1 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(101)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        article_builder_2 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(102)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=2))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder_1).with_record(article_builder_2).build(),
        )

        article1 = article_builder_1.build()
        article2 = article_builder_2.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article1["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ArticleCommentsResponseBuilder.article_comments_response()
            .with_record(ArticleCommentsRecordBuilder.article_comments_record().with_id(1001))
            .build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article2["id"])
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ArticleCommentsResponseBuilder.article_comments_response()
            .with_record(ArticleCommentsRecordBuilder.article_comments_record().with_id(1002))
            .build(),
        )

        output = read_stream("article_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1001 in record_ids
        assert 1002 in record_ids


@freezegun.freeze_time(_NOW.isoformat())
class TestArticleCommentsTransformations(TestCase):
    """Test article_comments stream transformations per playbook requirement."""

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
    def test_given_article_comment_when_read_then_airbyte_parent_id_is_added(self, http_mocker):
        """Validate that _airbyte_parent_id transformation is applied."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        article_id = 12345
        comment_id = 67890

        article_builder = (
            ArticlesRecordBuilder.articles_record()
            .with_id(article_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder).build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article_id)
            .with_start_time(self._config["start_date"])
            .with_page_size(100)
            .build(),
            ArticleCommentsResponseBuilder.article_comments_response()
            .with_record(ArticleCommentsRecordBuilder.article_comments_record().with_id(comment_id))
            .build(),
        )

        output = read_stream("article_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
        record_data = output.records[0].record.data
        assert "_airbyte_parent_id" in record_data
        # _airbyte_parent_id is a dict containing the parent stream's partition keys
        parent_id = record_data["_airbyte_parent_id"]
        if isinstance(parent_id, dict):
            # New format: dict with article_id key - verify the key exists
            assert "article_id" in parent_id, f"Expected 'article_id' key in parent_id dict, got: {parent_id}"
        else:
            # Legacy format: string containing article_id
            assert parent_id is not None, "Expected parent_id to be set"
