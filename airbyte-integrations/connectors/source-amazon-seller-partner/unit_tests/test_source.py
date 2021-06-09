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

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_amazon_seller_partner.source import SourceAmazonSellerPartner


def test_source_wrong_credentials():
    source = SourceAmazonSellerPartner()
    status = source.check(
        logger=AirbyteLogger(),
        config={
            "start_date": "2021-05-27",
            "refresh_token": "ABC",
            "lwa_app_id": "lwa_app_id",
            "lwa_client_secret": "lwa_client_secret",
            "aws_access_key": "aws_access_key",
            "aws_secret_key": "aws_secret_key",
            "role_arn": "role_arn",
            "marketplace": "USA",
        },
    )
    assert status == AirbyteConnectionStatus(
        status=Status.FAILED, message="An exception occurred: ('invalid_client', 'Client authentication failed', 401)"
    )
