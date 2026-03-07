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
    ArticleCommentVotesRecordBuilder,
    ArticleCommentVotesResponseBuilder,
    ArticlesRecordBuilder,
    ArticlesResponseBuilder,
)
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestArticleCommentVotesStreamFullRefresh(TestCase):
    """Test article_comment_votes stream which is a nested substream (articles -> article_comments -> article_comment_votes)."""

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
    def test_given_one_page_when_read_article_comment_votes_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        article_id = 123
        comment_id = 456

        article_builder = (
            ArticlesRecordBuilder.articles_record()
            .with_id(article_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder).build(),
        )

        comment_builder = (
            ArticleCommentsRecordBuilder.article_comments_record()
            .with_id(comment_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=2))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article_id).with_any_query_params().build(),
            ArticleCommentsResponseBuilder.article_comments_response().with_record(comment_builder).build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comment_votes_endpoint(api_token_authenticator, article_id, comment_id)
            .with_any_query_params()
            .build(),
            ArticleCommentVotesResponseBuilder.article_comment_votes_response()
            .with_record(ArticleCommentVotesRecordBuilder.article_comment_votes_record())
            .build(),
        )

        output = read_stream("article_comment_votes", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_parent_comments_when_read_then_return_records_from_both_parents(self, http_mocker):
        """
        Test nested substream with 2+ parent comments per playbook requirement.
        Structure: articles (grandparent) -> article_comments (parent) -> article_comment_votes (child)
        """
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        article1_id = 1001
        article2_id = 1002
        comment1_id = 2001
        comment2_id = 2002

        article_builder_1 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(article1_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        article_builder_2 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(article2_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=2))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder_1).with_record(article_builder_2).build(),
        )

        comment1_builder = (
            ArticleCommentsRecordBuilder.article_comments_record()
            .with_id(comment1_id)
            .with_field(FieldPath("source_id"), article1_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=3))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article1_id).with_any_query_params().build(),
            ArticleCommentsResponseBuilder.article_comments_response().with_record(comment1_builder).build(),
        )

        comment2_builder = (
            ArticleCommentsRecordBuilder.article_comments_record()
            .with_id(comment2_id)
            .with_field(FieldPath("source_id"), article2_id)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=4))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comments_endpoint(api_token_authenticator, article2_id).with_any_query_params().build(),
            ArticleCommentsResponseBuilder.article_comments_response().with_record(comment2_builder).build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comment_votes_endpoint(api_token_authenticator, article1_id, comment1_id)
            .with_any_query_params()
            .build(),
            ArticleCommentVotesResponseBuilder.article_comment_votes_response()
            .with_record(ArticleCommentVotesRecordBuilder.article_comment_votes_record().with_id(3001))
            .build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_comment_votes_endpoint(api_token_authenticator, article2_id, comment2_id)
            .with_any_query_params()
            .build(),
            ArticleCommentVotesResponseBuilder.article_comment_votes_response()
            .with_record(ArticleCommentVotesRecordBuilder.article_comment_votes_record().with_id(3002))
            .build(),
        )

        output = read_stream("article_comment_votes", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 3001 in record_ids
        assert 3002 in record_ids
