/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

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

fun String.isValidVersionColumnType() = VALID_VERSION_COLUMN_TYPES.contains(this)
