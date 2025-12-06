/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName

/** Transforms input schema elements to destination-specific naming and type conventions. */
interface TableSchemaMapper {
    fun toFinalTableName(desc: DestinationStream.Descriptor): TableName

    fun toTempTableName(tableName: TableName): TableName

    fun toColumnName(name: String): String

    fun toColumnType(fieldType: FieldType): ColumnType

    fun toFinalSchema(tableSchema: StreamTableSchema) = tableSchema

    fun colsConflict(a: String, b: String): Boolean = a.equals(b, ignoreCase = true)
}
