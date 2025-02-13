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
    val CURSOR_FIELD =
        Field(
            id = TRIGGER_TABLE_PREFIX + "change_time",
            type = OffsetDateTimeFieldType,
        )

    val SCHEMA: List<Field> =
        listOf(
            Field(
                id = TRIGGER_TABLE_PREFIX + "change_id",
                type = BigIntegerFieldType,
            ),
            CURSOR_FIELD,
            Field(
                id = TRIGGER_TABLE_PREFIX + "primary_key",
                type = StringFieldType,
            ),
            Field(
                id = TRIGGER_TABLE_PREFIX + "stream_name",
                type = StringFieldType,
            ),
            Field(
                id = TRIGGER_TABLE_PREFIX + "operation_type",
                type = StringFieldType,
            ),
            Field(
                id = TRIGGER_TABLE_PREFIX + "value_before",
                type = JsonStringFieldType,
            ),
            Field(
                id = TRIGGER_TABLE_PREFIX + "value_after",
                type = JsonStringFieldType,
            )
        )
}
