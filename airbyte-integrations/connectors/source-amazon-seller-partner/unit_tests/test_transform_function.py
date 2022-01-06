#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_amazon_seller_partner.auth import AWSSignature
from source_amazon_seller_partner.streams import SellerFeedbackReports


def reports_stream(marketplace_id):
    aws_signature = AWSSignature(
        service="execute-api",
        aws_access_key_id="AccessKeyId",
        aws_secret_access_key="SecretAccessKey",
        aws_session_token="SessionToken",
        region="Mars",
    )
    stream = SellerFeedbackReports(
        url_base="https://test.url",
        aws_signature=aws_signature,
        replication_start_date="2010-01-25T00:00:00Z",
        marketplace_id=marketplace_id,
        authenticator=NoAuth(),
        period_in_days=0,
        report_options=None,
        max_wait_seconds=0,
    )
    return stream


INPUT_DATES = {
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
                    {"Date": input_date, "Rating": 1, "Comments": "c", "Response": "r", "Order ID": "1", "Rater Email": "e"},
                    {"Date": expected_date, "Rating": 1, "Comments": "c", "Response": "r", "Order ID": "1", "Rater Email": "e"},
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
