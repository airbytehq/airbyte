#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
import re
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from pendulum.parsing.exceptions import ParserError
from requests.auth import AuthBase

from .streams import (
    Automations,
    Campaigns,
    EmailActivity,
    InterestCategories,
    Interests,
    ListMembers,
    Lists,
    Reports,
    SegmentMembers,
    Segments,
    Tags,
    Unsubscribes,
)


class MailChimpAuthenticator:
    @staticmethod
    def get_oauth_data_center(access_token: str) -> str:
        """
        Every Mailchimp API request must be sent to a specific data center.
        The data center is already embedded in API keys, but not OAuth access tokens.
        This method retrieves the data center for OAuth credentials.
        """
        try:
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)}
            )

            # Requests to this endpoint will return a 200 status code even if the access token is invalid.
            error = response.json().get("error")
            if error == "invalid_token":
                raise ValueError("The access token you provided was invalid. Please check your credentials and try again.")
            return response.json()["dc"]

        # Handle any other exceptions that may occur.
        except Exception as e:
            raise Exception(f"An error occured while retrieving the data center for your account. \n {repr(e)}")

    def get_auth(self, config: Mapping[str, Any]) -> AuthBase:
        authorization = config.get("credentials", {})
        auth_type = authorization.get("auth_type")
        if auth_type == "apikey" or not authorization:
            # API keys have the format <key>-<data_center>.
            # See https://mailchimp.com/developer/marketing/docs/fundamentals/#api-structure
            apikey = authorization.get("apikey") or config.get("apikey")
            if not apikey:
                raise Exception("Please provide a valid API key for authentication.")
            auth_string = f"anystring:{apikey}".encode("utf8")
            b64_encoded = base64.b64encode(auth_string).decode("utf8")
            auth = TokenAuthenticator(token=b64_encoded, auth_method="Basic")
            auth.data_center = apikey.split("-").pop()

        elif auth_type == "oauth2.0":
            access_token = authorization["access_token"]
            auth = TokenAuthenticator(token=access_token, auth_method="Bearer")
            auth.data_center = self.get_oauth_data_center(access_token)

        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return auth


class SourceMailchimp(AbstractSource):
    def _validate_start_date(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")

        if start_date:
            pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")
            if not pattern.match(start_date):  # Compare against the pattern descriptor.
                return "Please check the format of the start date against the pattern descriptor."

            try:  # Handle invalid dates.
                parsed_start_date = pendulum.parse(start_date)
            except ParserError:
                return "The provided start date is not a valid date. Please check the date you input and try again."

            if parsed_start_date > pendulum.now("UTC"):  # Handle future start date.
                return "The start date cannot be greater than the current date."

        return None

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # First, check for a valid start date if it is provided
        start_date_validation_error = self._validate_start_date(config)
        if start_date_validation_error:
            return False, start_date_validation_error

        try:
            authenticator = MailChimpAuthenticator().get_auth(config)
            response = requests.get(
                f"https://{authenticator.data_center}.api.mailchimp.com/3.0/ping", headers=authenticator.get_auth_header()
            )

            # A successful response will return a simple JSON object with a single key: health_status.
            # Otherwise, errors are returned as a JSON object with keys:
            # {type, title, status, detail, instance}

            if not response.json().get("health_status"):
                error_title = response.json().get("title", "Unknown Error")
                error_details = response.json().get("details", "An unknown error occurred. Please verify your credentials and try again.")
                return False, f"Encountered an error while connecting to Mailchimp. Type: {error_title}. Details: {error_details}"
            return True, None

        # Handle any other exceptions that may occur.
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = MailChimpAuthenticator().get_auth(config)
        campaign_id = config.get("campaign_id")
        start_date = config.get("start_date")

        lists = Lists(authenticator=authenticator, start_date=start_date)
        interest_categories = InterestCategories(authenticator=authenticator, parent=lists)

        return [
            Automations(authenticator=authenticator, start_date=start_date),
            Campaigns(authenticator=authenticator, start_date=start_date),
            EmailActivity(authenticator=authenticator, start_date=start_date, campaign_id=campaign_id),
            interest_categories,
            Interests(authenticator=authenticator, parent=interest_categories),
            lists,
            ListMembers(authenticator=authenticator, start_date=start_date),
            Reports(authenticator=authenticator, start_date=start_date),
            SegmentMembers(authenticator=authenticator, start_date=start_date),
            Segments(authenticator=authenticator, start_date=start_date),
            Tags(authenticator=authenticator, parent=lists),
            Unsubscribes(authenticator=authenticator, start_date=start_date, campaign_id=campaign_id),
        ]
