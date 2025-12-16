/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_EXTRACTED_AT
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_GENERATION_ID
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_META
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_RAW_ID
import jakarta.inject.Singleton

/**
 * Manages column names and ordering for Snowflake tables based on whether legacy raw tables mode is
 * enabled.
 *
 * TODO: We should add meta column munging and raw table support to the CDK, so this extra layer of
 * management shouldn't be necessary.
 */
@Singleton
class SnowflakeColumnManager(
    private val config: SnowflakeConfiguration,
) {
    /**
     * Get the list of column names for a table in the order they should appear in the CSV file and
     * COPY INTO statement.
     *
     * @param columnSchema The schema containing column information (ignored in raw mode)
     * @return List of column names in the correct order
     */
    fun getTableColumns(columnSchema: ColumnSchema): List<String> {
        return buildList {
            addAll(getMetaColumns())
            addAll(columnSchema.finalSchema.keys)
        }
    }

    /**
     * Get the list of Airbyte meta column names. In schema mode, these are uppercase. In raw mode,
     * they are lowercase and included loaded_at
     *
     * @return List of meta column names
     */
    fun getMetaColumns() =
        if (config.legacyRawTablesOnly) {
            Constants.rawModeMetaCols
        } else {
            Constants.schemaModeMetaCols
        }

    object Constants {
        val rawModeMetaCols =
            setOf(
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
                Meta.COLUMN_NAME_AB_LOADED_AT,
            )

        val schemaModeMetaCols =
            setOf(
                SNOWFLAKE_AB_RAW_ID,
                SNOWFLAKE_AB_EXTRACTED_AT,
                SNOWFLAKE_AB_META,
                SNOWFLAKE_AB_GENERATION_ID
            )
    }
}
