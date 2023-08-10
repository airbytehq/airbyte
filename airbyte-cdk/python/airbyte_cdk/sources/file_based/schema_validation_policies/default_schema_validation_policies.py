#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional

from airbyte_cdk.sources.file_based.config.file_based_stream_config import ValidationPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, StopSyncPerValidationPolicy
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.file_based.types import StreamSchema


class EmitRecordPolicy(AbstractSchemaValidationPolicy):
    name = "emit_record"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Optional[StreamSchema]) -> bool:
        return True


class SkipRecordPolicy(AbstractSchemaValidationPolicy):
    name = "skip_record"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Optional[StreamSchema]) -> bool:
        return schema is not None and schema.value_is_conform(record)


class WaitForDiscoverPolicy(AbstractSchemaValidationPolicy):
    name = "wait_for_discover"
    validate_schema_before_sync = True

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Optional[StreamSchema]) -> bool:
        if schema is None or not schema.value_is_conform(record):
            raise StopSyncPerValidationPolicy(FileBasedSourceError.STOP_SYNC_PER_SCHEMA_VALIDATION_POLICY)
        return True


DEFAULT_SCHEMA_VALIDATION_POLICIES = {
    ValidationPolicy.emit_record: EmitRecordPolicy(),
    ValidationPolicy.skip_record: SkipRecordPolicy(),
    ValidationPolicy.wait_for_discover: WaitForDiscoverPolicy(),
}
