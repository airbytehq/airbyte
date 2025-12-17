# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import AttributeDefinitionsRecordBuilder, AttributeDefinitionsResponseBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestAttributeDefinitionsStreamFullRefresh(TestCase):
    """Test attribute_definitions stream which is a full refresh only stream (base_stream)."""

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
    def test_given_one_page_when_read_attribute_definitions_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.attribute_definitions_endpoint(api_token_authenticator).build(),
            AttributeDefinitionsResponseBuilder.attribute_definitions_response()
            .with_record(AttributeDefinitionsRecordBuilder.attribute_definitions_record())
            .build(),
        )

        output = read_stream("attribute_definitions", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
