/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import jakarta.inject.Singleton

/** ANSI SQL reserved keywords that common query engines reject as unquoted column names. */
private val RESERVED_COLUMN_NAMES =
    setOf(
        "constraint",
        "current_date",
        "current_time",
        "current_timestamp",
        "current_user",
        "localtime",
        "localtimestamp",
    )

/**
 * Maps input schema names to the names actually written to Iceberg.
 *
 * Table names are delegated to [TableIdGenerator]. Column names are passed through unchanged unless
 * [S3DataLakeConfiguration.normalizeColumnNames] is enabled, in which case [normalizeColumnName] is
 * applied. Collisions are resolved by the CDK's [io.airbyte.cdk.load.schema.ColumnNameResolver].
 */
@Singleton
class S3DataLakeTableSchemaMapper(
    private val config: S3DataLakeConfiguration,
    private val tableIdGenerator: TableIdGenerator,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val tableId = tableIdGenerator.toTableIdentifier(desc)
        return TableName(namespace = tableId.namespace().toString(), name = tableId.name())
    }

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String =
        if (config.normalizeColumnNames) normalizeColumnName(name) else name

    override fun toColumnType(fieldType: FieldType): ColumnType =
        ColumnType(fieldType.type.toString(), fieldType.nullable)

    companion object {
        /**
         * Normalizes a column name: lowercases, replaces non-alphanumeric characters with
         * underscores (via [Transformations.toAlphanumericAndUnderscore]), and prefixes SQL
         * reserved keywords with `_`. Rejects empty names.
         */
        fun normalizeColumnName(name: String): String {
            if (name.isEmpty()) {
                throw ConfigErrorException("Empty string is not a valid column name")
            }
            val normalized = Transformations.toAlphanumericAndUnderscore(name).lowercase()
            return if (normalized in RESERVED_COLUMN_NAMES) "_$normalized" else normalized
        }
    }
}
