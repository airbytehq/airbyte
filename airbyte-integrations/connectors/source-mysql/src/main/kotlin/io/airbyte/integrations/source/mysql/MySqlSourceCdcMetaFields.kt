/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

enum class MySqlSourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    CDC_CURSOR(CdcIntegerMetaFieldType),
    CDC_LOG_POS(CdcIntegerMetaFieldType),
    CDC_LOG_FILE(CdcStringMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
