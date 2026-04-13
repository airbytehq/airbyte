/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.redshift2.sql.RedshiftDataType
import jakarta.inject.Singleton

/**
 * Manages column names and ordering for Redshift tables. Defines the Airbyte meta columns and their
 * types using Redshift-specific SQL types
 */
@Singleton
class RedshiftColumnManager {

    /**
     * Get the list of column names for a table in the order they should appear in the CSV file and
     * COPY statement.
     *
     * @param columnSchema The schema containing column information
     * @return List of column names in the correct order: meta columns first, then user columns
     */
    fun getTableColumnNames(columnSchema: ColumnSchema): List<String> {
        return buildList {
            addAll(getMetaColumnNames())
            addAll(columnSchema.finalSchema.keys)
        }
    }

    /**
     * Get the list of Airbyte meta column names.
     *
     * @return Set of meta column names in insertion order
     */
    fun getMetaColumnNames(): Set<String> = Constants.schemaModeMetaColNames

    /**
     * Get the Airbyte meta columns as a map of column name to [ColumnType]. This provides both the
     * column names and their types for table creation.
     *
     * @return Ordered map of meta column names to their types
     */
    fun getMetaColumns(): LinkedHashMap<String, ColumnType> = Constants.schemaModeMetaColumns

    fun getGenerationIdColumnName(): String = Meta.COLUMN_NAME_AB_GENERATION_ID

    object Constants {
        val schemaModeMetaColumns =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to
                    ColumnType(RedshiftDataType.VARCHAR_36.typeName, false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    ColumnType(RedshiftDataType.TIMESTAMPTZ.typeName, false),
                Meta.COLUMN_NAME_AB_META to ColumnType(RedshiftDataType.SUPER.typeName, false),
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    ColumnType(RedshiftDataType.BIGINT.typeName, false),
            )

        val schemaModeMetaColNames: Set<String> = schemaModeMetaColumns.keys
    }
}
