#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import SyncMode
from config import ConfigBuilder
from freezegun import freeze_time
from pagination import HarvestPaginationStrategy
from request_builder import HarvestRequestBuilder
from source_harvest.source import SourceHarvest


def _a_record(stream_name: str, data_path: str, primary_key: str) -> RecordBuilder:
    return create_record_builder(
        find_template(stream_name, __file__),
        records_path=FieldPath(data_path),
        record_id_path=FieldPath(primary_key),
        record_cursor_path=None
    )

def _a_response(stream_name: str, data_path: str) -> HttpResponseBuilder:
    return create_response_builder(
        find_template(stream_name, __file__),
        records_path=FieldPath(data_path),
        pagination_strategy=HarvestPaginationStrategy()
    )

@freeze_time("2024-03-24")
class UnitTest(TestCase):

    def setUp(self) -> None:
        self._config = ConfigBuilder().build()

    def test_streams(self):
        streams = SourceHarvest().streams(self._config)
        assert len(streams) == 32

    @HttpMocker()
    def test_next_page_token(self, http_mocker: HttpMocker):

        catalog = CatalogBuilder().with_stream("invoices", SyncMode.full_refresh).build()

        stream_name = "invoices"
        stream_pk = "id"

        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint("account_id").with_per_page(50).with_updated_since("2021-01-01T00:00:00Z").build(),
            _a_response(stream_name="invoices", data_path="invoices").with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk)).with_pagination().build()
        )

        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint("account_id").with_page(2).with_per_page(50).with_updated_since("2021-01-01T00:00:00Z").build(),
            _a_response(stream_name="invoices", data_path="invoices").with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk)).build()
        )

        output = read(SourceHarvest(), config=self._config, catalog=catalog)
        len(output.records) == 2

    @HttpMocker()
    def test_child_stream_partitions(self, http_mocker: HttpMocker):

        stream_name = "invoices"
        stream_pk = "id"

        http_mocker.get(
            HarvestRequestBuilder.invoices_endpoint("account_id").with_any_query_params().build(),
            [_a_response(stream_name=stream_name, data_path=stream_name).with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk).with_field(FieldPath(stream_pk), 1)).with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk).with_field(FieldPath(stream_pk), 2)).build()]
        )

        output_1 = read(SourceHarvest(), config=self._config, catalog=CatalogBuilder().with_stream("invoices", SyncMode.full_refresh).build())

        invoice_1_id = json.loads(output_1.records[0].json())["record"]["data"]["id"]
        invoice_2_id = json.loads(output_1.records[1].json())["record"]["data"]["id"]

        stream_name = "invoice_messages"

        http_mocker.get(
            HarvestRequestBuilder.invoice_messages_endpoint("account_id", invoice_1_id).with_any_query_params().build(),
            _a_response(stream_name=stream_name, data_path=stream_name).with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk)).build()
        )

        http_mocker.get(
            HarvestRequestBuilder.invoice_messages_endpoint("account_id", invoice_2_id).with_any_query_params().build(),
            _a_response(stream_name=stream_name, data_path=stream_name).with_record(_a_record(stream_name=stream_name, data_path=stream_name, primary_key=stream_pk)).build()
        )

        read(SourceHarvest(), config=self._config, catalog=CatalogBuilder().with_stream("invoice_messages", SyncMode.full_refresh).build())
        # Http Matcher test

    @HttpMocker()
    def test_report_based_stream(self, http_mocker: HttpMocker):

        stream_name = "expenses_clients"
        stream_pk = "client_id"
        data_path = "results"

        http_mocker.get(
            HarvestRequestBuilder.expenses_clients_endpoint("account_id").with_any_query_params().build(),
            _a_response(stream_name=stream_name, data_path=data_path).with_record(_a_record(stream_name, data_path, stream_pk)).build()
        )

        output = read(SourceHarvest(), config=self._config, catalog=CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build())

        len(output.records) == 1

    @HttpMocker()
    def test_report_based_stream_slices(self, http_mocker: HttpMocker):

        stream_name = "expenses_clients"
        stream_pk = "client_id"
        data_path = "results"

        replication_start_date = "2021-01-01T00:00:00Z"
        replication_start_datetime = datetime.strptime(replication_start_date, "%Y-%m-%dT%H:%M:%SZ")

        config = ConfigBuilder().with_replication_start_date(replication_start_datetime).build()

        while replication_start_datetime < datetime.now():

            # Adds 364 days to create a 365-day-long duration, which is max for Harvest API
            if replication_start_datetime + timedelta(days=364) < datetime.now():
                end_datetime = replication_start_datetime + timedelta(days=364)
            else:
                end_datetime = datetime.now()

            end_datetime = replication_start_datetime + timedelta(days=364) if replication_start_datetime + timedelta(days=364) < datetime.now() else datetime.now()

            http_mocker.get(
                HarvestRequestBuilder.expenses_clients_endpoint("account_id").with_per_page(50).with_from(replication_start_datetime).with_to(end_datetime).build(),
                _a_response(stream_name=stream_name, data_path=data_path).with_record(_a_record(stream_name, data_path, stream_pk)).build()
            )

            replication_start_datetime = end_datetime + timedelta(days=1)

        output = read(SourceHarvest(), config=config, catalog=CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build())

        assert len(output.records) == 4