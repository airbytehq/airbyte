from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from airbyte_cdk.sources.declarative.transformations.transformation import (
    RecordTransformation,
)
from airbyte_cdk.sources.declarative.types import (
    Config,
    Record,
    StreamSlice,
    StreamState,
)


@dataclass
class CustomFieldTransformation(RecordTransformation):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        Method to add `lastUpdated` field to root of record and
        convert the timestamp format
            - From: "%Y-%m-%dT%H:%M:%S.%fZ"
            - To:   "%Y-%m-%d %H:%M"
        This data is stored in the stream state and is critical
        to the functioning of the incremental sync
        """
        timestamp = record.get("history", {}).get("lastUpdated", {}).get("when")
        if timestamp:
            try:
                record["lastUpdated"] = datetime.strptime(
                    timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
                ).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

        return record
