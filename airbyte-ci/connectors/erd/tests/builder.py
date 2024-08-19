# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from erd.relationships import Relationship


class RelationshipBuilder:
    def __init__(self, stream_name: str) -> None:
        self._name = stream_name
        self._relations: dict[str, str] = {}
        self._false_positives: dict[str, str] = {}

    def with_relationship(self, column: str, target: str) -> "RelationshipBuilder":
        self._relations[column] = target
        return self

    def with_false_positive(self, column: str, target: str) -> "RelationshipBuilder":
        self._false_positives[column] = target
        return self

    def build(self) -> Relationship:
        result = {
            "name": self._name,
            "relations": self._relations,
        }
        if self._false_positives:
            result["false_positives"] = self._false_positives
        return result
