#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from itertools import islice
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from pendulum.parsing.exceptions import ParserError

from .streams import Blocks, Comments, Databases, Pages, Users


class SourceNotion(AbstractSource):
    def _get_authenticator(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        credentials = config.get("credentials", {})
        auth_type = credentials.get("auth_type")
        token = credentials.get("access_token") if auth_type == "OAuth2.0" else credentials.get("token")

        if credentials and token:
            return TokenAuthenticator(token)

        # The original implementation did not support OAuth, and therefore had no "credentials" key.
        # We can maintain backwards compatibility for OG connections by checking for the deprecated "access_token" key, just in case.
        if config.get("access_token"):
            return TokenAuthenticator(config["access_token"])

    def _validate_start_date(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")

        if start_date:
            pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")
            if not pattern.match(start_date):  # Compare against the pattern descriptor.
                return "Please check the format of the start date against the pattern descriptor."

            try:  # Handle invalid dates.
                parsed_start_date = pendulum.parse(start_date)
            except ParserError:
                return "The provided start date is not a valid date. Please check the format and try again."

            if parsed_start_date > pendulum.now("UTC"):  # Handle future start date.
                return "The start date cannot be greater than the current date."

        return None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # First confirm that if start_date is set by user, it is valid.
        validation_error = self._validate_start_date(config)
        if validation_error:
            return False, validation_error
        try:
            authenticator = self._get_authenticator(config)
            stream = Pages(authenticator=authenticator, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(islice(records, 5))  # Read the first 5 records to ensure that the connection is valid.
            return True, None
        except requests.exceptions.RequestException as e:
            # The most likely user error will be incorrectly configured credentials. We can provide a specific error message for those cases. Otherwise, the stock Notion API message should suffice.
            error_code = e.response.json().get("code")
            if error_code == "unauthorized":
                return (
                    False,
                    "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration.",
                )
            if error_code == "restricted_resource":
                return (
                    False,
                    "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration.",
                )
            return (
                False,
                f"{e.response.json().get('message', 'An unexpected error occured while connecting to Notion. Please check your credentials and try again.')}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        authenticator = self._get_authenticator(config)
        args = {"authenticator": authenticator, "config": config}
        pages = Pages(**args)
        blocks = Blocks(parent=pages, **args)
        comments = Comments(parent=pages, **args)

        return [Users(**args), Databases(**args), pages, blocks, comments]
