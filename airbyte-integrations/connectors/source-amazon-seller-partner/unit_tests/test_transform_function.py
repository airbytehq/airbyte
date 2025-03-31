#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from integration.utils import config, get_stream_by_name
from source_amazon_seller_partner.components import (
    FlatFileSettlementV2ReportsTypeTransformer,
    LedgerDetailedViewReportsTypeTransformer,
    MerchantListingsFypReportTypeTransformer,
    MerchantReportsTypeTransformer,
    SellerFeedbackReportsTypeTransformer,
)


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
    for marketplace_id, date_format in SellerFeedbackReportsTypeTransformer.MARKETPLACE_DATE_FORMAT_MAP.items():
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
    transformer = SellerFeedbackReportsTypeTransformer(config={"marketplace_id": marketplace_id})
    schema = get_stream_by_name("GET_SELLER_FEEDBACK_DATA", config().build()).get_json_schema()
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
def test_transform_merchant_reports(input_data, expected_data):
    transformer = MerchantReportsTypeTransformer()
    schema = get_stream_by_name("GET_MERCHANT_LISTINGS_ALL_DATA", config().build()).get_json_schema()
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
def test_transform_merchant_fyp_reports(input_data, expected_data):
    transformer = MerchantListingsFypReportTypeTransformer()
    schema = get_stream_by_name("GET_MERCHANTS_LISTINGS_FYP_REPORT", config().build()).get_json_schema()
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
def test_transform_ledger_reports(input_data, expected_data):
    transformer = LedgerDetailedViewReportsTypeTransformer()
    schema = get_stream_by_name("GET_LEDGER_DETAIL_VIEW_DATA", config().build()).get_json_schema()
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
    transformer = FlatFileSettlementV2ReportsTypeTransformer()
    schema = get_stream_by_name("GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE", config().build()).get_json_schema()
    transformer.transform(input_data, schema)
    assert input_data == expected_data
