/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import io.airbyte.cdk.load.table.CDC_CURSOR_COLUMN
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlTypes.VALID_VERSION_COLUMN_TYPES

object ClickhouseSqlTypes {
    const val DATETIME_WITH_PRECISION = "DateTime64(3)"
    const val DECIMAL_WITH_PRECISION_AND_SCALE = "Decimal(38, 9)"
    const val BOOL = "Bool"
    const val DATE32 = "Date32"
    const val INT64 = "Int64"
    const val STRING = "String"
    const val JSON = "JSON"

    val VALID_VERSION_COLUMN_TYPES =
        setOf(
            INT64,
            DATE32,
            DATETIME_WITH_PRECISION,
        )
}

// Warning: if any munging changes the name of the CDC column name this will break.
// Currently, that is not the case.
fun isValidVersionColumn(name: String, type: String) =
    // CDC cursors cannot be used as a version column since they are null
    // during the initial CDC snapshot.
    name != CDC_CURSOR_COLUMN && VALID_VERSION_COLUMN_TYPES.contains(type)
