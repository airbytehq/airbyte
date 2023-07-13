#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, StopSyncPerValidationPolicy
from airbyte_cdk.sources.file_based.schema_helpers import conforms_to_schema
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy


class EmitRecordPolicy(AbstractSchemaValidationPolicy):
    name = "emit_record"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        return True


class SkipRecordPolicy(AbstractSchemaValidationPolicy):
    name = "skip_record"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        return conforms_to_schema(record, schema)


class WaitForDiscoverPolicy(AbstractSchemaValidationPolicy):
    name = "wait_for_discover"
    validate_schema_before_sync = True

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        if not conforms_to_schema(record, schema):
            raise StopSyncPerValidationPolicy(FileBasedSourceError.STOP_SYNC_PER_SCHEMA_VALIDATION_POLICY)
        return True


DEFAULT_SCHEMA_VALIDATION_POLICIES = {
    "emit_record": EmitRecordPolicy(),
    "skip_record": SkipRecordPolicy(),
    "wait_for_discover": WaitForDiscoverPolicy(),
}
