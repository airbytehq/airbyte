#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from typing import Any, Mapping
from urllib import parse

import pendulum
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .authenticator import OktaOauth2Authenticator

logger = logging.getLogger("airbyte")


def get_token_refresh_endpoint(config: Mapping[str, Any]) -> str:
    return parse.urljoin(get_url_base(config), "/oauth2/v1/token")


def initialize_authenticator(config: Mapping[str, Any]):
    if "token" in config:
        return TokenAuthenticator(config["token"], auth_method="SSWS")

    credentials = config.get("credentials")
    if not credentials:
        raise Exception("Config validation error. `credentials` not specified.")

    auth_type = credentials.get("auth_type")
    if not auth_type:
        raise Exception("Config validation error. `auth_type` not specified.")

    if auth_type == "api_token":
        return TokenAuthenticator(credentials["api_token"], auth_method="SSWS")

    if auth_type == "oauth2.0":
        return OktaOauth2Authenticator(
            token_refresh_endpoint=get_token_refresh_endpoint(config),
            client_secret=credentials["client_secret"],
            client_id=credentials["client_id"],
            refresh_token=credentials["refresh_token"],
        )


def get_url_base(config: Mapping[str, Any]) -> str:
    return config.get("base_url") or f"https://{config['domain']}.okta.com"


def get_api_endpoint(config: Mapping[str, Any]) -> str:
    return parse.urljoin(get_url_base(config), "/api/v1/")


def get_start_date(config: Mapping[str, Any]) -> pendulum.datetime:
    # Set start date to default 7 days prior current date if not in config or set in future.
    # Docs: https://developer.okta.com/docs/reference/api/system-log/#request-parameters
    default_start_date = pendulum.now().subtract(days=7).replace(microsecond=0)

    if "start_date" in config:
        start_date = pendulum.parse(config["start_date"])
    else:
        message = "Set the start date to default 7 days prior current date."
        logger.warning(message)
        return default_start_date

    start_date_in_future = start_date.timestamp() > pendulum.now().timestamp()

    if start_date_in_future:
        message = "The start date cannot be in the future. Set the start date to default 7 days prior current date."
        logger.warning(message)
        return default_start_date

    return start_date.replace(microsecond=0)


def delete_milliseconds(date: str) -> str:
    return pendulum.parse(date).strftime("%Y-%m-%dT%H:%M:%SZ")


def datetime_to_string(date: datetime.datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
