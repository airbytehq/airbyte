#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
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

    def _extract_error_message(self, response: requests.Response) -> str:
        """
        Return a human-readable error message from a Notion API response, for use in connection check.
        """
        error_json = response.json()
        error_code = error_json.get("code", "unknown_error")
        error_message = error_json.get(
            "message", "An unspecified error occurred while connecting to Notion. Please check your credentials and try again."
        )

        if error_code == "unauthorized":
            return "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration."
        if error_code == "restricted_resource":
            return "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration."
        return f"Error: {error_message} (Error code: {error_code})"

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # First confirm that if start_date is set by user, it is valid.
        validation_error = self._validate_start_date(config)
        if validation_error:
            return False, validation_error
        try:
            authenticator = self._get_authenticator(config)
            # Notion doesn't have a dedicated ping endpoint, so we can use the users/me endpoint instead.
            # Endpoint docs: https://developers.notion.com/reference/get-self
            ping_endpoint = "https://api.notion.com/v1/users/me"
            notion_version = {"Notion-Version": "2022-06-28"}
            response = requests.get(ping_endpoint, auth=authenticator, headers=notion_version)

            if response.status_code == 200:
                return True, None
            else:
                error_message = self._extract_error_message(response)
                return False, error_message

        except requests.exceptions.RequestException as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        authenticator = self._get_authenticator(config)
        args = {"authenticator": authenticator, "config": config}
        pages = Pages(**args)
        blocks = Blocks(parent=pages, **args)
        comments = Comments(parent=pages, **args)

        return [Users(**args), Databases(**args), pages, blocks, comments]
