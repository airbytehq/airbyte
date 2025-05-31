#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
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
        global_state: Optional[Mapping[str, Any]] = None
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
