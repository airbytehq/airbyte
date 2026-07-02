/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.client

object DorisSqlTypes {
    const val BOOLEAN = "BOOLEAN"
    const val BIGINT = "BIGINT"
    const val DECIMAL = "DECIMAL(38, 9)"
    const val STRING = "STRING"
    const val DATE = "DATE"
    const val DATETIME = "DATETIME(3)"
    const val JSON = "JSON"
    const val VARCHAR_40 = "VARCHAR(40)"
}
