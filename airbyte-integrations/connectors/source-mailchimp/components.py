# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, MutableMapping

import dpath
import requests

from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import (
    ConfigTransformation,
)
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.traced_exception import FailureType


class MailChimpRecordExtractorEmailActivity(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        records = super().extract_records(response=response)
        yield from ({**record, **activity_item} for record in records for activity_item in record.pop("activity", []))


class ExtractAndSetDataCenterConfigValue(ConfigTransformation):
    def transform(self, config: MutableMapping[str, Any]) -> None:
        """
        Extract the data center from auth credentials and add it to the config.
        For API key auth, extract from the API key itself.
        For OAuth, make an HTTP request to get the data center.
        """

        # Exit early if the data center is already in the config
        if config.get("data_center"):
            return

        try:
            if config.get("credentials", {}).get("auth_type") == "oauth2.0":
                self._extract_data_center_from_oauth(config)
            else:
                self._extract_data_center_from_apikey(config)
        except AirbyteTracedException:
            # Re-raise AirbyteTracedException as-is
            raise
        except Exception as e:
            # Convert other exceptions to AirbyteTracedException
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                internal_message=f"Failed to extract data center: {str(e)}",
                message=("Unable to extract data center from credentials. " "Please check your configuration and try again."),
            ) from e

    @staticmethod
    def _extract_data_center_from_oauth(config: MutableMapping[str, Any]) -> None:
        """Make a request to oauth2/metadata endpoint to get the data center."""
        access_token = config.get("credentials", {}).get("access_token")

        response = requests.get(
            "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": f"OAuth {access_token}"}, timeout=10
        )
        response.raise_for_status()

        # Mailchimp returns a 200 response with an error key if the token is invalid
        error = response.json().get("error")
        if error == "invalid_token":
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                internal_message=error,
                message=("The access token you provided was invalid. " "Please check your credentials and try again."),
            )

        # Extract data center from the "dc" field
        data_center = response.json().get("dc")
        if data_center:
            dpath.new(config, ["data_center"], data_center)

    @staticmethod
    def _extract_data_center_from_apikey(config: MutableMapping[str, Any]) -> None:
        """Extract the data center directly from the API key."""

        # Backward compatibility - check for API key at top level
        if config.get("apikey"):
            api_key = config["apikey"]
            if api_key and "-" in api_key:
                # API key format: "prefix-datacenter"
                data_center = api_key.split("-")[-1]
                dpath.new(config, ["data_center"], data_center)
                return

        # API key flow - extract data center from API key
        api_key = config.get("credentials", {}).get("apikey")
        if api_key and "-" in api_key:
            # API key format: "prefix-datacenter"
            data_center = api_key.split("-")[-1]
            dpath.new(config, ["data_center"], data_center)
