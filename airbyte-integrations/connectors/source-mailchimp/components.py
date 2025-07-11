# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, MutableMapping

import requests

from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


class MailChimpRecordExtractorEmailActivity(DpathExtractor):
    def extract_records(
        self, response: requests.Response
    ) -> Iterable[MutableMapping[str, Any]]:
        records = super().extract_records(response=response)
        yield from (
            {**record, **activity_item}
            for record in records
            for activity_item in record.pop("activity", [])
        )


class MailChimpOAuthDataCenterExtractor(RecordTransformation):
    """
    Custom component to extract data center from OAuth access token.
    This is used during stream processing to dynamically set the data center.
    """
    
    def transform(
        self, 
        record: MutableMapping[str, Any], 
        config: MutableMapping[str, Any],
        stream_state: MutableMapping[str, Any],
        stream_slice: MutableMapping[str, Any]
    ) -> None:
        """
        Extract data center from OAuth access token and add it to config.
        
        Args:
            record: The record being processed (not used in this case)
            config: The connector configuration
            stream_state: The stream state (not used in this case)
            stream_slice: The stream slice (not used in this case)
        """
        credentials = config.get("credentials", {})
        auth_type = credentials.get("auth_type")
        
        if auth_type == "oauth2.0" and not config.get("data_center"):
            # For OAuth, make HTTP request to get data center
            access_token = credentials.get("access_token")
            if not access_token:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=(
                        "Access token is required for OAuth authentication."
                    )
                )
            data_center = self._get_oauth_data_center(access_token)
            config["data_center"] = data_center

    def _get_oauth_data_center(self, access_token: str) -> str:
        """
        Retrieve data center for OAuth credentials by making API request.

        Args:
            access_token: OAuth access token

        Returns:
            Data center string (e.g., 'us1', 'eu1')

        Raises:
            AirbyteTracedException: If token is invalid or request fails
        """
        try:
            headers = {"Authorization": f"OAuth {access_token}"}
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", 
                headers=headers,
                timeout=30
            )

            # Requests to this endpoint return 200 even if token is invalid
            response_data = response.json()
            error = response_data.get("error")

            if error == "invalid_token":
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    internal_message=error,
                    message=(
                        "The access token you provided was invalid. "
                        "Please check your credentials and try again."
                    )
                )

            data_center = response_data.get("dc")
            if not data_center:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=(
                        "Could not retrieve data center from OAuth metadata "
                        "response."
                    )
                )

            return data_center

        except requests.RequestException as e:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                message=(
                    f"Failed to retrieve data center from OAuth metadata: "
                    f"{str(e)}"
                )
            )
        except (ValueError, KeyError) as e:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                message=(
                    f"Invalid response format from OAuth metadata endpoint: "
                    f"{str(e)}"
                )
            )
