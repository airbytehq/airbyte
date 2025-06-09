#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


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
