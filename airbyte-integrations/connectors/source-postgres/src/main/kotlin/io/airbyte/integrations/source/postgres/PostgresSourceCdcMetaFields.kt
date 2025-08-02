/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

enum class PostgresSourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    UPDATED_AT(CdcOffsetDateTimeMetaFieldType),
    DELETED_AT(CdcOffsetDateTimeMetaFieldType),
    CDC_LSN(CdcIntegerMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
