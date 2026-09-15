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

/**
 * ANSI reserved keywords that Snowflake rejects as column names even when quoted. Same list as
 * destination-snowflake's `SnowflakeNamingUtils`, lowercased. See:
 * https://docs.snowflake.com/en/sql-reference/reserved-keywords
 */
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
 * Table identifiers are owned by the catalog-specific [TableIdGenerator] (the Iceberg toolkit
 * resolves tables through it), so this mapper delegates to it rather than duplicating the Glue /
 * Nessie / REST / Polaris naming rules. That keeps the CDK's view of the final table name in sync
 * with the identifier the toolkit uses.
 *
 * Column names are passed through unchanged unless [S3DataLakeConfiguration.normalizeColumnNames]
 * is enabled, in which case they go through [normalizeColumnName]. Names that normalize to the same
 * value (`Foo.Bar` and `foo_bar`, or `ID` and `id`) are made unique by the CDK's
 * [io.airbyte.cdk.load.schema.ColumnNameResolver] using the default [colsConflict] rule.
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
         * The normalization applied to column names when `normalize_column_names` is enabled. It
         * follows destination-snowflake's `String.toSnowflakeCompatibleName()`, except that names
         * are lowercased rather than uppercased (Snowflake requires lowercase identifiers when
         * reading Iceberg tables through Glue) and special characters are replaced rather than
         * quoted:
         * 1. An empty name is rejected.
         * 2. [Transformations.toAlphanumericAndUnderscore] strips accents and replaces whitespace
         * and any character outside `[A-Za-z0-9_]` with `_`, then the result is lowercased
         * (`userId` becomes `userid`, `Foo.Bar` becomes `foo_bar`, `my-column` becomes `my_column`,
         * `spécial` becomes `special`; leading digits are kept). This also neutralizes the `${` and
         * `"` sequences Snowflake special-cases. The output is ASCII, so [String.lowercase] is
         * locale-independent.
         * 3. Names that are Snowflake reserved keywords are prefixed with `_` (`CURRENT_DATE`
         * becomes `_current_date`).
         *
         * Also used by
         * [io.airbyte.integrations.destination.s3_data_lake.write.S3DataLakeStreamLoader] to detect
         * columns of an existing table that enabling the option would rename.
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
