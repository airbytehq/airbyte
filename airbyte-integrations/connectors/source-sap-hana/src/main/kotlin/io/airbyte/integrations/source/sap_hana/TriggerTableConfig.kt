/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream

/**
 * Trigger table related constants, schema etc. We use change time as cursor. Trigger table naming
 * convention: TRIGGER_TABLE_PREFIX + <schema_name> + <table_name>.
 */
object TriggerTableConfig {
    const val TRIGGER_TABLE_PREFIX = "_ab_trigger_"
    const val TRIGGER_TABLE_NAMESPACE = "_ab_cdc"

    val CHANGE_ID_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "change_id",
            type = BigIntegerFieldType,
        )

    val CURSOR_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "change_time",
            type = OffsetDateTimeFieldType,
        )

    val OPERATION_TYPE_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "operation_type",
            type = StringFieldType,
        )

    val COMMON_FIELDS: List<Field> =
        listOf(
            CHANGE_ID_FIELD,
            CURSOR_FIELD,
            OPERATION_TYPE_FIELD,
        )

    fun getTriggerTableSchemaFromStream(stream: Stream): List<Field> {
        val result = mutableListOf<Field>()

        stream.schema.forEach { field ->
            result.add(Field(id = TRIGGER_TABLE_PREFIX + field.id + "_before", type = field.type))
            result.add(Field(id = TRIGGER_TABLE_PREFIX + field.id + "_after", type = field.type))
        }
        return COMMON_FIELDS + result
    }
}
