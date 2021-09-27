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

import boto3.session
from botocore.client import Config

from .source import SourceFilesAbstract


def make_s3_resource(provider: dict, session: boto3.session.Session, config: Config = None) -> object:
    """
    Construct boto3 resource with specified config and remote endpoint
    :param provider provider configuration from connector configuration.
    :param session User session to create client from.
    :param config Client config parameter in case of using creds from .aws/config file.
    :return Boto3 S3 resource instance.
    """
    client_kv_args = _get_s3_client_args(provider, config)
    return session.resource("s3", **client_kv_args)


def make_s3_client(provider: dict, session: boto3.session.Session = None, config: Config = None) -> object:
    """
    Construct boto3 client with specified config and remote endpoint
    :param provider provider configuration from connector configuration.
    :param session User session to create client from. Default boto3 sesion in case of session not specified.
    :param config Client config parameter in case of using creds from .aws/config file.
    :return Boto3 S3 client instance.
    """
    client_kv_args = _get_s3_client_args(provider, config)
    if session is None:
        return boto3.client("s3", **client_kv_args)
    else:
        return session.client("s3", **client_kv_args)


def _get_s3_client_args(provider: dict, config: Config) -> dict:
    """
    Returns map of args used for creating s3 boto3 client.
    :param provider provider configuration from connector configuration.
    :param config Client config parameter in case of using creds from .aws/config file.
    :return map of s3 client arguments.
    """
    client_kv_args = {"config": config}
    endpoint = provider.get("endpoint")
    if endpoint:
        # endpoint could be None or empty string, set to default Amazon endpoint in
        # this case.
        client_kv_args["endpoint_url"] = endpoint
        client_kv_args["use_ssl"] = provider.get("use_ssl")
        client_kv_args["verify"] = provider.get("verify_ssl_cert")

    return client_kv_args


__all__ = ["SourceFilesAbstract", "make_s3_client", "make_s3_resource"]
