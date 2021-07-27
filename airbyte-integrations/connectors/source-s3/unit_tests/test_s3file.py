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


import pytest
from airbyte_cdk import AirbyteLogger
from source_s3.s3file import S3File

LOGGER = AirbyteLogger()


class TestS3File:
    @pytest.mark.parametrize(  # passing in full provider to emulate real usage (dummy values are unused by func)
        "provider, return_true",
        [
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "aws_secret_access_key": "key", "path_prefix": "dummy"}, True),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": None, "aws_secret_access_key": None, "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "aws_secret_access_key": None, "path_prefix": "dummy"}, False),
            (
                {"storage": "S3", "bucket": "dummy", "aws_access_key_id": None, "aws_secret_access_key": "key", "path_prefix": "dummy"},
                False,
            ),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "aws_secret_access_key": "key", "path_prefix": "dummy"}, False),
        ],
    )
    def test_use_aws_account(self, provider, return_true):
        assert S3File.use_aws_account(provider) is return_true
