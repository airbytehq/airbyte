# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Mapping


class PerPartitionKeySerializer:
    """
    We are concerned of the performance of looping through the `states` list and evaluating equality on the partition. To reduce this
    concern, we wanted to use dictionaries to map `partition -> cursor`. However, partitions are dict and dict can't be used as dict keys
    since they are not hashable. By creating json string using the dict, we can have a use the dict as a key to the dict since strings are
    hashable.
    """

    @staticmethod
    def to_partition_key(to_serialize: Any) -> str:
        # separators have changed in Python 3.4. To avoid being impacted by further change, we explicitly specify our own value
        return json.dumps(to_serialize, indent=None, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def to_partition(to_deserialize: Any) -> Mapping[str, Any]:
        return json.loads(to_deserialize)  # type: ignore # The partition is known to be a dict, but the type hint is Any
