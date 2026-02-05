#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import requests

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState

logger = logging.getLogger("airbyte")

GSC_SITES_LIST_URL = "https://www.googleapis.com/webmasters/v3/sites"


@dataclass
class NestedSubstreamStateMigration(StateMigration):
    """
    We require a custom state migration because SearchAnalytics streams contain two nested levels of
    substreams. The existing LegacyToPerPartitionStateMigration only handles one level.

    Legacy state format is as follows:
    {
        "date": "2025-05-28",
        "https://www.example.com/": {
            "web": {
                "date": "2025-05-25"
            },
            "news": {
                "date": "2023-05-22"
            }
        }
    }

    The resulting migrated per-partition state is:
    {
        "use_global_cursor": false,
        "states": [
        {
            "partition": {
                "search_type": "web",
                "site_url": "https://www.example.com/"
            },
            "cursor": {
                "date": "2025-05-25"
            }
        },
        {
            "partition": {
                "search_type": "news",
                "site_url": "https://www.example.com/"
            },
            "cursor": {
                "date": "2023-05-22"
            }
        }],
        "state": {
            "date": "2025-05-25"
        }
    }
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return len(stream_state) > 0 and "states" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        per_partition_state = []
        for site_url_key, search_type_state in stream_state.items():
            if site_url_key == "date":
                # The legacy state also contains a global cursor value under the `date` key which equates
                # to global state.
                #
                # However, the Python implementation does not appear to be implemented
                # correctly and simply saves the state of the last seen partition. Since I don't trust the
                # legacy value and in the current implementation global state is applied to partitions
                # without an existing value, I'm making a conscious choice to not migrate the global value.
                continue
            else:
                site_url = site_url_key
                for search_type_key, cursor in search_type_state.items():
                    per_partition_state.append({"partition": {"site_url": site_url, "search_type": search_type_key}, "cursor": cursor})
        return {
            "use_global_cursor": False,
            "states": per_partition_state,
        }


@dataclass
class CustomReportExtractDimensionsFromKeys(RecordTransformation):
    """
    A record transformation that remaps each value in the keys array back to its associated
    dimension. The reason this is a custom component is because we're unable to use list
    comprehension and and enumerate() is not a valid function in our Jinja contact so can't
    iterate over the dimensions defined in the config to create each field transformation on the
    stream_template for each custom report.

    If we were able to, the actual ComponentMappingDefinition would look like this:

    type: ComponentMappingDefinition
    field_path:
      - transformations
      - "1"
      - fields
    value: "{{ [{'path': [dimension], 'value': '{{ record['keys'][index]} for index, dimension in enumerate(components_values['dimensions'])] }}"

    or

    type: ComponentMappingDefinition
    field_path:
      - transformations
      - "1"
      - fields
    value: >
      {% for index, dimension in enumerate(components_values["dimensions"]) %}
           - type: AddFields
             fields:
               - path: [ {{ dimension }} ]
                 value: "{{ record['keys'][index] }}"
      {% endfor %}
    """

    dimensions: List[str] = field(default_factory=lambda: [])

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        for dimension in self.dimensions:
            record[dimension] = record["keys"].pop(0)

        record.pop("keys")


@dataclass
class CustomReportSchemaLoader(SchemaLoader):
    """
    Custom schema loader is needed because Google Search Console's custom reports streams
    because the schema is dependent on which dimensions are selected in the config. Right now,
    only DynamicSchemaLoader which is based on the response from an API endpoint supports
    remapping of types to Airbyte schema types. This CustomReportSchemaLoader functions
    more like a static schema loader and so we must perform the remapping in this custom component.
    """

    DIMENSION_TO_PROPERTY_SCHEMA_MAP = {
        "country": [{"country": {"type": ["null", "string"]}}],
        "date": [{"date": {"type": ["null", "string"], "format": "date"}}],
        "device": [{"device": {"type": ["null", "string"]}}],
        "page": [{"page": {"type": ["null", "string"]}}],
        "query": [{"query": {"type": ["null", "string"]}}],
    }

    dimensions: List[str]

    def get_json_schema(self) -> Mapping[str, Any]:
        schema: Mapping[str, Any] = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": {
                # metrics
                "clicks": {"type": ["null", "integer"]},
                "ctr": {"type": ["null", "number"], "multipleOf": 1e-25},
                "impressions": {"type": ["null", "integer"]},
                "position": {"type": ["null", "number"], "multipleOf": 1e-25},
                # default fields
                "search_type": {"type": ["null", "string"]},
                "site_url": {"type": ["null", "string"]},
            },
        }

        # dimensions
        dimension_properties = self._dimension_to_property_schema()
        schema["properties"].update(dimension_properties)
        return schema

    def _dimension_to_property_schema(self) -> dict:
        properties = {}
        for dimension in sorted(self.dimensions):
            fields = self.DIMENSION_TO_PROPERTY_SCHEMA_MAP[dimension]
            for field in fields:
                properties = {**properties, **field}
        return properties


@dataclass
class EnhancedSitesRetriever(SimpleRetriever):
    """
    Custom retriever for the sites stream that enriches error messages during connection checks.

    When reading records fails (e.g., invalid property URL), this retriever calls GET /sites
    to fetch the user's available properties and includes them as suggestions in the error message.
    """

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[Union[Mapping[str, Any], AirbyteMessage]]:
        try:
            yield from super().read_records(records_schema, stream_slice)
        except AirbyteTracedException as error:
            original_message = error.message or error.internal_message or str(error)
            enhanced_context = self._build_enhanced_error_message()
            enhanced_message = f"{enhanced_context} (Original error: {original_message})"
            raise AirbyteTracedException(
                internal_message=enhanced_message,
                message=enhanced_message,
                failure_type=error.failure_type,
            ) from error

    def _build_enhanced_error_message(self) -> str:
        """Compose an enhanced error message with property suggestions when available."""
        available_properties = self._fetch_available_properties()

        if available_properties is None:
            return (
                "Could not verify the property. "
                "Make sure each property matches the exact format shown in "
                "Google Search Console: use 'https://example.com/' for "
                "URL-prefix properties or 'sc-domain:example.com' for "
                "domain properties. "
                "Open Google Search Console to check your property names: "
                "https://search.google.com/search-console"
            )

        if not available_properties:
            return (
                "No Search Console properties were found for this account. "
                "Make sure the authenticated account (OAuth user or service "
                "account email) has been added as a user in Google Search "
                "Console. To add access, go to Settings > Users and "
                "permissions in Search Console: "
                "https://search.google.com/search-console"
            )

        property_list = ", ".join(
            p.get("siteUrl", "unknown") for p in available_properties
        )
        return (
            f"The property was not found in your account. "
            f"Your account has access to these Search Console properties: "
            f"{property_list}. "
            f"Choose the property that matches the site you want to sync and "
            f"enter the exact value into the 'Search Console Properties' field."
        )

    def _fetch_available_properties(self) -> Optional[List[Dict[str, str]]]:
        """Call GET /sites to retrieve all properties the authenticated user can access.

        Returns a list of property dicts on success, an empty list if the account has no
        properties, or None if the request could not be completed (auth failure, HTTP error, etc.).
        """
        try:
            authenticator = self.requester.authenticator
            if not authenticator:
                return None
            headers = authenticator.get_auth_header()
        except Exception:
            logger.warning("Could not get auth headers for property lookup", exc_info=True)
            return None

        try:
            response = requests.get(GSC_SITES_LIST_URL, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            logger.warning("GET /sites request failed during property lookup", exc_info=True)
            return None

        data = response.json()
        return data.get("siteEntry", [])
