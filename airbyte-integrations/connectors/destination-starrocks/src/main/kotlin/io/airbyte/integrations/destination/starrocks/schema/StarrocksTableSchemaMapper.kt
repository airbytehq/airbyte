/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.schema

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
import io.airbyte.integrations.destination.starrocks.spec.StarrocksConfiguration
import jakarta.inject.Singleton

/**
 * Maps Airbyte schema types to StarRocks SQL column types and table/column names. Mirrors
 * `ClickhouseTableSchemaMapper`, adapted to StarRocks types.
 *
 * StarRocks PRIMARY KEY columns must be NOT NULL, so [toFinalSchema] forces the primary-key columns
 * non-nullable for Dedupe streams (the cursor is irrelevant to StarRocks load-time dedup, which
 * sequences by load order via `__op`, so we do not touch it).
 */
@Singleton
class StarrocksTableSchemaMapper(
    private val config: StarrocksConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.resolvedDatabase).toStarrocksCompatibleName()
        val name = desc.name.toStarrocksCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String = name.toStarrocksCompatibleName()

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val starrocksType =
            when (fieldType.type) {
                BooleanType -> StarrocksSqlTypes.BOOLEAN
                IntegerType -> StarrocksSqlTypes.BIGINT
                NumberType -> StarrocksSqlTypes.DECIMAL
                DateType -> StarrocksSqlTypes.DATE
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> StarrocksSqlTypes.DATETIME
                StringType,
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone,
                is ArrayType,
                ArrayTypeWithoutSchema,
                is UnionType,
                is UnknownType -> StarrocksSqlTypes.STRING
                // Objects map to the StarRocks JSON type when `enable_json` is set, else a
                // JSON-encoded STRING (e.g. for Postgres jsonb columns).
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is ObjectType ->
                    if (config.enableJson) StarrocksSqlTypes.JSON else StarrocksSqlTypes.STRING
            }

        return ColumnType(starrocksType, fieldType.nullable)
    }

    override fun toFinalSchema(tableSchema: StreamTableSchema): StreamTableSchema {
        if (tableSchema.importType !is Dedupe) {
            return tableSchema
        }

        // StarRocks PRIMARY KEY columns must be NOT NULL.
        val pks = tableSchema.getPrimaryKey().flatten().toSet()

        val finalSchema =
            tableSchema.columnSchema.finalSchema
                .map { (name, type) -> name to type.copy(nullable = type.nullable && name !in pks) }
                .toMap()

        return tableSchema.copy(
            columnSchema = tableSchema.columnSchema.copy(finalSchema = finalSchema),
        )
    }
}

/** StarRocks SQL type literals used by the schema mapper and DDL. */
object StarrocksSqlTypes {
    const val BOOLEAN = "BOOLEAN"
    const val BIGINT = "BIGINT"
    const val DECIMAL = "DECIMAL(38, 9)"
    const val DATE = "DATE"
    const val DATETIME = "DATETIME"
    const val STRING = "STRING"
    const val JSON = "JSON"
}

/**
 * StarRocks identifiers may contain most characters when back-quoted, so we keep the original name.
 * A normalization hook is kept here (mirroring ClickHouse's `toClickHouseCompatibleName`) for
 * future reserved-character handling.
 */
internal fun String.toStarrocksCompatibleName(): String = this
