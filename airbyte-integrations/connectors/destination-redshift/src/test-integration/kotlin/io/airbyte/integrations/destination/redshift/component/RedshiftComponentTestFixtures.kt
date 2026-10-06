/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.integrations.destination.redshift.sql.RedshiftDataType

/**
 * Test fixtures for Redshift component tests.
 *
 * Redshift uses lowercase identifiers (via [toRedshiftCompatibleName]), so all column name mappings
 * are identity mappings -- the CDK default mappings work without transformation.
 */
object RedshiftComponentTestFixtures {

    /**
     * Expected table schema mapping all Airbyte types to their Redshift equivalents. Column names
     * match the CDK's [TableOperationsFixtures.ALL_TYPES_SCHEMA] field names after applying
     * [toRedshiftCompatibleName] (which is identity for these lowercase names).
     */
    val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "boolean" to ColumnType(RedshiftDataType.BOOLEAN.typeName, true),
                "integer" to ColumnType(RedshiftDataType.BIGINT.typeName, true),
                "number" to ColumnType(RedshiftDataType.NUMERIC.typeName, true),
                "date" to ColumnType(RedshiftDataType.DATE.typeName, true),
                "timestamp_tz" to ColumnType(RedshiftDataType.TIMESTAMPTZ.typeName, true),
                "timestamp_ntz" to ColumnType(RedshiftDataType.TIMESTAMP.typeName, true),
                "time_tz" to ColumnType(RedshiftDataType.TIMETZ.typeName, true),
                "time_ntz" to ColumnType(RedshiftDataType.TIME.typeName, true),
                "array" to ColumnType(RedshiftDataType.SUPER.typeName, true),
                "object" to ColumnType(RedshiftDataType.SUPER.typeName, true),
                // Union and unknown types are serialized to JSON strings by the coercer
                // and stored as VARCHAR, not SUPER.
                "union" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "legacy_union" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "unknown" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
            )
        )
}
