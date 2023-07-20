#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from boto3 import session as boto3session
from botocore.client import BaseClient, Config
from botocore import UNSIGNED

def make_s3_client(provider: dict) -> BaseClient:
    """
    Construct boto3 client with specified config and remote endpoint
    :param provider provider configuration from connector configuration.
    :param session User session to create client from. Default boto3 sesion in case of session not specified.
    :param config Client config parameter in case of using creds from .aws/config file.
    :return Boto3 S3 client instance.
    """
    aws_access_key_id = provider.get("aws_access_key_id")
    aws_secret_access_key = provider.get("aws_secret_access_key")
    if aws_access_key_id and aws_secret_access_key:
        session = boto3session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
    else:
        session = boto3session.Session()
    config = None
    # If we don't have credentials, we use unsigned requests. This is necessary for accessing public buckets.
    if session.get_credentials() is None:
        config = Config(signature_version=UNSIGNED)
    client_kv_args = _get_s3_client_args(provider, config)
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
        client_kv_args["use_ssl"] = provider.get("use_ssl", True)
        client_kv_args["verify"] = provider.get("verify_ssl_cert", True)
        client_kv_args["config"] = Config(s3={"addressing_style": provider.get("addressing_style", "auto")})

    return client_kv_args


__all__ = ["make_s3_client"]
