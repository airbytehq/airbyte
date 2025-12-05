/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
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
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.client.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse.client.DECIMAL_WITH_PRECISION_AND_SCALE
import io.airbyte.integrations.destination.clickhouse.client.VALID_VERSION_COLUMN_TYPES
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
                BooleanType -> "Bool"
                DateType -> "Date32"
                IntegerType -> "Int64"
                NumberType -> DECIMAL_WITH_PRECISION_AND_SCALE
                StringType -> "String"
                TimeTypeWithTimezone -> "String"
                TimeTypeWithoutTimezone -> "String"
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> DATETIME_WITH_PRECISION

                is ArrayType,
                ArrayTypeWithoutSchema,
                is UnionType,
                is UnknownType -> "String"

                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is ObjectType -> {
                    if (config.enableJson) {
                        "JSON"
                    } else {
                        "String"
                    }
                }
            }

        return ColumnType(clickhouseType, fieldType.nullable)
    }

    override fun toFinalSchema(
        inputToFinalColumnNames: Map<String, String>,
        inputSchema: Map<String, FieldType>,
        importType: ImportType,
    ): Map<String, ColumnType> {
        val directlyMappedSchema = super.toFinalSchema(inputToFinalColumnNames, inputSchema, importType)

        if (importType !is Dedupe) {
            return directlyMappedSchema
        }
        // For dedupe mode we do extra logic to ensure certain columns are non-null:
        //     1) the primary key columns
        //     2) the version column used by the dedupe engine
        val pks = importType.primaryKey.flatten()
        val cursor = importType.cursor

        // For ReplacingMergeTree, we need to make the cursor column non-nullable if it's used as
        // version column. We'll also determine here if we need to fall back to extracted_at.
        var useCursorAsVersionColumn = false
        val nonNullableColumns =
            mutableSetOf<String>().apply {
                addAll(pks) // Primary keys are always non-nullable
                if (cursor.isNotEmpty()) {
                    val cursorFieldName = cursor.first()
                    // Check if the cursor column type is valid for ClickHouse
                    // ReplacingMergeTree
                    val cursorColumnType = inputSchema[cursorFieldName]!!.type

                    if (isValidVersionColumnType(cursorColumnType)) {
                        // Cursor column is valid, use it as version column
                        add(cursorFieldName) // Make cursor column non-nullable too
                    }
                }
            }

        return
    }
}
