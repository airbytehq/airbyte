/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import jakarta.inject.Singleton

@Singleton
class TableSchemaFactory(
    private val mapper: TableSchemaMapper,
    private val colNameResolver: ColumnNameResolver,
) {
    fun make(
        finalTableName: TableName,
        inputSchema: Map<String, FieldType>,
        importType: ImportType,
    ): StreamTableSchema {
        val tempTableName = mapper.toTempTableName(finalTableName)
        val tableNames =
            TableNames(
                finalTableName = finalTableName,
                tempTableName = tempTableName,
            )

        val inputToFinalColumnNames = colNameResolver.getColumnNameMapping(inputSchema.keys)
        val finalSchema =
            inputSchema
                .map { inputToFinalColumnNames[it.key]!! to mapper.toColumnType(it.value) }
                .toMap()

        val columnSchema =
            ColumnSchema(
                inputSchema = inputSchema,
                inputToFinalColumnNames = inputToFinalColumnNames,
                finalSchema = finalSchema,
            )

        return StreamTableSchema(
            tableNames,
            columnSchema,
            importType,
        )
    }
}
