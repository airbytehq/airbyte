/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component.config

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsFixtures
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping

object SnowflakeComponentTestFixtures {
    private fun ColumnNameMapping.transformColumns() =
        ColumnNameMapping(mapValues { (_, v) -> v.uppercase() })

    val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it.uppercase() }

    val testMapping = TableOperationsFixtures.TEST_MAPPING.transformColumns()
    val idAndTestMapping = TableOperationsFixtures.ID_AND_TEST_MAPPING.transformColumns()
    val idTestWithCdcMapping = TableOperationsFixtures.ID_TEST_WITH_CDC_MAPPING.transformColumns()

    val allTypesTableSchema =
        TableSchema(
            mapOf(
                "STRING" to ColumnType("VARCHAR", true),
                "BOOLEAN" to ColumnType("BOOLEAN", true),
                // NUMBER == NUMBER(38, 0)
                "INTEGER" to ColumnType("NUMBER", true),
                // we use FLOAT instead of NUMBER(38, 9) for historical reasons
                "NUMBER" to ColumnType("FLOAT", true),
                "DATE" to ColumnType("DATE", true),
                "TIMESTAMP_TZ" to ColumnType("TIMESTAMP_TZ", true),
                "TIMESTAMP_NTZ" to ColumnType("TIMESTAMP_NTZ", true),
                "TIME_TZ" to ColumnType("VARCHAR", true),
                "TIME_NTZ" to ColumnType("TIME", true),
                "ARRAY" to ColumnType("ARRAY", true),
                "OBJECT" to ColumnType("OBJECT", true),
                "UNION" to ColumnType("VARIANT", true),
                "LEGACY_UNION" to ColumnType("VARIANT", true),
                "UNKNOWN" to ColumnType("VARIANT", true),
            )
        )
    val allTypesColumnNameMapping =
        ColumnNameMapping(TableOperationsFixtures.ALL_TYPES_MAPPING.transformColumns())
}
