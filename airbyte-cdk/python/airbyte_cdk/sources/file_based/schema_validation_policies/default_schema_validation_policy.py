#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy


class DefaultSchemaValidationPolicy(AbstractSchemaValidationPolicy):
    SKIP_RECORD = "skip_record_on_schema_mismatch"
    EMIT_RECORD = "emit_record_on_schema_mismatch"
    WAIT = "wait_for_discover_on_schema_mismatch"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        """
        Return True if the record passes the user's validation policy.
        """
        return True
