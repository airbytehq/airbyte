/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.defaults

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Default schema mapper that performs no transformations on names or types.
 *
 * For destinations that don't do schema munging in the new paradigm.
 */
@Singleton
@Secondary
class NoopTableSchemaMapper : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor) =
        TableName(desc.namespace ?: "", desc.name)

    override fun toTempTableName(tableName: TableName) = tableName

    override fun toColumnName(name: String) = name

    override fun toColumnType(fieldType: FieldType): ColumnType =
        ColumnType(
            fieldType.type.toString(),
            fieldType.nullable,
        )
}
