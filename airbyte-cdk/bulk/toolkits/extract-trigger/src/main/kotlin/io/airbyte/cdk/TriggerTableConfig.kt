/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream

/**
 * Trigger table related constants, schema etc. Trigger table naming convention:
 * TRIGGER_TABLE_PREFIX + <schema_name> + <table_name>.
 */
abstract class TriggerTableConfig() {

    abstract val cursorFieldType: FieldType
    abstract val cdcEnabled: Boolean

    val CURSOR_FIELD: EmittedField
        get() =
            EmittedField(
                id = TRIGGER_TABLE_PREFIX + "change_time",
                type = cursorFieldType,
            )

    val COMMON_FIELDS: List<EmittedField>
        get() =
            listOf(
                CHANGE_ID_FIELD,
                CURSOR_FIELD,
                OPERATION_TYPE_FIELD,
            )

    fun getTriggerTableSchemaFromStream(stream: Stream): List<EmittedField> {
        val result = mutableListOf<EmittedField>()

        stream.schema.forEach { field ->
            result.add(
                EmittedField(id = TRIGGER_TABLE_PREFIX + field.id + "_before", type = field.type)
            )
            result.add(
                EmittedField(id = TRIGGER_TABLE_PREFIX + field.id + "_after", type = field.type)
            )
        }
        return COMMON_FIELDS + result
    }

    companion object {
        const val TRIGGER_TABLE_PREFIX = "_ab_trigger_"
        const val TRIGGER_TABLE_NAMESPACE = "_ab_cdc"
        val CHANGE_ID_FIELD =
            EmittedField(
                id = TRIGGER_TABLE_PREFIX + "change_id",
                type = BigIntegerFieldType,
            )
        val OPERATION_TYPE_FIELD =
            EmittedField(
                id = TRIGGER_TABLE_PREFIX + "operation_type",
                type = StringFieldType,
            )
    }
}
