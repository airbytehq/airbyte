/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.integrations.destination.redshift2.sql.RedshiftDataType
import jakarta.inject.Singleton

/** Manages column names and ordering for Redshift tables */
@Singleton
class RedshiftColumnManager {

    fun getTableColumnNames(columnSchema: ColumnSchema): List<String> {
        return buildList {
            addAll(getMetaColumnNames())
            addAll(columnSchema.finalSchema.keys)
        }
    }

    fun getMetaColumnNames(): Set<String> = Constants.schemaModeMetaColNames

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
