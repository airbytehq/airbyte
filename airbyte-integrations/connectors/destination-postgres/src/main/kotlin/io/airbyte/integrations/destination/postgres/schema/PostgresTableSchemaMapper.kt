/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.schema

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
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.PostgresDataType
import jakarta.inject.Singleton
import java.util.Locale

@Singleton
class PostgresTableSchemaMapper(
    private val config: PostgresConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = desc.namespace ?: config.schema
        return if (!config.legacyRawTablesOnly) {
            TableName(
                namespace = namespace.toPostgresCompatibleName(),
                name = desc.name.toPostgresCompatibleName(),
            )
        } else {
            TableName(
                namespace = config.internalTableSchema!!.lowercase().toPostgresCompatibleName(),
                name =
                    TypingDedupingUtil.concatenateRawTableName(
                            namespace = namespace,
                            name = desc.name,
                        )
                        .lowercase()
                        .toPostgresCompatibleName(),
            )
        }
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return if (!config.legacyRawTablesOnly) {
            name.toPostgresCompatibleName()
        } else {
            // In legacy mode, column names are not transformed
            name
        }
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val postgresType =
            when (fieldType.type) {
                // Simple types
                BooleanType -> PostgresDataType.BOOLEAN.typeName
                IntegerType -> PostgresDataType.BIGINT.typeName
                NumberType -> PostgresDataType.DECIMAL.typeName
                StringType -> PostgresDataType.VARCHAR.typeName

                // Temporal types
                DateType -> PostgresDataType.DATE.typeName
                TimeTypeWithTimezone -> PostgresDataType.TIME_WITH_TIMEZONE.typeName
                TimeTypeWithoutTimezone -> PostgresDataType.TIME.typeName
                TimestampTypeWithTimezone -> PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName
                TimestampTypeWithoutTimezone -> PostgresDataType.TIMESTAMP.typeName

                // Semistructured types
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is UnionType,
                is UnknownType -> PostgresDataType.JSONB.typeName
            }

        return ColumnType(postgresType, fieldType.nullable)
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
                                ColumnType(PostgresDataType.JSONB.typeName, false)
                        )
                ),
            importType = tableSchema.importType,
        )
    }
}
