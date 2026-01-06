/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

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
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.table.TypingDedupingUtil
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDataType
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier
import jakarta.inject.Singleton

@Singleton
class SnowflakeTableSchemaMapper(
    private val config: SnowflakeConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = desc.namespace ?: config.schema
        return if (!config.legacyRawTablesOnly) {
            TableName(
                namespace = namespace.toSnowflakeCompatibleName(),
                name = desc.name.toSnowflakeCompatibleName(),
            )
        } else {
            TableName(
                namespace = config.internalTableSchema,
                name =
                    TypingDedupingUtil.concatenateRawTableName(
                        namespace = escapeJsonIdentifier(namespace),
                        name = escapeJsonIdentifier(desc.name),
                    ),
            )
        }
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return if (!config.legacyRawTablesOnly) {
            name.toSnowflakeCompatibleName()
        } else {
            // In legacy mode, column names are not transformed
            name
        }
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val snowflakeType =
            when (fieldType.type) {
                // Simple types
                BooleanType -> SnowflakeDataType.BOOLEAN.typeName
                IntegerType -> SnowflakeDataType.NUMBER.typeName
                NumberType -> SnowflakeDataType.FLOAT.typeName
                StringType -> SnowflakeDataType.VARCHAR.typeName

                // Temporal types
                DateType -> SnowflakeDataType.DATE.typeName
                TimeTypeWithTimezone -> SnowflakeDataType.VARCHAR.typeName
                TimeTypeWithoutTimezone -> SnowflakeDataType.TIME.typeName
                TimestampTypeWithTimezone -> SnowflakeDataType.TIMESTAMP_TZ.typeName
                TimestampTypeWithoutTimezone -> SnowflakeDataType.TIMESTAMP_NTZ.typeName

                // Semistructured types
                is ArrayType,
                ArrayTypeWithoutSchema -> SnowflakeDataType.ARRAY.typeName
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> SnowflakeDataType.OBJECT.typeName
                is UnionType -> SnowflakeDataType.VARIANT.typeName
                is UnknownType -> SnowflakeDataType.VARIANT.typeName
            }

        return ColumnType(snowflakeType, fieldType.nullable)
    }

    override fun toFinalSchema(tableSchema: StreamTableSchema): StreamTableSchema {
        if (!config.legacyRawTablesOnly) {
            return tableSchema
        }

        return StreamTableSchema(
            tableNames = tableSchema.tableNames,
            columnSchema =
                tableSchema.columnSchema.copy(
                    finalSchema =
                        mapOf(
                            Meta.COLUMN_NAME_DATA to
                                ColumnType(SnowflakeDataType.VARIANT.typeName, false)
                        )
                ),
            importType = tableSchema.importType,
        )
    }
}
