#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import time

import pytest
import requests
from airbyte_cdk.sources.streams.http.auth import NoAuth
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
        marketplace_ids=["id"],
        authenticator=NoAuth(),
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
    response = requests.Response()
    response.status_code = 429
    mocker.patch.object(requests.Session, "send", return_value=response)
    mocker.patch.object(time, "sleep", return_value=None)

    with pytest.raises(DefaultBackoffException):
        reports_stream._send_request(request=requests.PreparedRequest())

    assert "Backing off _send_request(...) for 5.0s" in caplog.text
    assert "Backing off _send_request(...) for 10.0s" in caplog.text
    assert "Backing off _send_request(...) for 20.0s" in caplog.text
    assert "Backing off _send_request(...) for 40.0s" in caplog.text
    assert "Giving up _send_request(...) after 5 tries" in caplog.text
