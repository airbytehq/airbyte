from typing import List, Optional, TypedDict


ConvexConfig = TypedDict(
    "ConvexConfig",
    {
        "deployment_url": str,
        "access_key": str,
    },
)

StreamMetadata = TypedDict(
    "StreamMetadata",
    {
        "stream": str,
        "syncMode": str,
        "cursor": List[str],
        "destinationSyncMode": str,
        "primaryKey": List[List[str]],
        "jsonSchema": str,
        "namespace": Optional[str],
    },
)
