/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.ImportType

/**
 * Schema information for a stream's table representation resolved for the target destination.
 *
 * Contains everything necessary to perform table operations for the associated stream.
 */
data class StreamTableSchema(
    val tableNames: TableNames,
    val columnSchema: ColumnSchema,
    val importType: ImportType,
) {
    fun getFinalColumnName(rawName: String) = columnSchema.inputToFinalColumnNames[rawName]!!

    /** Note: Returns final munged column names. */
    fun getCursor() =
        if (importType is Dedupe)
            importType.cursor.map { columnSchema.inputToFinalColumnNames[it]!! }
        else emptyList()

    /** Note: Returns final munged column names. */
    fun getPrimaryKey() =
        if (importType is Dedupe)
            importType.primaryKey.map { keys ->
                keys.map { columnSchema.inputToFinalColumnNames[it]!! }
            }
        else emptyList()
}
