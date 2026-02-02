/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsFixtures
import io.airbyte.cdk.load.component.TableSchema

object PostgresComponentTestFixtures {
    // PostgreSQL uses lowercase column names by default (no transformation needed)
    val testMapping = TableOperationsFixtures.TEST_MAPPING
    val idAndTestMapping = TableOperationsFixtures.ID_AND_TEST_MAPPING
    val idTestWithCdcMapping = TableOperationsFixtures.ID_TEST_WITH_CDC_MAPPING

    val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType("varchar", true),
                "boolean" to ColumnType("boolean", true),
                "integer" to ColumnType("bigint", true),
                "number" to ColumnType("decimal", true),
                "date" to ColumnType("date", true),
                "timestamp_tz" to ColumnType("timestamp with time zone", true),
                "timestamp_ntz" to ColumnType("timestamp", true),
                "time_tz" to ColumnType("time with time zone", true),
                "time_ntz" to ColumnType("time", true),
                "array" to ColumnType("jsonb", true),
                "object" to ColumnType("jsonb", true),
                "unknown" to ColumnType("jsonb", true),
            )
        )

    val allTypesColumnNameMapping = TableOperationsFixtures.ALL_TYPES_MAPPING
}
