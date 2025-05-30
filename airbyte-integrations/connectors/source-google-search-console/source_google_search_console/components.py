#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class GoogleSearchConsoleTransformKeysToDimensions(RecordTransformation):
    """
    A record transformation that remaps each value in the keys array back to its associated
    dimension. The reason this is a custom component is because each value in the keys array
    corresponds to the same order of the dimensions array which was used in the API request.

    TBD: Maybe we can remove if I find a way to do this in low-code only. Assuming we start
    using quote_plus() only on the outbound API request path, we can potentially remove this component.
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

        # Remove unnecessary empty field. This could be done in a RemoveFields transformation, as this
        # is not custom behavior, but given that we're transforming the record by moving the keys under,
        # dimensions, it is better to keep the functionality in a single transformation.
        record.pop("keys")


@dataclass
class NestedSubstreamStateMigration(StateMigration):
    """
    We require a custom state migration to move from the custom substream state that was generated via the legacy
    cursor custom components. State was not written back to the platform in a way that is compatible with concurrent cursors.

    The old state roughly had the following shape:
    {
        "updated_at": 1744153060,
        "prior_state": {
            "updated_at": 1744066660
        }
        "conversations": {
            "updated_at": 1744153060
        }
    }

    However, this was incompatible when we removed the custom cursors with the concurrent substream partition cursor
    components that were configured with use global_substream_cursor and incremental_dependency. They rely on passing the value
    of parent_state when getting parent records for the conversations/companies parent stream. The migration results in state:
    {
        "updated_at": 1744153060,
        "prior_state": {
            "updated_at": 1744066660
            # There are a lot of nested elements here, but are not used or relevant to syncs
        }
        "conversations": {
            "updated_at": 1744153060
        }
        "parent_state": {
            "conversations": {
                "updated_at": 1744153060
            }
        }
    }
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return len(stream_state) > 0 and "states" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        global_state: Optional[Mapping[str, Any]] = None
        per_partition_state = []
        for site_url_key, search_type_state in stream_state.items():
            if site_url_key == "date":
                # The legacy state also contains a global cursor value under the `date` key which we
                # treat as the global state
                global_state = {site_url_key: search_type_state}
            else:
                site_url = site_url_key
                for search_type_key, cursor in search_type_state.items():
                    per_partition_state.append({"partition": {"site_url": site_url, "search_type": search_type_key}, "cursor": cursor})
        if global_state:
            return {
                "use_global_cursor": False,
                "states": per_partition_state,
                "state": global_state,
            }
        else:
            return {
                "use_global_cursor": False,
                "states": per_partition_state,
            }
