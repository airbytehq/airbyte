#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from source_amazon_seller_partner.auth import AWSSignature
from source_amazon_seller_partner.streams import MerchantListingsReports


@pytest.fixture
def reports_stream():
    aws_signature = AWSSignature(
        service="execute-api",
        aws_access_key_id="AccessKeyId",
        aws_secret_access_key="SecretAccessKey",
        aws_session_token="SessionToken",
        region="US",
    )
    stream = MerchantListingsReports(
        url_base="https://test.url",
        aws_signature=aws_signature,
        replication_start_date="2017-01-25T00:00:00Z",
        replication_end_date="2017-02-25T00:00:00Z",
        marketplace_id="id",
        authenticator=None,
        period_in_days=0,
        report_options=None,
        max_wait_seconds=500,
    )
    return stream


def test_reports_stream_should_retry(mocker, reports_stream):
    response = requests.Response()
    response.status_code = 429
    mocker.patch.object(requests.Session, "send", return_value=response)
    should_retry = reports_stream.should_retry(response=response)

    assert should_retry is True


def test_reports_stream_send_request(mocker, reports_stream):
    response = requests.Response()
    response.status_code = 200
    mocker.patch.object(requests.Session, "send", return_value=response)

    assert response == reports_stream._send_request(request=requests.PreparedRequest())


def test_reports_stream_send_request_backoff_exception(mocker, caplog, reports_stream):
    mocker.patch("time.sleep", lambda x: None)
    response = requests.Response()
    response.status_code = 429
    mocker.patch.object(requests.Session, "send", return_value=response)

    with pytest.raises(DefaultBackoffException):
        reports_stream._send_request(request=requests.PreparedRequest())

    assert "Backing off _send_request(...) for 5.0s" in caplog.text
    assert "Backing off _send_request(...) for 10.0s" in caplog.text
    assert "Backing off _send_request(...) for 20.0s" in caplog.text
    assert "Backing off _send_request(...) for 40.0s" in caplog.text
    assert "Giving up _send_request(...) after 5 tries" in caplog.text
