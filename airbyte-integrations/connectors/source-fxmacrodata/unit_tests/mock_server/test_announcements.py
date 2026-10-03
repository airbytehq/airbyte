# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional
from unittest import TestCase
from unittest.mock import patch

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import FXMacroDataRequestBuilder, json_response, paged_response


_STREAM_NAME = "announcements"
_START_DATE = "2026-01-01"


def _row(date: str, val: Optional[float]) -> Dict[str, Any]:
    return {"announcement_id": f"usd_policy_rate_{date}", "date": date, "val": val, "announcement_datetime": 1767225600}


def _read(
    config: Dict[str, Any], state: Optional[List[AirbyteStateMessage]] = None, sync_mode: SyncMode = SyncMode.incremental
) -> EntrypointOutput:
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


class TestAnnouncementsStream(TestCase):
    @HttpMocker()
    def test_records_carry_currency_and_indicator(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date(_START_DATE).build(),
            paged_response([_row("2026-09-17", 4.25)]),
        )

        output = _read(ConfigBuilder().with_start_date(_START_DATE).build())

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["currency"] == "USD"
        assert record["indicator"] == "policy_rate"
        assert record["date"] == "2026-09-17"
        assert record["val"] == 4.25

    @HttpMocker()
    def test_null_values_are_kept(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date(_START_DATE).build(),
            paged_response([_row("2026-09-17", None), _row("2026-07-30", 4.5)]),
        )

        output = _read(ConfigBuilder().with_start_date(_START_DATE).build())

        # The record is still emitted. The Airbyte protocol serializer leaves null
        # fields out of the message, so destinations load `val` as NULL, never 0.
        assert [record.record.data["date"] for record in output.records] == ["2026-09-17", "2026-07-30"]
        assert [record.record.data.get("val") for record in output.records] == [None, 4.5]

    @HttpMocker()
    def test_pagination_follows_next_offset(self, http_mocker: HttpMocker) -> None:
        builder = FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date(_START_DATE)
        http_mocker.get(builder.build(), paged_response([_row("2026-09-17", 4.25)], next_offset=100))
        http_mocker.get(builder.with_offset(100).build(), paged_response([_row("2026-07-30", 4.5)]))

        output = _read(ConfigBuilder().with_start_date(_START_DATE).build())

        assert [record.record.data["date"] for record in output.records] == ["2026-09-17", "2026-07-30"]

    @HttpMocker()
    def test_one_partition_per_currency_and_indicator(self, http_mocker: HttpMocker) -> None:
        config = (
            ConfigBuilder()
            .with_api_key("test-api-key")
            .with_currencies("USD", "EUR")
            .with_indicators("inflation")
            .with_start_date(_START_DATE)
        )
        for currency in ("USD", "EUR"):
            http_mocker.get(
                FXMacroDataRequestBuilder.announcements_endpoint(currency, "inflation")
                .with_start_date(_START_DATE)
                .with_header("X-API-Key", "test-api-key")
                .build(),
                paged_response([_row("2026-08-31", 2.1)]),
            )

        output = _read(config.build())

        assert sorted(record.record.data["currency"] for record in output.records) == ["EUR", "USD"]

    @HttpMocker()
    def test_indicator_not_served_for_currency_is_skipped(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_indicators("m3_money_supply", "policy_rate").with_start_date(_START_DATE).build()
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "m3_money_supply").with_start_date(_START_DATE).build(),
            json_response({"detail": "Unsupported currency (USD) or indicator (m3_money_supply)."}, status_code=404),
        )
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date(_START_DATE).build(),
            paged_response([_row("2026-09-17", 4.25)]),
        )

        output = _read(config)

        assert output.errors == []
        assert [record.record.data["indicator"] for record in output.records] == ["policy_rate"]

    @HttpMocker()
    def test_missing_key_for_non_usd_currency_is_a_config_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("EUR", "inflation").with_start_date(_START_DATE).build(),
            json_response({"detail": "This endpoint requires an Individual or Enterprise API key."}, status_code=401),
        )
        config = ConfigBuilder().with_currencies("EUR").with_indicators("inflation").with_start_date(_START_DATE).build()

        output = _read(config, sync_mode=SyncMode.full_refresh)

        assert not output.records
        assert any("requires an Individual or Enterprise API key" in error.trace.error.message for error in output.errors)

    @HttpMocker()
    def test_state_is_saved_per_partition_and_used_as_start_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date("2026-07-30").build(),
            paged_response([_row("2026-09-17", 4.25), _row("2026-07-30", 4.5)]),
        )
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {"states": [{"partition": {"currency": "USD", "indicator": "policy_rate"}, "cursor": {"date": "2026-07-30"}}]},
            )
            .build()
        )

        output = _read(ConfigBuilder().with_start_date(_START_DATE).build(), state=state)

        assert len(output.records) == 2
        final_state = output.most_recent_state.stream_state.__dict__
        cursor = next(s["cursor"] for s in final_state["states"] if s["partition"] == {"currency": "USD", "indicator": "policy_rate"})
        assert cursor == {"date": "2026-09-17"}

    @HttpMocker()
    def test_server_error_is_retried(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date(_START_DATE).build(),
            [json_response({"detail": "unavailable"}, status_code=503), paged_response([_row("2026-09-17", 4.25)])],
        )

        with patch("time.sleep"):
            output = _read(ConfigBuilder().with_start_date(_START_DATE).build())

        assert len(output.records) == 1


class TestCheckAndAuth(TestCase):
    @HttpMocker()
    def test_check_succeeds_without_a_key_for_usd(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.announcements_endpoint("USD", "policy_rate").with_start_date("1900-01-01").build(),
            paged_response([_row("2026-09-17", 4.25)]),
        )
        config = ConfigBuilder().build()

        status = get_source(config=config).check(logger=None, config=config)

        assert status.status == Status.SUCCEEDED

    def test_api_key_header_is_only_sent_when_configured(self) -> None:
        def headers_for(config: Dict[str, Any]) -> Dict[str, Any]:
            source = get_source(config=config)
            stream = next(stream for stream in source.streams(config=config) if stream.name == _STREAM_NAME)
            partition = next(iter(stream.generate_partitions()))
            return dict(partition._retriever.requester.get_request_headers())

        assert "X-API-Key" not in headers_for(ConfigBuilder().build())
        assert headers_for(ConfigBuilder().with_api_key("test-api-key").build())["X-API-Key"] == "test-api-key"
