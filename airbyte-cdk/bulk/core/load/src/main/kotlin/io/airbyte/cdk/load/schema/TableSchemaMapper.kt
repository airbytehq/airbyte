/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.model.TableName

/** Transforms input schema elements to destination-specific naming and type conventions. */
interface TableSchemaMapper {
    fun toFinalTableName(desc: DestinationStream.Descriptor): TableName

    fun toTempTableName(tableName: TableName): TableName

    fun toColumnName(name: String): String

    fun toColumnType(fieldType: FieldType): ColumnType

    fun toFinalSchema(
        inputToFinalColumnNames: Map<String, String>,
        inputSchema: Map<String, FieldType>,
        importType: ImportType,
    ) = inputSchema
        .map { inputToFinalColumnNames[it.key]!! to toColumnType(it.value) }
        .toMap()

    fun colsConflict(a: String, b: String): Boolean = a.equals(b, ignoreCase = true)
}
