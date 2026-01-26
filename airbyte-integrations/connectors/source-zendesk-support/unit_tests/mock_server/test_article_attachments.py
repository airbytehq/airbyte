# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ArticleAttachmentsRecordBuilder,
    ArticleAttachmentsResponseBuilder,
    ArticlesRecordBuilder,
    ArticlesResponseBuilder,
)
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestArticleAttachmentsStreamFullRefresh(TestCase):
    """Test article_attachments stream which is a substream of articles."""

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
    def test_given_one_page_when_read_article_attachments_then_return_records(self, http_mocker):
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

        attachment_builder = ArticleAttachmentsRecordBuilder.article_attachments_record()

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_attachments_endpoint(api_token_authenticator, article["id"])
            .with_any_query_params()
            .build(),
            ArticleAttachmentsResponseBuilder.article_attachments_response().with_record(attachment_builder).build(),
        )

        # Mock the file download URL (content_url) that the CDK's file_uploader tries to access
        attachment = attachment_builder.build()
        http_mocker.get(
            HttpRequest(url=attachment["content_url"]),
            HttpResponse(body=b"fake file content", status_code=200),
        )

        output = read_stream("article_attachments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_parent_articles_when_read_then_return_records_from_both_parents(self, http_mocker):
        """Test substream with 2+ parent records per playbook requirement."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        article_builder_1 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(301)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        article_builder_2 = (
            ArticlesRecordBuilder.articles_record()
            .with_id(302)
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=2))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            ArticlesResponseBuilder.articles_response().with_record(article_builder_1).with_record(article_builder_2).build(),
        )

        article1 = article_builder_1.build()
        article2 = article_builder_2.build()

        attachment_builder_1 = (
            ArticleAttachmentsRecordBuilder.article_attachments_record()
            .with_id(3001)
            .with_field(FieldPath("content_url"), "https://company.zendesk.com/hc/article_attachments/3001/test1.pdf")
        )
        attachment_builder_2 = (
            ArticleAttachmentsRecordBuilder.article_attachments_record()
            .with_id(3002)
            .with_field(FieldPath("content_url"), "https://company.zendesk.com/hc/article_attachments/3002/test2.pdf")
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_attachments_endpoint(api_token_authenticator, article1["id"])
            .with_any_query_params()
            .build(),
            ArticleAttachmentsResponseBuilder.article_attachments_response().with_record(attachment_builder_1).build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.article_attachments_endpoint(api_token_authenticator, article2["id"])
            .with_any_query_params()
            .build(),
            ArticleAttachmentsResponseBuilder.article_attachments_response().with_record(attachment_builder_2).build(),
        )

        # Mock the file download URLs (content_url) that the CDK's file_uploader tries to access
        attachment1 = attachment_builder_1.build()
        attachment2 = attachment_builder_2.build()
        http_mocker.get(
            HttpRequest(url=attachment1["content_url"]),
            HttpResponse(body=b"fake file content 1", status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=attachment2["content_url"]),
            HttpResponse(body=b"fake file content 2", status_code=200),
        )

        output = read_stream("article_attachments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 3001 in record_ids
        assert 3002 in record_ids
