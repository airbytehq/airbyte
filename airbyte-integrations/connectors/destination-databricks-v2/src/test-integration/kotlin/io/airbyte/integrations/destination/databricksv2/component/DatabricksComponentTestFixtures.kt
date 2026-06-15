/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.BOOLEAN
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.DATE
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.DECIMAL
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.LONG
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.STRING
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.TIMESTAMP
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper.Companion.TIMESTAMP_NTZ

/**
 * Test fixtures for Databricks component tests.
 *
 * Databricks preserves column name casing (unlike Redshift which lowercases), so column names match
 * the CDK fixture field names exactly.
 */
object DatabricksComponentTestFixtures {

    /**
     * Expected table schema mapping all Airbyte types to their Databricks equivalents. Column names
     * match the CDK's [TableOperationsFixtures.ALL_TYPES_SCHEMA] field names.
     */
    val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType(STRING, true),
                "boolean" to ColumnType(BOOLEAN, true),
                "integer" to ColumnType(LONG, true),
                "number" to ColumnType(DECIMAL, true),
                "date" to ColumnType(DATE, true),
                "timestamp_tz" to ColumnType(TIMESTAMP, true),
                "timestamp_ntz" to ColumnType(TIMESTAMP_NTZ, true),
                // Time types have no native Databricks equivalent; stored as STRING.
                "time_tz" to ColumnType(STRING, true),
                "time_ntz" to ColumnType(STRING, true),
                // Semi-structured and special types all stored as STRING in Databricks.
                "array" to ColumnType(STRING, true),
                "object" to ColumnType(STRING, true),
                "union" to ColumnType(STRING, true),
                "legacy_union" to ColumnType(STRING, true),
                "unknown" to ColumnType(STRING, true),
            ),
        )
}
