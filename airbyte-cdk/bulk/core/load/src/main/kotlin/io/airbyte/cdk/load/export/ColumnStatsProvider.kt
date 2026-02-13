/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import io.airbyte.cdk.load.schema.model.TableName

data class ColumnStats(val nullCount: Long, val nonNullCount: Long)

interface ColumnStatsProvider {
    fun computeColumnStats(
        tableName: TableName,
        columnNames: Collection<String>,
    ): Map<String, ColumnStats>
}
