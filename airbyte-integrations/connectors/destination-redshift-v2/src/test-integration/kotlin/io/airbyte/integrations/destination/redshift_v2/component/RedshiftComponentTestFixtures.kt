/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsFixtures
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift_v2.schema.toRedshiftCompatibleName

object RedshiftComponentTestFixtures {
    private fun ColumnNameMapping.transformColumns() =
        ColumnNameMapping(mapValues { (_, v) -> v.toRedshiftCompatibleName() })

    val testMapping = TableOperationsFixtures.TEST_MAPPING.transformColumns()
    val idAndTestMapping = TableOperationsFixtures.ID_AND_TEST_MAPPING.transformColumns()
    val idTestWithCdcMapping = TableOperationsFixtures.ID_TEST_WITH_CDC_MAPPING.transformColumns()

    val allTypesTableSchema =
        TableSchema(
            mapOf(
                // Type sizes are stripped for schema comparison (VARCHAR(65535) -> VARCHAR)
                "string" to ColumnType("VARCHAR", true),
                "boolean" to ColumnType("BOOLEAN", true),
                "integer" to ColumnType("BIGINT", true),
                // Redshift uses DOUBLE PRECISION which normalizes to DOUBLE
                "number" to ColumnType("DOUBLE", true),
                "date" to ColumnType("DATE", true),
                "timestamp_tz" to ColumnType("TIMESTAMPTZ", true),
                "timestamp_ntz" to ColumnType("TIMESTAMP", true),
                // Redshift doesn't have TIMETZ - we store as VARCHAR
                "time_tz" to ColumnType("VARCHAR", true),
                "time_ntz" to ColumnType("TIME", true),
                "array" to ColumnType("SUPER", true),
                "object" to ColumnType("SUPER", true),
                // Note: union and legacy_union are filtered out by schema normalization
                // (UnionType collapses to its underlying types)
                "unknown" to ColumnType("SUPER", true),
            )
        )
    val allTypesColumnNameMapping =
        ColumnNameMapping(TableOperationsFixtures.ALL_TYPES_MAPPING.transformColumns())
}
