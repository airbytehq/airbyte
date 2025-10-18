/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField
import kotlin.text.lowercase

/* We shouldn't have to create this but destination can't recognize this column if passed as field
 * type. This is to be used as CURSOR_FIELD in TriggerTableConfig.
 */
enum class TriggerCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    CHANGE_TIME(CdcStringMetaFieldType);

    override val id: String
        get() = TriggerTableConfig.TRIGGER_TABLE_PREFIX + name.lowercase()
}
