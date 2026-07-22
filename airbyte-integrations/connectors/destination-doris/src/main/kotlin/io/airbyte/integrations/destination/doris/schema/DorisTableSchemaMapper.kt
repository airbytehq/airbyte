/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.schema

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.doris.client.DorisSqlTypes
import io.airbyte.integrations.destination.doris.spec.DorisConfiguration
import jakarta.inject.Singleton

@Singleton
class DorisTableSchemaMapper(
    private val config: DorisConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.database).toDorisCompatibleName()
        val name = desc.name.toDorisCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toDorisCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val dorisType =
            when (fieldType.type) {
                BooleanType -> DorisSqlTypes.BOOLEAN
                DateType -> DorisSqlTypes.DATE
                IntegerType -> DorisSqlTypes.BIGINT
                NumberType -> DorisSqlTypes.DECIMAL
                StringType -> DorisSqlTypes.STRING
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> DorisSqlTypes.STRING
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> DorisSqlTypes.DATETIME
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> DorisSqlTypes.JSON
                is ArrayType,
                ArrayTypeWithoutSchema -> DorisSqlTypes.JSON
                is UnionType,
                is UnknownType -> DorisSqlTypes.STRING
            }

        return ColumnType(dorisType, fieldType.nullable)
    }

    override fun toFinalSchema(tableSchema: StreamTableSchema): StreamTableSchema {
        if (tableSchema.importType !is Dedupe) {
            return tableSchema
        }

        // For Dedupe mode, make primary key columns non-nullable
        val pks = tableSchema.getPrimaryKey().flatten()

        val finalSchema =
            tableSchema.columnSchema.finalSchema
                .map { (name, type) ->
                    name to type.copy(nullable = type.nullable && !pks.contains(name))
                }
                .toMap()

        return tableSchema.copy(
            columnSchema = tableSchema.columnSchema.copy(finalSchema = finalSchema)
        )
    }
}
