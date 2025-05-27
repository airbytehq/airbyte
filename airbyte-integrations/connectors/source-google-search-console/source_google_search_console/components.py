#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import unquote_plus

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


@dataclass
class GoogleSearchConsoleInjectTransformedSiteUrlAndDimensions(RecordTransformation):
    """
    A record transformation that flattens the `associations` field in HubSpot records.
    This transformation takes a nested dictionary under the `associations` key and extracts the IDs
    of associated objects. The extracted lists of IDs are added as new top-level fields in the record,
    using the association name as the key (spaces replaced with underscores).
    Example:
        Input:
        {
            "id": 1,
            "associations": {
                "Contacts": {"results": [{"id": 101}, {"id": 102}]}
            }
        }
        Output:
        {
            "id": 1,
            "Contacts": [101, 102]
        }
    """

    dimensions: List[str] = field(default_factory=lambda: [])

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        record["site_url"] = unquote_plus(stream_slice.get("site_url"))

        for dimension in self.dimensions:
            record[dimension] = record["keys"].pop(0)

        # Remove unnecessary empty field. This could be done in a RemoveFields transformation, as this
        # is not custom behavior, but given that we're transforming the record by moving the keys under,
        # dimensions, it is better to keep the functionality in a single transformation.
        record.pop("keys")
