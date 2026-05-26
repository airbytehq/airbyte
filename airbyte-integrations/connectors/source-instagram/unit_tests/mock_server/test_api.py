# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)

from ..conftest import get_source
from .config import ConfigBuilder
from .pagination import NEXT_PAGE_TOKEN, InstagramPaginationStrategy
from .request_builder import get_account_request
from .response_builder import SECOND_BUSINESS_ACCOUNT_ID, build_response, get_account_response, get_multiple_accounts_response
from .utils import config, read_output


logger = logging.getLogger("airbyte")

_FIELDS = ["id", "instagram_business_account"]

_STREAM_NAME = "Api"


def _get_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME.lower(), __file__),
        records_path=FieldPath("data"),
        pagination_strategy=InstagramPaginationStrategy(request=get_account_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    )


def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME.lower(), __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


class TestFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        # Verify transformations are applied (page_id, business_account_id in account field)
        record = output.records[0].record.data
        assert "account" in record
        assert "page_id" in record["account"]
        assert "business_account_id" in record["account"]

    @HttpMocker()
    def test_accounts_with_no_instagram_business_account_field(self, http_mocker: HttpMocker) -> None:
        test = "not_instagram_business_account"
        mocked_response = json.dumps(find_template(f"api_for_{test}", __file__))
        http_mocker.get(get_account_request().build(), HttpResponse(mocked_response, 200))
        original_records = json.loads(mocked_response)

        output = self._read(config_=config())
        # accounts which are not business will be filtered
        assert len(original_records["data"]) > len(output.records)
        assert len(output.records) == 13
        for single_record in output.records:
            assert "id" in single_record.record.data
            assert "account" in single_record.record.data
            assert "business_account_id" in single_record.record.data["account"]
            assert "page_id" in single_record.record.data["account"]

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_account_request().build(),
            _get_response().with_pagination().with_record(_record()).build(),
        )
        next_account_url = get_account_request().with_next_page_token(NEXT_PAGE_TOKEN).build()
        http_mocker.get(
            next_account_url,
            _get_response().with_record(_record()).with_record(_record()).build(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_exception_on_accounts_request(self, http_mocker: HttpMocker) -> None:
        get_account_request().build()
        http_mocker.get(get_account_request().build(), build_response(status_code=HTTPStatus.FORBIDDEN, body={}))

        is_successful, error = get_source(config={}).check_connection(logger=logger, config={})
        assert not is_successful
        assert "Forbidden" in error


class TestIgAccountIdFilter(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_no_ig_account_id_returns_all_accounts(self, http_mocker: HttpMocker) -> None:
        """When ig_account_id is not set, all accounts should be returned."""
        http_mocker.get(
            get_account_request().build(),
            get_multiple_accounts_response(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_ig_account_id_filters_to_matching_account(self, http_mocker: HttpMocker) -> None:
        """When ig_account_id is set, only the matching account should be returned."""
        from .config import BUSINESS_ACCOUNT_ID

        http_mocker.get(
            get_account_request().build(),
            get_multiple_accounts_response(),
        )

        output = self._read(config_=config().with_ig_account_id(BUSINESS_ACCOUNT_ID))
        assert len(output.records) == 1
        assert output.records[0].record.data["account"]["business_account_id"] == BUSINESS_ACCOUNT_ID

    @HttpMocker()
    def test_ig_account_id_filters_to_second_account(self, http_mocker: HttpMocker) -> None:
        """When ig_account_id matches the second account, only that one is returned."""
        http_mocker.get(
            get_account_request().build(),
            get_multiple_accounts_response(),
        )

        output = self._read(config_=config().with_ig_account_id(SECOND_BUSINESS_ACCOUNT_ID))
        assert len(output.records) == 1
        assert output.records[0].record.data["account"]["business_account_id"] == SECOND_BUSINESS_ACCOUNT_ID

    @HttpMocker()
    def test_ig_account_id_no_match_returns_empty(self, http_mocker: HttpMocker) -> None:
        """When ig_account_id doesn't match any account, no records are returned."""
        http_mocker.get(
            get_account_request().build(),
            get_multiple_accounts_response(),
        )

        output = self._read(config_=config().with_ig_account_id("999999999999999"))
        assert len(output.records) == 0
