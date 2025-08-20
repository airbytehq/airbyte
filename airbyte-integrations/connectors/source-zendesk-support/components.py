# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Tuple

import requests

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


class ZendeskSupportExtractorEvents(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ["via_reference_id", "ticket_id", "timestamp"]:
                        event[prop] = record.get(prop)

                    # https://github.com/airbytehq/oncall/issues/1001
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events


class ZendeskSupportAttributeDefinitionsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = []
            for definition in response.json()["definitions"]["conditions_all"]:
                definition["condition"] = "all"
                records.append(definition)
            for definition in response.json()["definitions"]["conditions_any"]:
                definition["condition"] = "any"
                records.append(definition)
        except requests.exceptions.JSONDecodeError:
            records = []
        return records


@dataclass
class ZendeskSupportOAuth2Authenticator(DeclarativeOauth2Authenticator):
    """
    Custom OAuth2 authenticator for Zendesk Support that handles token expiration and refresh.

    This authenticator implements Zendesk's new OAuth refresh token flow to comply with
    their September 30, 2025 deadline for access token expiration support.

    Reference: https://developer.zendesk.com/api-reference/ticketing/oauth/grant_type_tokens/
    """

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Build the request body for token refresh according to Zendesk's OAuth specification.

        Zendesk expects:
        - grant_type: "refresh_token"
        - refresh_token: The refresh token
        - client_id: The OAuth client ID
        - client_secret: The OAuth client secret
        """
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Refresh the access token using Zendesk's /oauth/tokens endpoint.

        Returns:
            Tuple[str, int]: (access_token, expires_in_seconds)

        Raises:
            Exception: If the token refresh fails
        """
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                json=self.get_refresh_request_body(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            response_json = response.json()

            access_token = response_json.get("access_token")
            expires_in = response_json.get("expires_in", 7200)  # Default to 2 hours if not provided

            if not access_token:
                raise Exception("No access_token in refresh response")

            return access_token, expires_in

        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP error while refreshing Zendesk access token: {e}") from e
        except (KeyError, ValueError) as e:
            raise Exception(f"Invalid response format while refreshing Zendesk access token: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error while refreshing Zendesk access token: {e}") from e
