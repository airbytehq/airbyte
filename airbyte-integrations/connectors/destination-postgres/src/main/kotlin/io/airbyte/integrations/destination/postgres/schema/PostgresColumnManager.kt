/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.PostgresDataType
import jakarta.inject.Singleton

/**
 * Manages column names and ordering for Postgres tables based on whether legacy raw tables mode is
 * enabled.
 */
@Singleton
class PostgresColumnManager(
    private val config: PostgresConfiguration,
) {
    /**
     * Get the list of column names for a table in the order they should appear in the CSV file and
     * COPY statement.
     *
     * @param columnSchema The schema containing column information (ignored in raw mode)
     * @return List of column names in the correct order
     */
    fun getTableColumnNames(columnSchema: ColumnSchema): List<String> {
        return buildList {
            addAll(getMetaColumnNames())
            addAll(columnSchema.finalSchema.keys)
        }
    }

    /**
     * Get the list of Airbyte meta column names. In schema mode, these are the standard meta
     * columns. In raw mode, they include loaded_at and data columns.
     *
     * @return Set of meta column names
     */
    fun getMetaColumnNames(): Set<String> =
        if (config.legacyRawTablesOnly) {
            Constants.rawModeMetaColNames
        } else {
            Constants.schemaModeMetaColNames
        }

    /**
     * Get the Airbyte meta columns as a map of column name to ColumnType. This provides both the
     * column names and their types for table creation.
     *
     * @return Map of meta column names to their types
     */
    fun getMetaColumns(): LinkedHashMap<String, ColumnType> {
        return if (config.legacyRawTablesOnly) {
            Constants.rawModeMetaColumns
        } else {
            Constants.schemaModeMetaColumns
        }
    }

    fun getGenerationIdColumnName(): String {
        return Meta.COLUMN_NAME_AB_GENERATION_ID
    }

    object Constants {
        val rawModeMetaColumns =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to ColumnType(PostgresDataType.VARCHAR.typeName, false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    ColumnType(
                        PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                        false,
                    ),
                Meta.COLUMN_NAME_AB_META to ColumnType(PostgresDataType.JSONB.typeName, false),
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    ColumnType(
                        PostgresDataType.BIGINT.typeName,
                        false,
                    ),
                Meta.COLUMN_NAME_AB_LOADED_AT to
                    ColumnType(
                        PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                        true,
                    ),
                Meta.COLUMN_NAME_DATA to ColumnType(PostgresDataType.JSONB.typeName, false),
            )

        val schemaModeMetaColumns =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to ColumnType(PostgresDataType.VARCHAR.typeName, false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    ColumnType(PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName, false),
                Meta.COLUMN_NAME_AB_META to ColumnType(PostgresDataType.JSONB.typeName, false),
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    ColumnType(PostgresDataType.BIGINT.typeName, false),
            )

        val rawModeMetaColNames: Set<String> = rawModeMetaColumns.keys

        val schemaModeMetaColNames: Set<String> = schemaModeMetaColumns.keys
    }
}
