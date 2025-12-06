/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

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
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlTypes
import io.airbyte.integrations.destination.clickhouse.client.isValidVersionColumnType
import io.airbyte.integrations.destination.clickhouse.config.toClickHouseCompatibleName
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import jakarta.inject.Singleton

@Singleton
class ClickhouseTableSchemaMapper(
    private val config: ClickhouseConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.resolvedDatabase).toClickHouseCompatibleName()
        val name = desc.name.toClickHouseCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toClickHouseCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        // Map Airbyte field types to ClickHouse column types
        val clickhouseType =
            when (fieldType.type) {
                BooleanType -> ClickhouseSqlTypes.BOOL
                DateType -> ClickhouseSqlTypes.DATE32
                IntegerType -> ClickhouseSqlTypes.INT64
                NumberType -> ClickhouseSqlTypes.DECIMAL_WITH_PRECISION_AND_SCALE
                StringType -> ClickhouseSqlTypes.STRING
                TimeTypeWithTimezone -> ClickhouseSqlTypes.STRING
                TimeTypeWithoutTimezone -> ClickhouseSqlTypes.STRING
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> ClickhouseSqlTypes.DATETIME_WITH_PRECISION
                is ArrayType,
                ArrayTypeWithoutSchema,
                is UnionType,
                is UnknownType -> ClickhouseSqlTypes.STRING
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is ObjectType -> {
                    if (config.enableJson) {
                        ClickhouseSqlTypes.JSON
                    } else {
                        ClickhouseSqlTypes.STRING
                    }
                }
            }

        return ColumnType(clickhouseType, fieldType.nullable)
    }

    override fun toFinalSchema(tableSchema: StreamTableSchema): StreamTableSchema {
        if (tableSchema.importType !is Dedupe) {
            return tableSchema
        }

        // For dedupe mode we do extra logic to ensure certain columns are non-null:
        //     1) the primary key columns
        //     2) the version column used by the dedupe engine (in practice the cursor)
        val pks = tableSchema.getPrimaryKey().flatten()
        val cursor = tableSchema.getCursor().firstOrNull()

        val nonNullCols = buildSet {
            addAll(pks) // Primary keys are always non-nullable
            if (cursor != null) {
                // Check if the cursor column type is valid for ClickHouse ReplacingMergeTree
                val cursorColumnType = tableSchema.columnSchema.finalSchema[cursor]!!.type
                if (cursorColumnType.isValidVersionColumnType()) {
                    // Cursor column is valid, use it as version column
                    add(cursor) // Make cursor column non-nullable too
                }
            }
        }

        val finalSchema =
            tableSchema.columnSchema.finalSchema
                .map {
                    it.key to
                        it.value.copy(nullable = it.value.nullable && !nonNullCols.contains(it.key))
                }
                .toMap()

        return tableSchema.copy(
            columnSchema = tableSchema.columnSchema.copy(finalSchema = finalSchema)
        )
    }
}
