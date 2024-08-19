# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
from typing import List, Optional, TypedDict

from typing_extensions import NotRequired


class Relationship(TypedDict):
    name: str
    relations: dict[str, str]
    false_positives: NotRequired[dict[str, str]]


Relationships = TypedDict("Relationships", {"streams": List[Relationship]})


class RelationshipsMerger:
    def merge(self, estimated_relationships: Relationships, confirmed_relationships: Relationships) -> Relationships:
        streams = []
        for estimated_stream in estimated_relationships["streams"]:
            confirmed_relationships_for_stream = self._get_stream(confirmed_relationships, estimated_stream["name"])
            if confirmed_relationships_for_stream:
                streams.append(self._merge_for_stream(estimated_stream, confirmed_relationships_for_stream))  # type: ignore  # at this point, we know confirmed_relationships_for_stream is not None
            else:
                streams.append(estimated_stream)

        already_processed_streams = set(map(lambda relationship: relationship["name"], streams))
        for confirmed_stream in confirmed_relationships["streams"]:
            if confirmed_stream["name"] not in already_processed_streams:
                streams.append(
                    {
                        "name": confirmed_stream["name"],
                        "relations": confirmed_stream["relations"],
                    }
                )
        return {"streams": streams}

    def _merge_for_stream(self, estimated: Relationship, confirmed: Relationship) -> Relationship:
        relations = copy.deepcopy(confirmed.get("relations", {}))

        # get estimated but filter out false positives
        for field, target in estimated.get("relations", {}).items():
            false_positives = confirmed["false_positives"] if "false_positives" in confirmed else {}
            if field not in relations and (field not in false_positives or false_positives.get(field, None) != target):  # type: ignore  # at this point, false_positives should not be None
                relations[field] = target

        return {
            "name": estimated["name"],
            "relations": relations,
        }

    def _get_stream(self, relationships: Relationships, stream_name: str) -> Optional[Relationship]:
        for stream in relationships["streams"]:
            if stream.get("name", None) == stream_name:
                return stream

        return None
