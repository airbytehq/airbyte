/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.ImportType

data class StreamTableSchema(
    val tableNames: TableNames,
    val columnSchema: ColumnSchema,
    val importType: ImportType,
) {
    fun getFinalColumnName(rawName: String) = columnSchema.rawToFinalColumnNames[rawName]!!

    fun getCursor() =
        if (importType is Dedupe)
            importType.cursor.map { columnSchema.rawToFinalColumnNames[it]!! }
        else
            emptyList()

    fun getPrimaryKey() =
        if (importType is Dedupe)
            importType.primaryKey.map {
                keys -> keys.map { columnSchema.rawToFinalColumnNames[it]!! }
            }
        else
            emptyList()
}
