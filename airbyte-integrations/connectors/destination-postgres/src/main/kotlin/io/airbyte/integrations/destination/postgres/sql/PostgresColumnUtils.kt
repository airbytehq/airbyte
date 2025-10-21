/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.data.AirbyteType
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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton

@Singleton
class PostgresColumnUtils(
    private val postgresConfiguration: PostgresConfiguration
) {
    companion object {
        internal const val NOT_NULL = "NOT NULL"

        /**
         * Default columns that are always present in both raw and typed tables.
         */
        internal val DEFAULT_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_RAW_ID,
                    columnTypeName = "${PostgresDataType.VARCHAR.typeName} $NOT_NULL",
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_EXTRACTED_AT,
                    columnTypeName = "${PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName} $NOT_NULL",
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_META,
                    columnTypeName = "${PostgresDataType.JSONB.typeName} $NOT_NULL",
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_GENERATION_ID,
                    columnTypeName = PostgresDataType.BIGINT.typeName,
                    nullable = false
                ),
            )

        /**
         * Additional columns that are only present in raw (legacy) tables.
         */
        internal val RAW_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_LOADED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = true
                ),
                Column(
                    columnName = COLUMN_NAME_DATA,
                    columnTypeName = "${PostgresDataType.JSONB.typeName} $NOT_NULL",
                    nullable = false
                )
            )
    }

    /**
     * Returns the complete set of default columns based on the table mode.
     * - Raw table mode: includes _airbyte_data column for storing raw JSON
     * - Typed table mode: excludes _airbyte_data, schema columns stored separately
     */
    internal fun defaultColumns(): List<Column> =
        if (postgresConfiguration.legacyRawTablesOnly == true) {
            DEFAULT_COLUMNS + RAW_COLUMNS
        } else {
            DEFAULT_COLUMNS
        }

    /**
     * Returns formatted default columns for SQL generation.
     */
    fun formattedDefaultColumns(): List<Column> = defaultColumns()

    /**
     * Returns the list of columns and their types for table creation.
     * - Raw table mode: Only returns system columns (including _airbyte_data), user columns are ignored
     * - Typed table mode: Returns system columns + mapped user columns
     */
    fun columnsAndTypes(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping
    ): List<Column> =
        if (postgresConfiguration.legacyRawTablesOnly == true) {
            // RAW TABLE MODE: Only return default columns (no user columns)
            formattedDefaultColumns()
        } else {
            // TYPED TABLE MODE: Return default columns + user columns
            formattedDefaultColumns() +
                columns.map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName] ?: fieldName
                    val typeName = toDialectType(type.type)
                    Column(
                        columnName = columnName,
                        columnTypeName = typeName,
                        nullable = type.nullable
                    )
                }
        }

    /**
     * Formats a column name for SQL statements.
     * Returns the column name with proper quoting.
     */
    fun formatColumnName(columnName: String, quote: Boolean = true): String {
        return if (quote) "\"$columnName\"" else columnName
    }

    /**
     * Converts Airbyte types to PostgreSQL dialect types.
     */
    private fun toDialectType(type: AirbyteType): String =
        when (type) {
            BooleanType -> PostgresDataType.BOOLEAN.typeName
            DateType -> PostgresDataType.DATE.typeName
            IntegerType -> PostgresDataType.BIGINT.typeName
            NumberType -> PostgresDataType.DECIMAL.typeName
            StringType -> PostgresDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> PostgresDataType.TIME_WITH_TIMEZONE.typeName
            TimeTypeWithoutTimezone -> PostgresDataType.TIME.typeName
            TimestampTypeWithTimezone -> PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName
            TimestampTypeWithoutTimezone -> PostgresDataType.TIMESTAMP.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnknownType,
            is UnionType -> PostgresDataType.JSONB.typeName
        }
}
