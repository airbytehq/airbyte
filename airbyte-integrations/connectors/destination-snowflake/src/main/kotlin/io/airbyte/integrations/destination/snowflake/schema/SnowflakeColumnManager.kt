/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_EXTRACTED_AT
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_GENERATION_ID
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_META
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_RAW_ID
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDataType
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
     * Warning: MUST match the order defined in SnowflakeRecordFormatter
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
     * Get the list of Airbyte meta column names. In schema mode, these are uppercase. In raw mode,
     * they are lowercase and included loaded_at
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
     * @param columnSchema The user column schema (used to check for CDC columns)
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
        return if (config.legacyRawTablesOnly) {
            Meta.COLUMN_NAME_AB_GENERATION_ID
        } else {
            SNOWFLAKE_AB_GENERATION_ID
        }
    }

    object Constants {
        val rawModeMetaColumns =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to ColumnType(SnowflakeDataType.VARCHAR.typeName, false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    ColumnType(
                        SnowflakeDataType.TIMESTAMP_TZ.typeName,
                        false,
                    ),
                Meta.COLUMN_NAME_AB_META to ColumnType(SnowflakeDataType.VARIANT.typeName, false),
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    ColumnType(
                        SnowflakeDataType.NUMBER.typeName,
                        true,
                    ),
                Meta.COLUMN_NAME_AB_LOADED_AT to
                    ColumnType(
                        SnowflakeDataType.TIMESTAMP_TZ.typeName,
                        true,
                    ),
            )

        val schemaModeMetaColumns =
            linkedMapOf(
                SNOWFLAKE_AB_RAW_ID to ColumnType(SnowflakeDataType.VARCHAR.typeName, false),
                SNOWFLAKE_AB_EXTRACTED_AT to
                    ColumnType(SnowflakeDataType.TIMESTAMP_TZ.typeName, false),
                SNOWFLAKE_AB_META to ColumnType(SnowflakeDataType.VARIANT.typeName, false),
                SNOWFLAKE_AB_GENERATION_ID to ColumnType(SnowflakeDataType.NUMBER.typeName, true),
            )

        val rawModeMetaColNames: Set<String> = rawModeMetaColumns.keys

        val schemaModeMetaColNames: Set<String> = schemaModeMetaColumns.keys
    }
}
