/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType

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

    val PRIMARY_KEY_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "primary_key",
            type = StringFieldType,
        )

    val STREAM_NAME_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "stream_name",
            type = StringFieldType,
        )

    val OPERATION_TYPE_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "operation_type",
            type = StringFieldType,
        )

    val VALUE_BEFORE_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "value_before",
            type = JsonStringFieldType,
        )

    val VALUE_AFTER_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "value_after",
            type = JsonStringFieldType,
        )

    val SCHEMA: List<Field> =
        listOf(
            CHANGE_ID_FIELD,
            CURSOR_FIELD,
            PRIMARY_KEY_FIELD,
            STREAM_NAME_FIELD,
            OPERATION_TYPE_FIELD,
            VALUE_BEFORE_FIELD,
            VALUE_AFTER_FIELD,
        )
}
