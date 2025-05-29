#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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
