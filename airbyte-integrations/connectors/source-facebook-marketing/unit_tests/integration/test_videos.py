#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Dict, List, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.models import AirbyteStateMessage, AirbyteStreamStateSerializer, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ACCESS_TOKEN, ACCOUNT_ID, NOW, ConfigBuilder
from .pagination import NEXT_PAGE_TOKEN, FacebookMarketingPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import error_reduce_amount_of_data_response, get_account_response
from .utils import config, read_output

_STREAM_NAME = "videos"
_CURSOR_FIELD = "updated_time"
_FIELDS = [
    "id",
    "ad_breaks",
    "backdated_time",
    "backdated_time_granularity",
    "content_category",
    "content_tags",
    "created_time",
    "custom_labels",
    "description",
    "embed_html",
    "embeddable",
    "format",
    "icon",
    "is_crosspost_video",
    "is_crossposting_eligible",
    "is_episode",
    "is_instagram_eligible",
    "length",
    "live_status",
    "permalink_url",
    "post_views",
    "premiere_living_room_status",
    "published",
    "scheduled_publish_time",
    "source",
    "title",
    "universal_video_id",
    "updated_time",
    "views",
]


def _get_videos_request(account_id: Optional[str] = ACCOUNT_ID, fields: Optional[List[str]] = None) -> RequestBuilder:
    return (
        RequestBuilder.get_videos_endpoint(access_token=ACCESS_TOKEN, account_id=account_id)
        .with_limit(100)
        .with_fields(fields or _FIELDS)
        .with_summary()
    )


def _get_videos_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=FacebookMarketingPaginationStrategy(request=_get_videos_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    )


def _video_record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False, json_schema: Optional[Dict[str, any]] = None) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
            json_schema=json_schema
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        client_side_account_id = ACCOUNT_ID
        server_side_account_id = ACCOUNT_ID

        http_mocker.get(
            get_account_request(account_id=client_side_account_id).build(),
            get_account_response(account_id=server_side_account_id),
        )
        http_mocker.get(
            _get_videos_request(account_id=server_side_account_id).build(),
            _get_videos_response().with_record(_video_record()).build(),
        )

        output = self._read(config().with_account_ids([client_side_account_id]))
        assert len(output.records) == 1

    @HttpMocker()
    def test_request_fields_from_json_schema_in_configured_catalog(self, http_mocker: HttpMocker) -> None:
        """
        The purpose of this test is to check that the request fields are the same provided in json_request_schema inside configured catalog
        """
        configured_json_schema = find_template(f"{_STREAM_NAME}_reduced_configured_schema_fields", __file__)
        params_fields = [field for field in configured_json_schema["properties"]]
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_videos_request(fields=params_fields).build(),
            _get_videos_response().with_record(_video_record()).build(),
        )

        output = self._read(config(), json_schema=configured_json_schema)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            _get_videos_request().build(),
            _get_videos_response().with_pagination().with_record(_video_record()).build(),
        )
        http_mocker.get(
            _get_videos_request().with_next_page_token(NEXT_PAGE_TOKEN).build(),
            _get_videos_response().with_record(_video_record()).with_record(_video_record()).build(),
        )

        output = self._read(config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_return_records_from_all_accounts(self, http_mocker: HttpMocker) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"

        http_mocker.get(get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_1).build(),
            _get_videos_response().with_record(_video_record()).build(),
        )
        http_mocker.get(get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_2).build(),
            _get_videos_response().with_record(_video_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id_1, account_id_2]))
        assert len(output.records) == 2

    @HttpMocker()
    def test_when_read_then_add_account_id_field(self, http_mocker: HttpMocker) -> None:
        account_id = "123123123"

        http_mocker.get(get_account_request().with_account_id(account_id).build(), get_account_response(account_id=account_id))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id).build(),
            _get_videos_response().with_record(_video_record()).build(),
        )

        output = self._read(config().with_account_ids([account_id]))
        assert output.records[0].record.data["account_id"] == account_id

    @HttpMocker()
    def test_when_read_then_datetime_fields_transformed(self, http_mocker: HttpMocker) -> None:
        created_time_field = "created_time"
        input_datetime_value = "2024-01-01t00:00:00 0000"
        expected_datetime_value = "2024-01-01T00:00:00+0000"

        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            _get_videos_request().with_fields(_FIELDS).with_summary().build(),
            _get_videos_response().with_record(_video_record().with_field(FieldPath(created_time_field), input_datetime_value)).build(),
        )

        output = self._read(config())
        assert output.records[0].record.data[created_time_field] == expected_datetime_value

    @HttpMocker()
    def test_given_status_500_reduce_amount_of_data_when_read_then_limit_reduced(self, http_mocker: HttpMocker) -> None:
        limit = 100

        http_mocker.get(get_account_request().build(), get_account_response())
        http_mocker.get(
            _get_videos_request().with_limit(limit).with_fields(_FIELDS).with_summary().build(),
            error_reduce_amount_of_data_response(),
        )
        http_mocker.get(
            _get_videos_request().with_limit(int(limit / 2)).with_fields(_FIELDS).with_summary().build(),
            _get_videos_response().with_record(_video_record()).build(),
        )

        self._read(config())


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental(TestCase):
    @staticmethod
    def _read(
        config_: ConfigBuilder, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
    ) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker: HttpMocker) -> None:
        min_cursor_value = "2024-01-01T00:00:00+00:00"
        max_cursor_value = "2024-02-01T00:00:00+00:00"
        account_id = "123123123"

        http_mocker.get(get_account_request().with_account_id(account_id).build(), get_account_response(account_id=account_id))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(max_cursor_value))
            .with_record(_video_record().with_cursor(min_cursor_value))
            .build(),
        )

        output = self._read(config().with_account_ids([account_id]))
        cursor_value_from_state_message = AirbyteStreamStateSerializer.dump(output.most_recent_state).get("stream_state").get(account_id, {}).get(_CURSOR_FIELD)
        assert cursor_value_from_state_message == max_cursor_value

    @HttpMocker()
    def test_given_multiple_account_ids_when_read_then_state_produced_by_account_id_and_state_match_latest_record(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        min_cursor_value_account_id_1 = "2024-01-01T00:00:00+00:00"
        max_cursor_value_account_id_1 = "2024-02-01T00:00:00+00:00"
        min_cursor_value_account_id_2 = "2024-03-01T00:00:00+00:00"
        max_cursor_value_account_id_2 = "2024-04-01T00:00:00+00:00"

        http_mocker.get(get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_1).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(max_cursor_value_account_id_1))
            .with_record(_video_record().with_cursor(min_cursor_value_account_id_1))
            .build(),
        )
        http_mocker.get(get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_2).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(max_cursor_value_account_id_2))
            .with_record(_video_record().with_cursor(min_cursor_value_account_id_2))
            .build(),
        )

        output = self._read(config().with_account_ids([account_id_1, account_id_2]))
        cursor_value_from_state_account_1 = AirbyteStreamStateSerializer.dump(output.most_recent_state).get("stream_state").get(account_id_1, {}).get(_CURSOR_FIELD)
        cursor_value_from_state_account_2 = AirbyteStreamStateSerializer.dump(output.most_recent_state).get("stream_state").get(account_id_2, {}).get(_CURSOR_FIELD)
        assert cursor_value_from_state_account_1 == max_cursor_value_account_id_1
        assert cursor_value_from_state_account_2 == max_cursor_value_account_id_2

    @HttpMocker()
    def test_given_state_when_read_then_records_with_cursor_value_less_than_state_filtered(self, http_mocker: HttpMocker) -> None:
        account_id = "123123123"
        cursor_value_1 = "2024-01-01T00:00:00+00:00"
        cursor_value_2 = "2024-01-02T00:00:00+00:00"
        cursor_value_3 = "2024-01-03T00:00:00+00:00"

        http_mocker.get(get_account_request().with_account_id(account_id).build(), get_account_response(account_id=account_id))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(cursor_value_3))
            .with_record(_video_record().with_cursor(cursor_value_2))
            .with_record(_video_record().with_cursor(cursor_value_1))
            .build(),
        )

        output = self._read(
            config().with_account_ids([account_id]),
            state=StateBuilder().with_stream_state(_STREAM_NAME, {account_id: {_CURSOR_FIELD: cursor_value_2}}).build(),
        )
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_state_and_multiple_account_ids_when_read_then_records_with_cursor_value_less_than_state_filtered(
        self, http_mocker: HttpMocker
    ) -> None:
        account_id_1 = "123123123"
        account_id_2 = "321321321"
        cursor_value_1 = "2024-01-01T00:00:00+00:00"
        cursor_value_2 = "2024-01-02T00:00:00+00:00"
        cursor_value_3 = "2024-01-03T00:00:00+00:00"

        http_mocker.get(get_account_request().with_account_id(account_id_1).build(), get_account_response(account_id=account_id_1))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_1).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(cursor_value_3))
            .with_record(_video_record().with_cursor(cursor_value_2))
            .with_record(_video_record().with_cursor(cursor_value_1))
            .build(),
        )
        http_mocker.get(get_account_request().with_account_id(account_id_2).build(), get_account_response(account_id=account_id_2))
        http_mocker.get(
            _get_videos_request().with_account_id(account_id_2).build(),
            _get_videos_response()
            .with_record(_video_record().with_cursor(cursor_value_3))
            .with_record(_video_record().with_cursor(cursor_value_2))
            .with_record(_video_record().with_cursor(cursor_value_1))
            .build(),
        )

        stream_state = {account_id_1: {_CURSOR_FIELD: cursor_value_2}, account_id_2: {_CURSOR_FIELD: cursor_value_2}}
        output = self._read(
            config().with_account_ids([account_id_1, account_id_2]),
            state=StateBuilder().with_stream_state(_STREAM_NAME, stream_state).build(),
        )
        assert len(output.records) == 4
