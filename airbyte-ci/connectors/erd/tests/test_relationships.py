# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from erd.relationships import Relationships, RelationshipsMerger
from tests.builder import RelationshipBuilder

_A_STREAM_NAME = "a_stream_name"
_A_COLUMN = "a_column"
_ANOTHER_COLUMN = "another_column"
_A_TARGET = "a_target_table.a_target_column"
_ANOTHER_TARGET = "another_target_table.a_target_column"


class RelationshipsMergerTest(TestCase):
    def setUp(self) -> None:
        self._merger = RelationshipsMerger()

    def test_given_no_confirmed_then_return_estimation(self) -> None:
        estimated: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _A_TARGET).build()]}
        confirmed: Relationships = {"streams": []}

        merged = self._merger.merge(estimated, confirmed)

        assert merged == estimated

    def test_given_confirmed_as_false_positive_then_remove_from_estimation(self) -> None:
        estimated: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _A_TARGET).build()]}
        confirmed: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_false_positive(_A_COLUMN, _A_TARGET).build()]}

        merged = self._merger.merge(estimated, confirmed)

        assert merged == {"streams": [{"name": "a_stream_name", "relations": {}}]}

    def test_given_no_estimated_but_confirmed_then_return_confirmed_without_false_positives(self) -> None:
        estimated: Relationships = {"streams": []}
        confirmed: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _A_TARGET).build()]}

        merged = self._merger.merge(estimated, confirmed)

        assert merged == confirmed

    def test_given_different_columns_then_return_both(self) -> None:
        estimated: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _A_TARGET).build()]}
        confirmed: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_ANOTHER_COLUMN, _A_TARGET).build()]}

        merged = self._merger.merge(estimated, confirmed)

        assert merged == {
            "streams": [
                {
                    "name": "a_stream_name",
                    "relations": {
                        _A_COLUMN: _A_TARGET,
                        _ANOTHER_COLUMN: _A_TARGET,
                    },
                }
            ]
        }

    def test_given_same_column_but_different_value_then_prioritize_confirmed(self) -> None:
        estimated: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _A_TARGET).build()]}
        confirmed: Relationships = {"streams": [RelationshipBuilder(_A_STREAM_NAME).with_relationship(_A_COLUMN, _ANOTHER_TARGET).build()]}

        merged = self._merger.merge(estimated, confirmed)

        assert merged == {
            "streams": [
                {
                    "name": "a_stream_name",
                    "relations": {
                        _A_COLUMN: _ANOTHER_TARGET,
                    },
                }
            ]
        }
