# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import pytest
from deepdiff import DeepDiff  # type: ignore


class TestDataIntegrity:
    def test_all_pks_are_produced_in_target_version(self, control_and_target_artifacts_per_sessions) -> None:
        # TODO iterating on session results could be factorized into parametrized tests
        for control_artifacts, target_artifacts in control_and_target_artifacts_per_sessions:
            for control_stream, control_pks in control_artifacts.pks_per_streams.items():
                target_pks = target_artifacts.pks_per_streams[control_stream]
                missing_pks = set(control_pks) - set(target_pks)
                assert not missing_pks, f"Missing {len(missing_pks)} primary keys in target version on stream {control_stream}"

    def test_record_counts_match(
        self,
        control_and_target_artifacts_per_sessions,
    ):
        for control_artifacts, target_artifacts in control_and_target_artifacts_per_sessions:
            target_record_count = target_artifacts.message_type_count.get("RECORD", 0)
            control_record_count = control_artifacts.message_type_count.get("RECORD", 0)
            assert (
                control_record_count <= target_record_count
            ), f"Target version produced less records than control version ({target_record_count} vs {control_record_count})"

    def test_record_schema_match(self, control_and_target_artifacts_per_sessions) -> None:
        streams_with_mistmatched_schemas = []
        for control_artifacts, target_artifacts in control_and_target_artifacts_per_sessions:
            for stream, control_schema in control_artifacts.stream_schemas.items():
                target_schema = target_artifacts.stream_schemas.get(stream, {})
                diff = DeepDiff(control_schema, target_schema, ignore_order=True)
                if diff:
                    streams_with_mistmatched_schemas.append(stream)
        if streams_with_mistmatched_schemas:
            pytest.fail(
                f"{len(streams_with_mistmatched_schemas)} streams have different schema between control and target versions: {streams_with_mistmatched_schemas}"
            )
