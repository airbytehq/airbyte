#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from jsonschema import validate
from source_amazon_ads import SourceAmazonAds


def setup_initial_responses(
    profiles_response=None,
    invoices_response=None,
    invoices_response_with_next_page_token=None
):
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "alala", "expires_in": 10},
    )
    if profiles_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/v2/profiles",
            body=profiles_response,
        )
    if invoices_response:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/invoices?count=100",
            body=invoices_response,
        )
    if invoices_response_with_next_page_token:
        responses.add(
            responses.GET,
            "https://advertising-api.amazon.com/invoices?cursor=abcd",
            body=invoices_response_with_next_page_token,
        )


def setup_invoice_responses(
    all_invoice_data=None
):
    if all_invoice_data:
        for invoice_id, val in all_invoice_data.items():
            responses.add(
                responses.GET,
                "https://advertising-api.amazon.com/invoices/%s" % invoice_id,
                body=val,
            )


def get_all_stream_records(stream):
    records = stream.read_records(SyncMode.full_refresh)
    return [r for r in records]


def get_stream_by_name(streams, stream_name):
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise Exception(f"Expected stream {stream_name} not found")


@pytest.mark.parametrize(
    ("start_date", "expected_count"),
    [
        ("2023-01-27", 3),
        ("2023-01-26", 4),
        ("2023-01-30", 0),
    ],
)
@responses.activate
def test_invoices(config, profiles_response, invoices_response_with_next_page_token,
                  invoices_response, invoice_response, start_date, expected_count):
    # custom start date
    config["start_date"] = start_date

    profiles = json.loads(profiles_response)
    # use only single profile
    profiles_response = json.dumps([profiles[0]])

    setup_initial_responses(profiles_response=profiles_response,
                            invoices_response=invoices_response,
                            invoices_response_with_next_page_token=invoices_response_with_next_page_token)
    source = SourceAmazonAds()
    streams = source.streams(config)
    invoices_stream = get_stream_by_name(streams, "invoices")

    all_invoice_data = {}

    records1 = json.loads(invoices_response).get(
        invoices_stream._invoices_payload, {}).get(invoices_stream._invoice_summaries_field, [])
    records2 = json.loads(invoices_response_with_next_page_token).get(
        invoices_stream._invoices_payload, {}).get(invoices_stream._invoice_summaries_field, [])
    records = records1 + records2
    for record in records:
        all_invoice_data[record["id"]] = invoice_response(record["id"])

    setup_invoice_responses(all_invoice_data=all_invoice_data)
    invoices_records = get_all_stream_records(invoices_stream)

    schema = invoices_stream.get_json_schema()
    current_count = 0
    for record in invoices_records:
        validate(schema=schema, instance=record)
        assert record["invoiceSummary"]["fromDate"] not in invoices_stream._ignore_invoice_statuses

        from_date = pendulum.from_format(record["invoiceSummary"]["fromDate"],
                                         invoices_stream.REPORT_DATE_FORMAT).date()
        if from_date >= invoices_stream._start_date:
            current_count += 1

    assert current_count == expected_count
