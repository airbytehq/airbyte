/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

/** PostgreSQL CDC-specific meta fields added to records during CDC sync. */
enum class PostgresV2SourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    /**
     * A monotonically increasing cursor value derived from the LSN, used for deduplication in
     * incremental syncs.
     */
    CDC_CURSOR(CdcIntegerMetaFieldType),

    /** The LSN (Log Sequence Number) as a string in PostgreSQL format (e.g., "0/16B3748"). */
    CDC_LSN(CdcStringMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
