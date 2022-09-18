#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from enum import Enum

import boto3.session
from botocore import UNSIGNED
from botocore.client import BaseClient, Config


class AuthenticationMethod(Enum):
    ACCESS_KEY_SECRET_ACCESS_KEY = 1
    DEFAULT = 2
    UNSIGNED = 3


def get_authentication_method(provider: dict) -> AuthenticationMethod:
    """
    Return authentication method for this provider.
    :param provider provider configuration from connector configuration.
    :return authentication method.
    """
    if provider.get("aws_access_key_id") and provider.get("aws_secret_access_key"):
        return AuthenticationMethod.ACCESS_KEY_SECRET_ACCESS_KEY
    elif provider.get("use_aws_default_credential_provider_chain"):
        return AuthenticationMethod.DEFAULT
    else:
        return AuthenticationMethod.UNSIGNED


def make_s3_client(provider: dict, session: boto3.session.Session = None, config: Config = None) -> BaseClient:
    """
    Construct boto3 client with specified config and remote endpoint
    :param provider provider configuration from connector configuration.
    :param session User session to create client from. Default boto3 sesion in case of session not specified.
    :param config Client config parameter in case of using creds from .aws/config file.
    :return Boto3 S3 client instance.
    """
    client_kv_args = _get_s3_client_args(provider)
    if session is None:
        return boto3.client("s3", **client_kv_args)
    else:
        return session.client("s3", **client_kv_args)


def _get_s3_client_args(provider: dict) -> dict:
    """
    Returns map of args used for creating s3 boto3 client.
    :param provider provider configuration from connector configuration.
    :return map of s3 client arguments.
    """
    client_kv_args = {}
    authentication_method = get_authentication_method(provider)

    if authentication_method == AuthenticationMethod.ACCESS_KEY_SECRET_ACCESS_KEY:
        client_kv_args["aws_access_key_id"] = provider.get("aws_access_key_id")
        client_kv_args["aws_secret_access_key"] = provider.get("aws_secret_access_key")
        client_kv_args["config"] = Config()
    elif authentication_method == AuthenticationMethod.DEFAULT:
        client_kv_args["config"] = Config()
    elif authentication_method == AuthenticationMethod.UNSIGNED:
        client_kv_args["config"] = Config(signature_version=UNSIGNED)
    else:
        raise Exception("Could not set up boto client since a valid authentication method was not determined.")

    endpoint = provider.get("endpoint")
    if endpoint:
        # endpoint could be None or empty string, set to default Amazon endpoint in
        # this case.
        client_kv_args["endpoint_url"] = endpoint
        client_kv_args["use_ssl"] = provider.get("use_ssl")
        client_kv_args["verify"] = provider.get("verify_ssl_cert")

    return client_kv_args


__all__ = ["make_s3_client"]
