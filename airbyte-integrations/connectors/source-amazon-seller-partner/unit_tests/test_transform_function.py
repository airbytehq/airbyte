#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_amazon_seller_partner.streams import (
    FlatFileSettlementV2Reports,
    LedgerDetailedViewReports,
    MerchantListingsFypReport,
    MerchantListingsReports,
    SellerFeedbackReports,
)


def reports_stream(marketplace_id):
    stream = SellerFeedbackReports(
        stream_name="SELLER_FEEDBACK_REPORTS",
        url_base="https://test.url",
        replication_start_date="2010-01-25T00:00:00Z",
        replication_end_date="2017-02-25T00:00:00Z",
        marketplace_id=marketplace_id,
        authenticator=None,
        period_in_days=0,
        report_options=None,
    )
    return stream


INPUT_DATES = {
    "YYYY-MM-DD": ["2017-01-13", "2017-12-12", "2017-12-17", "2011-12-13"],
    "D.M.YY": ["13.1.17", "12.12.17", "17.12.17", "13.12.11"],
    "YY/M/D": ["17/1/13", "17/12/12", "17/12/17", "11/12/13"],
    "D/M/YY": ["13/1/17", "12/12/17", "17/12/17", "13/12/11"],
    "M/D/YY": ["1/13/17", "12/12/17", "12/17/17", "12/13/11"],
}
EXPECTED_DATES = ["2017-01-13", "2017-12-12", "2017-12-17", "2011-12-13"]


def parametrize_seller_feedback():
    result = []
    for marketplace_id, date_format in SellerFeedbackReports.MARKETPLACE_DATE_FORMAT_MAP.items():
        for index, input_date in enumerate(INPUT_DATES.get(date_format)):
            expected_date = EXPECTED_DATES[index]
            result.append(
                (
                    marketplace_id,
                    {"date": input_date, "rating": 1, "comments": "c", "response": "r", "order_id": "1", "rater_email": "e"},
                    {"date": expected_date, "rating": 1, "comments": "c", "response": "r", "order_id": "1", "rater_email": "e"},
                )
            )

    return result


@pytest.mark.parametrize("marketplace_id,input_data,expected_data", parametrize_seller_feedback())
def test_transform_seller_feedback(marketplace_id, input_data, expected_data):
    stream = reports_stream(marketplace_id)
    transformer = stream.transformer
    schema = stream.get_json_schema()
    transformer.transform(input_data, schema)

    assert input_data == expected_data


@pytest.mark.parametrize(
    ("input_data", "expected_data"),
    (
        (
            {"item-name": "GiftBox", "open-date": "2022-07-11 01:34:18 PDT", "dataEndTime": "2022-07-31"},
            {"item-name": "GiftBox", "open-date": "2022-07-11T01:34:18-07:00", "dataEndTime": "2022-07-31"},
        ),
        (
            {"item-name": "GiftBox", "open-date": "", "dataEndTime": "2022-07-31"},
            {"item-name": "GiftBox", "open-date": "", "dataEndTime": "2022-07-31"},
        ),
    ),
)
def test_transform_merchant_reports(report_init_kwargs, input_data, expected_data):
    stream = MerchantListingsReports(**report_init_kwargs)
    transformer = stream.transformer
    schema = stream.get_json_schema()
    transformer.transform(input_data, schema)
    assert input_data == expected_data


@pytest.mark.parametrize(
    ("input_data", "expected_data"),
    (
        (
            {"Product name": "GiftBox", "Condition": "11", "Status Change Date": "Jul 29, 2022", "dataEndTime": "2022-07-31"},
            {"Product name": "GiftBox", "Condition": "11", "Status Change Date": "2022-07-29", "dataEndTime": "2022-07-31"},
        ),
        (
            {"Product name": "GiftBox", "Condition": "11", "Status Change Date": "", "dataEndTime": "2022-07-31"},
            {"Product name": "GiftBox", "Condition": "11", "Status Change Date": "", "dataEndTime": "2022-07-31"},
        ),
    ),
)
def test_transform_merchant_fyp_reports(report_init_kwargs, input_data, expected_data):
    stream = MerchantListingsFypReport(**report_init_kwargs)
    transformer = stream.transformer
    schema = stream.get_json_schema()
    transformer.transform(input_data, schema)
    assert input_data == expected_data


@pytest.mark.parametrize(
    ("input_data", "expected_data"),
    (
        ({"Date": "07/29/2022", "dataEndTime": "2022-07-31"}, {"Date": "2022-07-29", "dataEndTime": "2022-07-31"}),
        ({"Date": "7/29/2022", "dataEndTime": "2022-07-31"}, {"Date": "2022-07-29", "dataEndTime": "2022-07-31"}),
        ({"Date": "07/2022", "dataEndTime": "2022-07-31"}, {"Date": "2022-07-01", "dataEndTime": "2022-07-31"}),
        ({"Date": "7/2022", "dataEndTime": "2022-07-31"}, {"Date": "2022-07-01", "dataEndTime": "2022-07-31"}),
        ({"Date": "", "dataEndTime": "2022-07-31"}, {"Date": "", "dataEndTime": "2022-07-31"}),
    ),
)
def test_transform_ledger_reports(report_init_kwargs, input_data, expected_data):
    stream = LedgerDetailedViewReports(**report_init_kwargs)
    transformer = stream.transformer
    schema = stream.get_json_schema()
    transformer.transform(input_data, schema)
    assert input_data == expected_data


@pytest.mark.parametrize(
    ("input_data", "expected_data"),
    (
        (
            {"posted-date": "2023-11-09T18:44:35+00:00", "dataEndTime": "2022-07-31"},
            {"posted-date": "2023-11-09T18:44:35+00:00", "dataEndTime": "2022-07-31"},
        ),
        ({"posted-date": "", "dataEndTime": "2022-07-31"}, {"posted-date": None, "dataEndTime": "2022-07-31"}),
    ),
)
def test_transform_settlement_reports(report_init_kwargs, input_data, expected_data):
    stream = FlatFileSettlementV2Reports(**report_init_kwargs)
    transformer = stream.transformer
    schema = stream.get_json_schema()
    transformer.transform(input_data, schema)
    assert input_data == expected_data
