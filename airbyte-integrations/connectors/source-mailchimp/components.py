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
    def extract_records(
        self, response: requests.Response
    ) -> Iterable[MutableMapping[str, Any]]:
        records = super().extract_records(response=response)
        yield from (
            {**record, **activity_item}
            for record in records
            for activity_item in record.pop("activity", [])
        )


class MailChimpOAuthDataCenterExtractor(ConfigTransformation):
    def transform(self, config: MutableMapping[str, Any]) -> None:
        """
        Extract the data center from OAuth tokens and add it to the config.
        For API key auth, extract from the API key itself.
        For OAuth auth, make an HTTP request to get the data center.
        """
        # Check if this is OAuth authentication
        print(f"Config: {config}")
        if config.get("credentials", {}).get("auth_type") == "oauth2.0":
            
            access_token = config.get("credentials", {}).get("access_token")
            # OAuth flow - extract data center from access token
            
            # Make HTTP request to get OAuth metadata
            try:
                response = requests.get(
                    "https://login.mailchimp.com/oauth2/metadata",
                    headers={"Authorization": f"OAuth {access_token}"},
                    timeout=10
                )
                response.raise_for_status()
                
                # Check for invalid token error
                error = response.json().get("error")
                if error == "invalid_token":
                    raise AirbyteTracedException(
                        failure_type=FailureType.config_error,
                        internal_message=error,
                        message=(
                            "The access token you provided was invalid. "
                            "Please check your credentials and try again."
                        ),
                    )
                
                # Extract data center from the "dc" field
                data_center = response.json().get("dc")
                if data_center:
                    # Only add to user config fields, avoid framework-injected fields
                    self._safe_add_field(config, "data_center", data_center)
                    
            except Exception as e:
                # If we can't get the data center, log the error but don't fail
                # The connector will handle this gracefully
                print(
                    f"Warning: Could not extract data center from OAuth token: {e}"
                )
                
        elif config.get("credentials", {}).get("auth_type") == "apikey":
            # API key flow - extract data center from API key
            api_key = config.get("credentials", {}).get("apikey")
            if api_key and "-" in api_key:
                # API key format: "prefix-datacenter"
                data_center = api_key.split("-")[-1]
                self._safe_add_field(config, "data_center", data_center)
        elif "apikey" in config:
            # Backward compatibility - check for API key at top level
            api_key = config["apikey"]
            if api_key and "-" in api_key:
                # API key format: "prefix-datacenter"
                data_center = api_key.split("-")[-1]
                self._safe_add_field(config, "data_center", data_center)

    def _safe_add_field(self, config: MutableMapping[str, Any], field_name: str, value: Any) -> None:
        """
        Safely add a field to the config, avoiding framework-injected fields.
        
        Args:
            config: The config to modify
            field_name: The name of the field to add
            value: The value to set
        """
        # Avoid modifying framework-injected fields
        framework_fields = {
            "__injected_declarative_manifest",
            "__injected_components_py", 
            "__injected_components_py_checksums"
        }
        
        # Only add the field if it's not a framework-injected field
        if field_name not in framework_fields:
            dpath.new(config, [field_name], value)
