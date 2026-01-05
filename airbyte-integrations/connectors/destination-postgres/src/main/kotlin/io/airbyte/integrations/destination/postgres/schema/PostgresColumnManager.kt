/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.schema

import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
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
     * @param columnSchema The schema containing column information
     * @return List of column names in the correct order
     */
    fun getTableColumns(columnSchema: ColumnSchema): List<String> {
        return buildList {
            addAll(getMetaColumns())
            if (!config.legacyRawTablesOnly) {
                addAll(columnSchema.finalSchema.keys)
            }
        }
    }

    /**
     * Get the list of Airbyte meta column names. In raw mode, includes _airbyte_loaded_at and
     * _airbyte_data as additional columns. In schema mode, only includes the standard meta columns.
     *
     * @return List of meta column names
     */
    fun getMetaColumns(): List<String> =
        if (config.legacyRawTablesOnly) {
            Constants.standardMetaCols + Constants.rawOnlyCols
        } else {
            Constants.standardMetaCols
        }

    object Constants {
        /** Standard meta columns present in both raw and schema modes */
        val standardMetaCols =
            listOf(
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
            )

        /** Additional columns only present in raw/legacy mode */
        val rawOnlyCols =
            listOf(
                Meta.COLUMN_NAME_AB_LOADED_AT,
                Meta.COLUMN_NAME_DATA,
            )
    }
}
