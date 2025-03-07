/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

/* We shouldn't have to create this but destination can't recognize this column if passed as field
 * type. This is to be used as CURSOR_FIELD in TriggerTableConfig.
 */
enum class SapHanaSourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {
    CHANGE_TIME(CdcStringMetaFieldType);

    override val id: String
        get() = TriggerTableConfig.TRIGGER_TABLE_PREFIX + name.lowercase()
}
