#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import re
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.types import StreamSlice, StreamState


logger = logging.getLogger("airbyte")


# Pattern to identify custom field keys (40-character alphanumeric hash)
CUSTOM_FIELD_KEY_PATTERN = re.compile(r"^[a-f0-9]{40}$")


@dataclass
class NullCheckedDpathExtractor(RecordExtractor):
    """
    Pipedrive requires a custom extractor because the format of its API responses is inconsistent.

    Records are typically found in a nested "data" field, but sometimes the "data" field is null.
    This extractor checks for null "data" fields and returns the parent object, which contains the record ID, instead.

    Example faulty records:
    ```
      {
        "item": "file",
        "id": <an_id>,
        "data": null
      },
      {
        "item": "file",
        "id": <another_id>,
        "data": null
      }
    ```
    """

    field_path: List[Union[InterpolatedString, str]]
    nullable_nested_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._dpath_extractor = DpathExtractor(
            field_path=self.field_path,
            config=self.config,
            parameters=parameters,
            decoder=self.decoder,
        )

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        records = self._dpath_extractor.extract_records(response)
        return [record.get(self.nullable_nested_field) or record for record in records]


@dataclass
class CustomFieldsTransformation(RecordTransformation):
    """
    Transforms Pipedrive records to include human-readable custom field names.

    Pipedrive returns custom fields with 40-character hash keys (e.g., "abc123def456...").
    This transformation:
    1. Fetches field definitions from the appropriate *Fields endpoint
    2. Maps hash keys to human-readable field names
    3. Adds new fields with the pattern: custom_<field_name> = <value>

    The original hash-keyed fields are preserved for backwards compatibility.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    fields_endpoint: str  # e.g., "v1/dealFields", "v1/personFields", "v1/organizationFields"
    _field_mapping: Dict[str, Dict[str, Any]] = field(default_factory=dict, init=False)
    _fields_fetched: bool = field(default=False, init=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def _fetch_field_definitions(self) -> None:
        """Fetch and cache field definitions from the Pipedrive API."""
        if self._fields_fetched:
            return

        api_token = self.config.get("api_token")
        base_url = "https://api.pipedrive.com"

        try:
            url = f"{base_url}/{self.fields_endpoint}"
            all_fields = []
            start = 0
            limit = 100

            while True:
                response = requests.get(
                    url,
                    params={"api_token": api_token, "start": start, "limit": limit},
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success") and data.get("data"):
                    all_fields.extend(data["data"])

                    # Check if there are more pages
                    pagination = data.get("additional_data", {}).get("pagination", {})
                    if pagination.get("more_items_in_collection"):
                        start = pagination.get("next_start", start + limit)
                    else:
                        break
                else:
                    break

            # Build the field mapping: key -> {name, field_type, options, ...}
            for field_def in all_fields:
                key = field_def.get("key")
                if key and self._is_custom_field_key(key):
                    self._field_mapping[key] = {
                        "name": field_def.get("name", key),
                        "field_type": field_def.get("field_type"),
                        "options": {
                            str(opt.get("id")): opt.get("label")
                            for opt in (field_def.get("options") or [])
                            if opt.get("id") is not None
                        },
                    }
                    # Also handle subfields (e.g., for monetary fields: key_currency)
                    if field_def.get("field_type") in ("monetary", "daterange", "timerange"):
                        suffix_map = {
                            "monetary": "_currency",
                            "daterange": ("_from", "_until"),
                            "timerange": ("_from", "_until"),
                        }
                        suffixes = suffix_map.get(field_def.get("field_type"), ())
                        if isinstance(suffixes, str):
                            suffixes = (suffixes,)
                        for suffix in suffixes:
                            subfield_key = f"{key}{suffix}"
                            self._field_mapping[subfield_key] = {
                                "name": f"{field_def.get('name', key)}{suffix}",
                                "field_type": "subfield",
                                "options": {},
                            }

            self._fields_fetched = True
            logger.info(f"Fetched {len(self._field_mapping)} custom field definitions from {self.fields_endpoint}")

        except Exception as e:
            logger.warning(f"Failed to fetch field definitions from {self.fields_endpoint}: {e}")
            self._fields_fetched = True  # Don't retry on every record

    def _is_custom_field_key(self, key: str) -> bool:
        """Check if a key matches the Pipedrive custom field pattern (40-char hex hash)."""
        return bool(CUSTOM_FIELD_KEY_PATTERN.match(str(key)))

    def _sanitize_field_name(self, name: str) -> str:
        """Convert a field name to a valid, consistent key format."""
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())
        # Remove consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")
        return sanitized

    def _resolve_option_value(self, value: Any, options: Dict[str, str]) -> Any:
        """
        Resolve option IDs to their labels for enum/set fields.

        For set fields (multiple values), the value is a comma-separated string of IDs.
        """
        if not options or value is None:
            return value

        str_value = str(value)

        # Check if it's a comma-separated list (set field)
        if "," in str_value:
            ids = [id.strip() for id in str_value.split(",")]
            labels = [options.get(id, id) for id in ids]
            return ", ".join(labels)

        # Single value (enum field)
        return options.get(str_value, value)

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform the record by adding human-readable custom field names.

        For each custom field (identified by a 40-char hash key), adds:
        - custom_<sanitized_field_name>: The value (with option labels resolved if applicable)
        """
        self._fetch_field_definitions()

        if not self._field_mapping:
            return

        custom_fields: Dict[str, Any] = {}

        for key, value in list(record.items()):
            if key in self._field_mapping:
                field_info = self._field_mapping[key]
                field_name = field_info["name"]
                sanitized_name = self._sanitize_field_name(field_name)

                # Resolve option values to labels
                resolved_value = self._resolve_option_value(value, field_info.get("options", {}))

                # Add the custom field with a readable name
                custom_field_key = f"custom_{sanitized_name}"
                custom_fields[custom_field_key] = resolved_value

        # Add all custom fields to the record
        record.update(custom_fields)
