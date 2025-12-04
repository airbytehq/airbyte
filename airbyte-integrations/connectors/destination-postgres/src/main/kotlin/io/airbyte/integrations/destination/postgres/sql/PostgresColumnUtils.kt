/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
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
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton
import kotlin.collections.plus

@Singleton
class PostgresColumnUtils(private val postgresConfiguration: PostgresConfiguration) {
    companion object {
        private const val CURSOR_INDEX_PREFIX = "idx_cursor_"
        private const val PRIMARY_KEY_INDEX_PREFIX = "idx_pk_"
        private const val EXTRACTED_AT_INDEX_PREFIX = "idx_extracted_at_"
        // Default columns that are always present in both raw and typed tables.
        private val DEFAULT_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_RAW_ID,
                    columnTypeName = PostgresDataType.VARCHAR.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_EXTRACTED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_META,
                    columnTypeName = PostgresDataType.JSONB.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_GENERATION_ID,
                    columnTypeName = PostgresDataType.BIGINT.typeName,
                    nullable = false
                ),
            )

        // Columns that are only present in raw (legacy) tables.
        private val RAW_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_LOADED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = true
                ),
                Column(
                    columnName = COLUMN_NAME_DATA,
                    columnTypeName = "${PostgresDataType.JSONB.typeName}",
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
     * Returns the list of columns and their types
     * - Raw table mode: Only returns system columns (including _airbyte_data), user columns are
     * ignored
     * - Typed table mode: Returns system columns + mapped user columns
     */
    internal fun getTargetColumns(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): List<Column> =
        if (postgresConfiguration.legacyRawTablesOnly == true) {
            // RAW TABLE MODE: Only return default columns (no user columns)
            defaultColumns()
        } else {
            // TYPED TABLE MODE: Return default columns + user columns
            val columns = getColumns(stream)
            defaultColumns() +
                columns.map { (columnName, type) ->
                    val targetColumnName = getTargetColumnName(columnName, columnNameMapping)
                    val typeName = toDialectType(type.type)
                    Column(
                        columnName = targetColumnName,
                        columnTypeName = typeName,
                        nullable = type.nullable
                    )
                }
        }

    private fun getColumns(stream: DestinationStream): Map<String, FieldType> {
        return when (val schema = stream.schema) {
            is ObjectType -> schema.asColumns()
            is ObjectTypeWithEmptySchema -> emptyMap()
            else -> emptyMap()
        }
    }

    internal fun getTargetColumnName(
        streamColumnName: String,
        columnNameMapping: ColumnNameMapping
    ): String = columnNameMapping[streamColumnName] ?: streamColumnName

    // Converts Airbyte types to PostgreSQL column types.
    @VisibleForTesting
    internal fun toDialectType(type: AirbyteType): String =
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

    internal fun getPrimaryKeysColumnNames(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return when (stream.importType) {
            is Dedupe -> getPrimaryKeysColumnNames(stream.importType as Dedupe, columnNameMapping)
            else -> listOf()
        }
    }

    internal fun getPrimaryKeysColumnNames(
        importType: Dedupe,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return importType.primaryKey
            .map { fieldPath ->
                val primaryKeyColumnName = fieldPath.first() // only at the root level for Postgres
                getTargetColumnName(primaryKeyColumnName, columnNameMapping)
            }
            .toList()
    }

    internal fun getCursorColumnName(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): String? {
        return when (stream.importType) {
            is Dedupe ->
                getCursorColumnName((stream.importType as Dedupe).cursor, columnNameMapping)
            else -> null
        }
    }

    internal fun getCursorColumnName(
        cursor: List<String>,
        columnNameMapping: ColumnNameMapping
    ): String? {
        return cursor.firstOrNull()?.let { columnName ->
            getTargetColumnName(columnName, columnNameMapping)
        }
    }

    internal fun getCursorIndexName(tableName: TableName): String =
        CURSOR_INDEX_PREFIX + tableName.name

    internal fun getPrimaryKeyIndexName(tableName: TableName): String =
        PRIMARY_KEY_INDEX_PREFIX + tableName.name

    internal fun getExtractedAtIndexName(tableName: TableName): String =
        EXTRACTED_AT_INDEX_PREFIX + tableName.name
}

data class Column(val columnName: String, val columnTypeName: String, val nullable: Boolean = true)
