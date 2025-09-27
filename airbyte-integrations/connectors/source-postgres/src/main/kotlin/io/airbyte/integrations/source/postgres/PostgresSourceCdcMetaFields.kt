/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcNumberMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

enum class PostgresSourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    CDC_CURSOR(CdcIntegerMetaFieldType),
    CDC_LOG_POS(CdcNumberMetaFieldType),
    CDC_LOG_FILE(CdcStringMetaFieldType),
    CDC_LSN(CdcIntegerMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
